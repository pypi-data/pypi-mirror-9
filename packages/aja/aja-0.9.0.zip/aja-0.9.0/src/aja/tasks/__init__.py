# -*- coding: utf-8 -*-
import os
from tempfile import NamedTemporaryFile

from fabric import api
from fabric.api import task
from fabric.context_managers import (
    lcd,
    settings
)
from fabric.contrib.files import exists
from fabric.network import parse_host_string
from fabric.tasks import (
    Task,
    execute
)
from fabric.operations import (
    local,
    run
)
from aja.utils import (
    get_buildout_directory,
    get_buildout_config,
    get_buildout_extends,
    get_buildout_eggs,
    get_rsync_push
)


class AjaTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(AjaTask, self).__init__(*args, **kwargs)
        self.func = func

    def run(self, *args, **kwargs):
        buildout_directory = get_buildout_directory(api.env.host)
        buildout = get_buildout_config(
            os.path.join(buildout_directory, 'buildout.cfg')
        )
        keys = api.env.keys()
        config = dict([
            (key.replace('-', '_'), value) for key, value
            in buildout.get('aja', {}).items() if key in keys
        ])
        if 'host_string' in config:
            config.update(parse_host_string(config.get('host_string')))
        config['buildout'] = buildout
        directory = buildout.get('buildout', {}).get('directory')
        with settings(**config):
            with lcd(directory):
                return self.func(*args, **kwargs)


@task()
def create(buildout_directory, buildout_extends):
    """Create buildout directory
    """
    ##
    # Resolve arguments
    directory = get_buildout_directory(buildout_directory)
    extends = get_buildout_extends(buildout_extends)

    ##
    # Create buildout directory
    local('mkdir -p {0:s}'.format(directory))

    ##
    # Create buildout.cfg
    filename = os.path.join(directory, 'buildout.cfg')
    contents = """\
[buildout]
extends = {0:s}
""".format(extends)

    ##
    # Write buildout.cfg
    with NamedTemporaryFile() as output:
        print("[localhost] create: {0:s}".format(output.name))
        output.write(contents)
        output.flush()
        local('cp {0:s} {1:s}'.format(output.name, filename))
        local('chmod a+r {0:s}'.format(filename))


@task(task_class=AjaTask)
def bootstrap_download(*args):
    cmd = 'curl https://bootstrap.pypa.io/bootstrap-buildout.py -o bootstrap.py'
    local(' '.join([cmd] + list(args)))
bootstrap_download.__doc__ = \
    """Download bootstrap.py
    """


@task(task_class=AjaTask)
def bootstrap(*args):
    if not os.path.isfile('bootstrap.py'):
        execute(bootstrap_download)
    cmd = '{0:s} bootstrap.py'.format(
        (api.env.buildout.get('aja') or {}).get('executable')
        or api.env.buildout.get('buildout').get('executable')
    )
    local(' '.join([cmd] + list(args)))
bootstrap.__doc__ = \
    """Execute bootstrap.py
    """


@task(task_class=AjaTask)
def buildout(*args):
    if not os.path.isfile('bin/buildout'):
        execute(bootstrap)
    cmd = 'bin/buildout'
    local(' '.join([cmd] + list(args)))
buildout.__doc__ = \
    """Execute bin/buildout
    """


@task(task_class=AjaTask)
def push():
    buildout_part = api.env.buildout['buildout']
    ##
    # Push bin
    if not exists(buildout_part.get('bin-directory')):
        run('mkdir -p {0:s}'.format(buildout_part.get('bin-directory')))
    with get_rsync_push(
        files=buildout_part.get('bin-directory'),
        exclude=os.path.join(buildout_part.get('bin-directory'), 'buildout')
    ) as cmd:
        local(cmd)
    ##
    # Push parts
    if not exists(buildout_part.get('parts-directory')):
        run('mkdir -p {0:s}'.format(buildout_part.get('parts-directory')))
    with get_rsync_push(files=buildout_part.get('parts-directory')) as cmd:
        local(cmd)
    ##
    # Push eggs
    eggs = get_buildout_eggs(api.env.buildout)
    if not exists(os.path.commonprefix(eggs)):
        run('mkdir -p {0:s}'.format(os.path.commonprefix(eggs)))
    with get_rsync_push(files=get_buildout_eggs(api.env.buildout)) as cmd:
        local(cmd)
push.__doc__ = \
    """Push bin-, parts- and eggs-directories
    """
