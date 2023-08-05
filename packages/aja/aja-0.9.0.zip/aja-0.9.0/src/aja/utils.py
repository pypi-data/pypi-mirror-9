# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os.path
from tempfile import NamedTemporaryFile
from urlparse import (
    urlparse,
    urljoin
)

from fabric import api
from fabric.network import key_filenames
from zc.buildout.buildout import Buildout


_memo = {}


def memoize(function):
    def wrapper(*args):
        if args in _memo:
            return _memo[args]
        else:
            rv = function(*args)
            _memo[args] = rv
            return rv
    return wrapper


@memoize
def get_buildout_config(buildout_filename):
    """Parse buildout config with zc.buildout ConfigParser
    """
    print("[localhost] get_buildout_config: {0:s}".format(buildout_filename))
    buildout = Buildout(buildout_filename, [('buildout', 'verbosity', '-100')])
    while True:
        try:
            len(buildout.items())
            break
        except OSError:
            pass
    return buildout


def get_buildout_parts(buildout, query=None):
    """Return buildout parts matching the given query
    """
    parts = names = (buildout['buildout'].get('parts') or '').split('\n')
    for name in names:
        part = buildout.get(name) or {}
        for key, value in (query or {}).items():
            if value not in (part.get(key) or ''):
                parts.remove(name)
                break
    return parts


def get_buildout_eggs(buildout, query=None):
    """Return buildout eggs matching the parts for the given query
    """
    eggs = set()
    for name in get_buildout_parts(buildout, query=query):
        if name == 'buildout':
            continue  # skip eggs from the buildout script itself
        path = os.path.join(buildout['buildout'].get('bin-directory'), name)
        if os.path.isfile(path):
            eggs.update(parse_eggs_list(path))
    return list(eggs)


def parse_eggs_list(path):
    """Parse eggs list from the script at the given path
    """
    with open(path, 'r') as script:
        data = script.readlines()
        start = 0
        end = 0
        for counter, line in enumerate(data):
            if not start:
                if 'sys.path[0:0]' in line:
                    start = counter + 1
            if counter >= start and not end:
                if ']' in line:
                    end = counter
        script_eggs = tidy_eggs_list(data[start:end])
    return script_eggs


def tidy_eggs_list(eggs_list):
    """Tidy the given eggs list
    """
    tmp = []
    for line in eggs_list:
        line = line.lstrip().rstrip()
        line = line.replace('\'', '')
        line = line.replace(',', '')
        if line.endswith('site-packages'):
            continue
        tmp.append(line)
    return tmp


@contextmanager
def get_rsync_pull(files, target='/', exclude=None, arguments=None):
    with _get_rsync(
            files, target=target, exclude=exclude, arguments=arguments,
            source='{0:s}@{1:s}:/'.format(api.env.user, api.env.host)) as cmd:
        yield cmd


@contextmanager
def get_rsync_push(files, source='/', exclude=None, arguments=None):
    with _get_rsync(
            files, source=source, exclude=exclude, arguments=arguments,
            target='{0:s}@{1:s}:/'.format(api.env.user, api.env.host)) as cmd:
        yield cmd


@contextmanager
def _get_rsync(files, source='/', target='/', exclude=None, arguments=None):
    with NamedTemporaryFile() as files_file:
        with NamedTemporaryFile() as exclude_file:
            cmd = ['rsync']

            ##
            # Fix or set default files
            if isinstance(files, str) or isinstance(files, unicode):
                files = [files]
            elif files is None:
                files = []

            ##
            # Fix or set default exclude
            if isinstance(exclude, str) or isinstance(exclude, unicode):
                exclude = [exclude]
            elif exclude is None:
                exclude = []

            ##
            # Set common prefix to avoid rsync with root ('/') when possible
            prefix = os.path.commonprefix(files + exclude)
            if not os.path.exists(prefix):
                prefix = os.path.dirname(prefix)
            if os.path.isdir(prefix) and not prefix.endswith(os.path.sep):
                prefix += os.path.sep
            if (prefix.startswith(target.split(':')[-1])
                    and prefix.startswith(target.split(':')[-1])):
                source = ':'.join(source.split(':')[:-1] + [prefix])
                target = ':'.join(target.split(':')[:-1] + [prefix])
            else:
                prefix = ''

            ##
            # Build files-from
            for line in (files or []):
                if line[len(prefix):]:
                    files_file.write(line[len(prefix):] + '\n')
                files_file.flush()
            files_file.seek(0)
            if files and files_file.read():
                cmd.append('--files-from={0:s}'.format(files_file.name))

            ##
            # Build exclude-from
            for line in (exclude or []):
                if line[len(prefix):]:
                    exclude_file.write(line[len(prefix):] + '\n')
                exclude_file.flush()
            exclude_file.seek(0)
            if exclude and exclude_file.read():
                cmd.append('--exclude-from={0:s}'.format(exclude_file.name))

            ##
            # -p preserve permissions
            # -t preserve modification times
            # -h output numbers in a human-readable format
            # -l copy symlinks as symlinks
            # -r recurse into directories
            # -z compress file data during the transfer
            cmd.append('-pthlrz')

            if arguments:
                cmd.append(arguments)

            ##
            # Build rsh
            if any([api.env.port, key_filenames()]):
                cmd.append('--rsh="ssh {0:s}"'.format(' '.join(filter(bool, [
                    # api.env.port
                    api.env.port and '-p {0:s}'.format(api.env.port) or None,
                    # key_filenames
                    ' '.join(['-i {0:s}'.format(key)
                              for key in key_filenames()])
                ]))))

            cmd.append(source)
            cmd.append(target)

            yield ' '.join(cmd)


def get_buildout_directory(buildout_directory):
    buildout_directory_prefix = api.env.get('buildout_directory_prefix') or ''
    if not urlparse(buildout_directory).path.startswith('/'):
        return os.path.join(buildout_directory_prefix,
                            buildout_directory)
    else:
        return buildout_directory


def get_buildout_extends(buildout_extends):
    buildout_extends_prefix = api.env.get('buildout_extends_prefix') or ''
    if not urlparse(buildout_extends).path.startswith('/'):
        return urljoin(buildout_extends_prefix, buildout_extends)
    else:
        return buildout_extends
