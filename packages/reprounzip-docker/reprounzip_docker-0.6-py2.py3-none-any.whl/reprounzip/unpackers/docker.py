# Copyright (C) 2014-2015 New York University
# This file is part of ReproZip which is released under the Revised BSD License
# See file LICENSE for full license details.

"""Docker plugin for reprounzip.

This files contains the 'docker' unpacker, which builds a Dockerfile from a
reprozip pack. You can then build a container and run it with Docker.

See http://www.docker.io/
"""

from __future__ import unicode_literals

import argparse
from itertools import chain
import json
import logging
import os
import pickle
import re
from rpaths import Path, PosixPath
import subprocess
import sys
import tarfile

from reprounzip.common import Package, load_config, record_usage
from reprounzip import signals
from reprounzip.unpackers.common import COMPAT_OK, COMPAT_MAYBE, \
    CantFindInstaller, composite_action, target_must_exist, make_unique_name, \
    shell_escape, select_installer, busybox_url, join_root, \
    FileUploader, FileDownloader, get_runs, interruptible_call
from reprounzip.unpackers.common.x11 import X11Handler, LocalForwarder
from reprounzip.utils import unicode_, iteritems, download_file


def select_image(runs):
    """Selects a base image for the experiment, with the correct distribution.
    """
    distribution, version = runs[0]['distribution']
    distribution = distribution.lower()
    architecture = runs[0]['architecture']

    record_usage(docker_select_box='%s;%s;%s' % (distribution, version,
                                                 architecture))

    if architecture == 'i686':
        logging.info("wanted architecture was i686, but we'll use x86_64 with "
                     "Docker")
    elif architecture != 'x86_64':
        logging.error("Error: unsupported architecture %s", architecture)
        sys.exit(1)

    # Ubuntu
    if distribution == 'ubuntu':
        if version == '12.04':
            return 'ubuntu', 'ubuntu:12.04'
        elif version == '14.04':
            return 'ubuntu', 'ubuntu:14.04'
        else:
            if version != '14.10':
                logging.warning("using Ubuntu 14.10 'Utopic' instead of '%s'",
                                version)
            return 'ubuntu', 'ubuntu:14.10'

    # Debian
    else:
        if distribution != 'debian':
            logging.warning("unsupported distribution %s, using Debian",
                            distribution)
            version = '7'

        if version == '6' or version.startswith('squeeze'):
            return 'debian', 'debian:squeeze'
        elif version == '8' or version.startswith('jessie'):
            return 'debian', 'debian:jessie'
        else:
            if (version != '7' and not version.startswith('7.') and
                    not version.startswith('wheezy')):
                logging.warning("using Debian 7 'Wheezy' instead of '%s'",
                                version)
            return 'debian', 'debian:wheezy'


def write_dict(filename, dct):
    to_write = {'unpacker': 'docker'}
    to_write.update(dct)
    with filename.open('wb') as fp:
        pickle.dump(to_write, fp, 2)


def read_dict(filename):
    with filename.open('rb') as fp:
        dct = pickle.load(fp)
    if dct['unpacker'] != 'docker':
        raise ValueError("Wrong unpacker used: %s != docker" % dct['unpacker'])
    return dct


