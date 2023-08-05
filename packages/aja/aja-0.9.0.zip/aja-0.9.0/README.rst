Aja
===

.. image:: https://secure.travis-ci.org/pingviini/aja.png
   :target: http://travis-ci.org/pingviini/aja

Aja provides Fabric_ tasks for deploying buildouts_ from staging server to
remote production servers:

* it assumes buildout with absolute path (this is the buildout default)

* it assumes that all the relevant paths (python, buildout, shared eggs, etc)
  are identical for the staging and production servers

* bootstrap and buildout are always run on the staging server only

* buildout is deployed by pushing its bin-, parts- and (local or shared)
  eggs-directories into the remote production server using rsync

.. _buildout: https://pypi.python.org/pypi/zc.buildout
.. _buildouts: https://pypi.python.org/pypi/zc.buildout
.. _Fabric: https://pypi.python.org/pypi/Fabric


Installation
------------

Aja can be installed like any Python package:

.. code:: bash

   $ pip install aja

But be aware that Aja comes with the following dependencies

* Fabric
* paramiko
* zc.buildout
* setuptools
* ecdsa
* pycrypto

and therefore, it's recommended to use a dedicated virtualenv.

Aja doesn't have it's own executable, but is executed using Fabric's ``fab``
command. Of course, it is possible to symlink that as ``aja``.


Configuration
-------------

Aja is configured with a fabfile, e.g. ``fabfile.py``:

.. code:: python

   import fabric.api
   fabric.api.env.update({
       'buildout_directory_prefix': '',  # optional
       'buildout_extends_prefix': '',    # optional
   })
   from aja.tasks import *


``buildout_directory_prefix`` provides optional convenience when creating new
buildouts or when looking for buildouts for the other commands.

``buildout_extends_prefix`` provides optional convenience when creating new
buildout.


Usage
-----

Aja maps Fabric's hosts into buildouts so that for each buildout, it fills
``fabric.api.env`` with variables from ``[aja]`` part in the buildout (this is
quite similar to `collective.hostout`_). The rest of the resolved buildout file
can be found at ``fabric.api.env.buildout``.

.. _collective.hostout: https://pypi.python.org/pypi/collective.hostout

An example ``[aja]`` part could look like:

.. code:: ini

   [aja]
   executable = /usr/local/python/bin/python
   host_string = buildout@production
   key_filename = /home/buildout/.ssh/id_rsa

This part would configure Aja tasks to use particular Python virtualenv for
running the buildout
and
push the results into server ``production`` by performing rsync using the
given key file.

Example Aja usage could look like:

.. code:: bash

   $ fab create:/var/buildout/plone,/vagrant/plone-4.3.cfg
   $ fab -H /var/buildout/plone buildout push

And with the following convenience configuration in fabfile:

.. code:: python

   import fabric.api
   fabric.api.env.update({
       'buildout_directory_prefix': '/var/buildout',
       'buildout_extends_prefix': '/vagrant',
   })
   from aja.tasks import *

The previous example usage could look like:

.. code:: bash

   $ fab create:plone,plone-4.3.cfg
   $ fab -H plone buildout push

.. note::

   ``buildout_extends_prefix`` can also be an URL like
   ``http://myserver/buildouts/``


Extending
---------

Aja provides only the most basic fabric tasks, but it provides a custom
task class ``aja.tasks.AjaTask``, which provides resolved buildout
at ``fabric.api.env.buildout``. This makes it easy to define custom tasks
in your fabfile, e.g.

.. code:: python

   from fabric import api
   from fabric.operations import run
   from aja.tasks import AjaTask

   @task(task_class=AjaTask)
   def purge():
       buildout_bin = api.env.buildout['buildout'].get('bin-directory')
       buildout_parts = api.env.buildout['buildout'].get('parts-directory')
       run('rm -rf {0:s}'.format(buildout_bin))
       run('rm -rf {0:s}'.format(buildout_parts))
   purge.__doc__ = \
       """Clean bin- and parts-directories (e.g. before push)
       """
