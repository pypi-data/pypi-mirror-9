# -*- coding: utf-8 -*-
import os
import unittest
from fabric import api

from aja.utils import (
    get_buildout_config,
    get_buildout_parts,
    get_buildout_eggs,
    get_rsync_push,
    _memo
)

from tempfile import mkdtemp


class TestUtils(unittest.TestCase):

    def setUp(self):
        self._cwd = os.getcwd()
        self._buildout = mkdtemp()
        self._buildout_cfg = os.path.join(self._buildout, 'buildout.cfg')
        self._buildout_bin = os.path.join(self._buildout, 'bin')
        self._buildout_bin_fab = os.path.join(self._buildout_bin, 'fab')

        buildout = open(self._buildout_cfg, 'w')
        buildout.write("""\
[buildout]
parts = fab
develop = .

[fab]
recipe = zc.recipe.egg
eggs =
    aja
    fabric
scripts =
    fab
""")
        buildout.close()

        os.mkdir(self._buildout_bin)

        script = open(self._buildout_bin_fab, 'w')
        script.write("""\
#!/usr/bin/python

import sys
sys.path[0:0] = [
  '/var/buildout/eggs-directory/Fabric-1.8.3-py2.7.egg',
  '/var/buildout/eggs-directory/paramiko-1.12.4-py2.7.egg',
  '/var/buildout/eggs-directory/zc.buildout-2.2.1-py2.7.egg',
  '/var/buildout/eggs-directory/setuptools-3.6-py2.7.egg',
  '/var/buildout/eggs-directory/ecdsa-0.11-py2.7.egg',
  '/var/buildout/eggs-directory/pycrypto-2.6.1-py2.7-macosx-10.9-intel.egg',
  '/var/buildout/eggs-directory/aja-1.0.0-py2.7.egg',
  ]

import fabric.main

if __name__ == '__main__':
    sys.exit(fabric.main.main(aja.tasks.__path__))
""")
        script.close()

    def tearDown(self):
        os.unlink(self._buildout_bin_fab)
        os.rmdir(self._buildout_bin)
        os.unlink(self._buildout_cfg)
        os.rmdir(self._buildout)
        os.chdir(self._cwd)

    def test_memoize(self):
        get_buildout_config(self._buildout_cfg)
        self.assertTrue(len(_memo) > 0)

    def test_get_buildout_config(self):
        buildout = get_buildout_config(self._buildout_cfg)
        self.assertIn('buildout', buildout)
        self.assertIn('fab', buildout)

    def test_get_buildout_parts(self):
        buildout = get_buildout_config(self._buildout_cfg)
        parts = get_buildout_parts(buildout)
        self.assertEqual(parts, ['fab'])

    def test_get_buildout_eggs(self):
        buildout = get_buildout_config(self._buildout_cfg)
        eggs = get_buildout_eggs(buildout)
        self.assertEqual(eggs, [
            '/var/buildout/eggs-directory/paramiko-1.12.4-py2.7.egg',
            '/var/buildout/eggs-directory/ecdsa-0.11-py2.7.egg',
            '/var/buildout/eggs-directory/setuptools-3.6-py2.7.egg',
            '/var/buildout/eggs-directory/pycrypto-2.6.1-py2.7-macosx-10.9'
            '-intel.egg',
            '/var/buildout/eggs-directory/zc.buildout-2.2.1-py2.7.egg',
            '/var/buildout/eggs-directory/aja-1.0.0-py2.7.egg',
            '/var/buildout/eggs-directory/Fabric-1.8.3-py2.7.egg'
        ])

    def test_get_rsync_push(self):
        buildout = get_buildout_config(self._buildout_cfg)
        eggs = get_buildout_eggs(buildout)
        api.env.user = 'foo'
        api.env.host = 'bar'
        with get_rsync_push(eggs) as cmd:
            self.assertTrue(cmd.endswith(
                '/var/buildout/eggs-directory '
                'foo@bar:/var/buildout/eggs-directory')
            )


if __name__ == '__main__':
    unittest.main()