def docker_setup_create(args):
    """Sets up the experiment to be run in a Docker-built container.
    """
    pack = Path(args.pack[0])
    target = Path(args.target[0])
    if target.exists():
        logging.critical("Target directory exists")
        sys.exit(1)

    signals.pre_setup(target=target, pack=pack)

    # Unpacks configuration file
    tar = tarfile.open(str(pack), 'r:*')
    member = tar.getmember('METADATA/config.yml')
    member.name = 'config.yml'
    tar.extract(member, str(target))
    tar.close()

    # Loads config
    runs, packages, other_files = load_config(target / 'config.yml', True)

    if args.base_image:
        record_usage(docker_explicit_base=True)
        base_image = args.base_image[0]
        if args.distribution:
            target_distribution = args.distribution[0]
        else:
            target_distribution = None
    else:
        target_distribution, base_image = select_image(runs)
    logging.info("Using base image %s", base_image)
    logging.debug("Distribution: %s", target_distribution or "unknown")

    target.mkdir(parents=True)
    pack.copyfile(target / 'experiment.rpz')

    # Writes Dockerfile
    logging.info("Writing %s...", target / 'Dockerfile')
    with (target / 'Dockerfile').open('w',
                                      encoding='utf-8', newline='\n') as fp:
        fp.write('FROM %s\n\n' % base_image)

        # Installs busybox
        download_file(busybox_url(runs[0]['architecture']),
                      target / 'busybox')
        fp.write('COPY busybox /bin/busybox\n')

        fp.write('COPY experiment.rpz /reprozip_experiment.rpz\n\n')
        fp.write('RUN \\\n'
                 '    chmod +x /bin/busybox && \\\n')

        if args.install_pkgs:
            # Install every package through package manager
            missing_packages = []
        else:
            # Only install packages that were not packed
            missing_packages = [pkg for pkg in packages if pkg.packfiles]
            packages = [pkg for pkg in packages if not pkg.packfiles]
        # FIXME : Right now, we need 'sudo' to be available (and it's not
        # necessarily in the base image)
        if packages:
            record_usage(docker_install_pkgs=True)
        else:
            record_usage(docker_install_pkgs="sudo")
        packages += [Package('sudo', None, packfiles=False)]
        if packages:
            try:
                installer = select_installer(pack, runs, target_distribution)
            except CantFindInstaller as e:
                logging.error("Need to install %d packages but couldn't "
                              "select a package installer: %s",
                              len(packages), e)
                sys.exit(1)
            # Updates package sources
            fp.write('    %s && \\\n' % installer.update_script())
            # Installs necessary packages
            fp.write('    %s && \\\n' % installer.install_script(packages))
        logging.info("Dockerfile will install the %d software packages that "
                     "were not packed", len(packages))

        # Untar
        paths = set()
        pathlist = []
        dataroot = PosixPath('DATA')
        # Adds intermediate directories, and checks for existence in the tar
        tar = tarfile.open(str(pack), 'r:*')
        missing_files = chain.from_iterable(pkg.files
                                            for pkg in missing_packages)
        for f in chain(other_files, missing_files):
            path = PosixPath('/')
            for c in f.path.components[1:]:
                path = path / c
                if path in paths:
                    continue
                paths.add(path)
                datapath = join_root(dataroot, path)
                try:
                    tar.getmember(str(datapath))
                except KeyError:
                    logging.info("Missing file %s", datapath)
                else:
                    pathlist.append(unicode_(datapath))
        tar.close()
        # FIXME : for some reason we need reversed() here, I'm not sure why.
        # Need to read more of tar's docs.
        # TAR bug: --no-overwrite-dir removes --keep-old-files
        fp.write('    cd / && tar zpxf /reprozip_experiment.rpz '
                 '--numeric-owner --strip=1 %s\n' %
                 ' '.join(shell_escape(p) for p in reversed(pathlist)))

    # Meta-data for reprounzip
    write_dict(target / '.reprounzip', {})

    signals.post_setup(target=target)


@target_must_exist
def docker_setup_build(args):
    """Builds the container from the Dockerfile
    """
    target = Path(args.target[0])
    unpacked_info = read_dict(target / '.reprounzip')
    if 'initial_image' in unpacked_info:
        logging.critical("Image already built")
        sys.exit(1)

    image = make_unique_name(b'reprounzip_image_')

    logging.info("Calling 'docker build'...")
    try:
        retcode = subprocess.call(['docker', 'build', '-t', image, '.'],
                                  cwd=target.path)
    except OSError:
        logging.critical("docker executable not found")
        sys.exit(1)
    else:
        if retcode != 0:
            logging.critical("docker build failed with code %d", retcode)
            sys.exit(1)
    logging.info("Initial image created: %s", image.decode('ascii'))

    unpacked_info['initial_image'] = image
    unpacked_info['current_image'] = image
    write_dict(target / '.reprounzip', unpacked_info)


_addr_re = re.compile(br'inet ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')


def get_iface_addr(iface):
    """Gets the local IP address of a named network interface.

    Returns an IPv4 address as a unicode object, in digits-and-dots format.

    >>> get_iface_addr('lo')
    '127.0.0.1'
    """
    p = subprocess.Popen(['/bin/ip', 'addr', 'show', iface],
                         stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    for line in stdout.splitlines():
        m = _addr_re.search(line)
        if m is not None:
            return m.group(1).decode('ascii')


@target_must_exist
def docker_run(args):
    """Runs the experiment in the container.
    """
    target = Path(args.target[0])
    unpacked_info = read_dict(target / '.reprounzip')
    cmdline = args.cmdline

    # Loads config
    runs, packages, other_files = load_config(target / 'config.yml', True)

    selected_runs = get_runs(runs, args.run, cmdline)

    # Destroy previous container
    if 'ran_container' in unpacked_info:
        container = unpacked_info.pop('ran_container')
        logging.info("Destroying previous container %s",
                     container.decode('ascii'))
        retcode = subprocess.call(['docker', 'rm', '-f', container])
        if retcode != 0:
            logging.error("Error deleting previous container %s",
                          container.decode('ascii'))
        write_dict(target / '.reprounzip', unpacked_info)

    # Use the initial image directly
    if 'current_image' in unpacked_info:
        image = unpacked_info['current_image']
        logging.debug("Running from image %s", image.decode('ascii'))
    else:
        logging.critical("Image doesn't exist yet, have you run setup/build?")
        sys.exit(1)

    # Name of new container
    container = make_unique_name(b'reprounzip_run_')

    hostname = runs[selected_runs[0]].get('hostname', 'reprounzip')

    # Get the local bridge IP
    ip_str = get_iface_addr('docker0')

    # X11 handler
    x11 = X11Handler(args.x11, ('internet', ip_str), args.x11_display)

    cmds = []
    for run_number in selected_runs:
        run = runs[run_number]
        cmd = 'cd %s && ' % shell_escape(run['workingdir'])
        cmd += '/usr/bin/env -i '
        environ = x11.fix_env(run['environ'])
        cmd += ' '.join('%s=%s' % (k, shell_escape(v))
                        for k, v in iteritems(environ))
        cmd += ' '
        # FIXME : Use exec -a or something if binary != argv[0]
        if cmdline is None:
            argv = [run['binary']] + run['argv'][1:]
        else:
            argv = cmdline
        cmd += ' '.join(shell_escape(a) for a in argv)
        uid = run.get('uid', 1000)
        cmd = 'sudo -u \'#%d\' /bin/busybox sh -c %s\n' % (uid,
                                                           shell_escape(cmd))
        cmds.append(cmd)
    cmds = x11.init_cmds + cmds
    cmds = ' && '.join(cmds)

    signals.pre_run(target=target)

    # Creates forwarders
    forwarders = []
    for port, connector in x11.port_forward:
        forwarders.append(
                LocalForwarder(connector, port))

    # Run command in container
    logging.info("Starting container %s", container.decode('ascii'))
    retcode = interruptible_call(['docker', 'run', b'--name=' + container,
                                  '-h', hostname,
                                  '-i', '-t', image,
                                  '/bin/busybox', 'sh', '-c', cmds])
    if retcode != 0:
        logging.critical("docker run failed with code %d", retcode)
        sys.exit(1)

    # Get exit status from "docker inspect"
    out = subprocess.check_output(['docker', 'inspect', container])
    outjson = json.loads(out)
    if (outjson[0]["State"]["Running"] is not False or
            outjson[0]["State"]["Paused"] is not False):
        logging.error("Invalid container state after execution:\n%s",
                      json.dumps(outjson[0]["State"]))
    retcode = outjson[0]["State"]["ExitCode"]
    sys.stderr.write("\n*** Command finished, status: %d\n" % retcode)

    # Store container name (so we can download output files)
    unpacked_info['ran_container'] = container
    write_dict(target / '.reprounzip', unpacked_info)

    signals.post_run(target=target, retcode=retcode)


class ContainerUploader(FileUploader):
    def __init__(self, target, input_files, files, unpacked_info):
        self.unpacked_info = unpacked_info
        FileUploader.__init__(self, target, input_files, files)

    def prepare_upload(self, files):
        if 'current_image' not in self.unpacked_info:
            sys.stderr.write("Image doesn't exist yet, have you run "
                             "setup/build?\n")
            sys.exit(1)

        self.build_directory = Path.tempdir(prefix='reprozip_build_')
        self.docker_copy = []

    def upload_file(self, local_path, input_path):
        stem, ext = local_path.stem, local_path.ext
        name = local_path.name
        nb = 0
        while (self.build_directory / name).exists():
            nb += 1
            name = stem + ('_%d' % nb).encode('ascii') + ext
        name = Path(name)
        local_path.copyfile(self.build_directory / name)
        logging.info("Copied file %s to %s", local_path, name)
        self.docker_copy.append((name, input_path))

    def finalize(self):
        if not self.docker_copy:
            self.build_directory.rmtree()
            return

        from_image = self.unpacked_info['current_image']

        with self.build_directory.open('w', 'Dockerfile',
                                       encoding='utf-8',
                                       newline='\n') as dockerfile:
            dockerfile.write('FROM %s\n\n' % from_image.decode('ascii'))
            for src, target in self.docker_copy:
                # FIXME : spaces in filenames will probably break Docker
                dockerfile.write(
                        'COPY \\\n    %s \\\n    %s\n' % (
                            unicode_(src),
                            unicode_(target)))

            # TODO : restore permissions?

        image = make_unique_name(b'reprounzip_image_')
        retcode = subprocess.call(['docker', 'build', '-t', image, '.'],
                                  cwd=self.build_directory.path)
        if retcode != 0:
            logging.critical("docker build failed with code %d", retcode)
            sys.exit(1)
        else:
            logging.info("New image created: %s", image.decode('ascii'))
            if from_image != self.unpacked_info['initial_image']:
                retcode = subprocess.call(['docker', 'rmi', from_image])
                if retcode != 0:
                    logging.warning("Can't remove previous image, docker "
                                    "returned %d", retcode)
            self.unpacked_info['current_image'] = image
            write_dict(self.target / '.reprounzip', self.unpacked_info)

        self.build_directory.rmtree()


@target_must_exist
def docker_upload(args):
    """Replaces an input file in the container.
    """
    target = Path(args.target[0])
    files = args.file
    unpacked_info = read_dict(target / '.reprounzip')
    input_files = unpacked_info.setdefault('input_files', {})

    try:
        ContainerUploader(target, input_files, files, unpacked_info)
    finally:
        write_dict(target / '.reprounzip', unpacked_info)


class ContainerDownloader(FileDownloader):
    def __init__(self, target, files, container):
        self.container = container
        FileDownloader.__init__(self, target, files)

    def download(self, remote_path, local_path):
        # Docker copies to a file in the specified directory, cannot just take
        # a file name (#4272)
        tmpdir = Path.tempdir(prefix='reprozip_docker_output_')
        try:
            ret = subprocess.call(['docker', 'cp',
                                  self.container + b':' + remote_path.path,
                                  tmpdir.path])
            if ret != 0:
                logging.critical("Can't get output file: %s", remote_path)
                sys.exit(1)
            (tmpdir / remote_path.name).copyfile(local_path)
        finally:
            tmpdir.rmtree()


@target_must_exist
def docker_download(args):
    """Gets an output file out of the container.
    """
    target = Path(args.target[0])
    files = args.file
    unpacked_info = read_dict(target / '.reprounzip')

    if 'ran_container' not in unpacked_info:
        logging.critical("Container does not exist. Have you run the "
                         "experiment?")
        sys.exit(1)
    container = unpacked_info['ran_container']
    logging.debug("Downloading from container %s", container.decode('ascii'))

    ContainerDownloader(target, files, container)


@target_must_exist
def docker_destroy_docker(args):
    """Destroys the container and images.
    """
    target = Path(args.target[0])
    unpacked_info = read_dict(target / '.reprounzip')
    if 'initial_image' not in unpacked_info:
        logging.critical("Image not created")
        sys.exit(1)

    if 'ran_container' in unpacked_info:
        container = unpacked_info.pop('ran_container')
        logging.info("Destroying container...")
        retcode = subprocess.call(['docker', 'rm', '-f', container])
        if retcode != 0:
            logging.error("Error deleting container %s",
                          container.decode('ascii'))

    initial_image = unpacked_info.pop('initial_image')

    if 'current_image' in unpacked_info:
        image = unpacked_info.pop('current_image')
        if image != initial_image:
            logging.info("Destroying image %s...", image.decode('ascii'))
            retcode = subprocess.call(['docker', 'rmi', image])
            if retcode != 0:
                logging.error("Error deleting image %s", image.decode('ascii'))

    logging.info("Destroying image %s...", initial_image.decode('ascii'))
    retcode = subprocess.call(['docker', 'rmi', initial_image])
    if retcode != 0:
        logging.error("Error deleting image %s", initial_image.decode('ascii'))


@target_must_exist
def docker_destroy_dir(args):
    """Destroys the directory.
    """
    target = Path(args.target[0])
    read_dict(target / '.reprounzip')

    logging.info("Removing directory %s...", target)
    signals.pre_destroy(target=target)
    target.rmtree()
    signals.post_destroy(target=target)


def test_has_docker(pack, **kwargs):
    """Compatibility test: has docker (ok) or not (maybe).
    """
    pathlist = os.environ['PATH'].split(os.pathsep) + ['.']
    pathexts = os.environ.get('PATHEXT', '').split(os.pathsep)
    for path in pathlist:
        for ext in pathexts:
            fullpath = os.path.join(path, 'docker') + ext
            if os.path.isfile(fullpath):
                return COMPAT_OK
    return COMPAT_MAYBE, "docker not found in PATH"


def setup(parser, **kwargs):
    """Runs the experiment in a Docker container

    You will need Docker to be installed on your machine if you want to run the
    experiment.

    setup   setup/create    creates Dockerfile (needs the pack filename)
            setup/build     builds the container from the Dockerfile
    upload                  replaces input files in the container
                            (without arguments, lists input files)
    run                     runs the experiment in the container
    download                gets output files from the container
                            (without arguments, lists output files)
    destroy destroy/docker  destroys the container and associated images
            destroy/dir     removes the unpacked directory

    For example:

        $ reprounzip docker setup mypack.rpz experiment; cd experiment
        $ reprounzip docker run .
        $ reprounzip docker download . results:/home/user/theresults.txt
        $ cd ..; reprounzip docker destroy experiment

    Upload specifications are either:
      :input_id             restores the original input file from the pack
      filename:input_id     replaces the input file with the specified local
                            file

    Download specifications are either:
      output_id:            print the output file to stdout
      output_id:filename    extracts the output file to the corresponding local
                            path
    """
    subparsers = parser.add_subparsers(title="actions",
                                       metavar='', help=argparse.SUPPRESS)
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('target', nargs=1, help="Experiment directory")

    # setup/create
    opt_setup = argparse.ArgumentParser(add_help=False)
    opt_setup.add_argument('pack', nargs=1, help="Pack to extract")
    opt_setup.add_argument('--base-image', nargs=1, help="Base image to use")
    opt_setup.add_argument('--distribution', nargs=1,
                           help=("Distribution used in the base image (for "
                                 "package installer selection)"))
    opt_setup.add_argument('--install-pkgs', action='store_true',
                           default=False,
                           help=("Install packages rather than extracting "
                                 "them from RPZ file"))
    opt_setup.add_argument('--unpack-pkgs', action='store_false',
                           default=False,
                           help=("Extract packed packages rather than "
                                 "installing them"))
    parser_setup_create = subparsers.add_parser('setup/create',
                                                parents=[opt_setup, options])
    parser_setup_create.set_defaults(func=docker_setup_create)

    # setup/build
    parser_setup_build = subparsers.add_parser('setup/build',
                                               parents=[options])
    parser_setup_build.set_defaults(func=docker_setup_build)

    # setup
    parser_setup = subparsers.add_parser('setup', parents=[opt_setup, options])
    parser_setup.set_defaults(func=composite_action(docker_setup_create,
                                                    docker_setup_build))

    # upload
    parser_upload = subparsers.add_parser('upload', parents=[options])
    parser_upload.add_argument('file', nargs=argparse.ZERO_OR_MORE,
                               help="<path>:<input_file_name")
    parser_upload.set_defaults(func=docker_upload)

    # run
    parser_run = subparsers.add_parser('run', parents=[options])
    parser_run.add_argument('run', default=None, nargs='?')
    parser_run.add_argument('--cmdline', nargs=argparse.REMAINDER,
                            help="Command line to run")
    parser_run.add_argument('--enable-x11', action='store_true', default=False,
                            dest='x11',
                            help=("Enable X11 support (needs an X server on "
                                  "the host)"))
    parser_run.add_argument('--x11-display', dest='x11_display',
                            help=("Display number to use on the experiment "
                                  "side (change the host display with the "
                                  "DISPLAY environment variable)"))
    parser_run.set_defaults(func=docker_run)

    # download
    parser_download = subparsers.add_parser('download', parents=[options])
    parser_download.add_argument('file', nargs=argparse.ZERO_OR_MORE,
                                 help="<output_file_name>:<path>")
    parser_download.set_defaults(func=docker_download)

    # destroy/docker
    parser_destroy_docker = subparsers.add_parser('destroy/docker',
                                                  parents=[options])
    parser_destroy_docker.set_defaults(func=docker_destroy_docker)

    # destroy/dir
    parser_destroy_dir = subparsers.add_parser('destroy/dir',
                                               parents=[options])
    parser_destroy_dir.set_defaults(func=docker_destroy_dir)

    # destroy
    parser_destroy = subparsers.add_parser('destroy', parents=[options])
    parser_destroy.set_defaults(func=composite_action(docker_destroy_docker,
                                                      docker_destroy_dir))

    return {'test_compatibility': test_has_docker}
