===============
OpenStackClient
===============

OpenStackClient (aka OSC) is a command-line client for OpenStack that
brings the command set for Compute, Identity, Image, Object Store and Volume
APIs together in a single shell with a uniform command structure.

Contents:

.. toctree::
   :maxdepth: 1

   command-list
   commands
   plugins
   authentication
   interactive
   humaninterfaceguide
   releases
   man/openstack

Getting Started
---------------

* Try :doc:`some commands <command-list>`
* Read the source `on OpenStack's Git server`_
* Install OpenStackClient from `PyPi`_ or a `tarball`_


Project Goals
-------------

* Use the OpenStack Python API libraries, extending or replacing them as required
* Use a consistent naming and structure for commands and arguments
* Provide consistent output formats with optional machine parseable formats
* Use a single-binary approach that also contains an embedded shell that can execute
  multiple commands on a single authentication (see libvirt's virsh for an example)
* Independence from the OpenStack project names; only API names are referenced (to
  the extent possible)

Contributing
============

OpenStackClient utilizes all of the usual OpenStack processes and requirements for
contributions.  The code is hosted `on OpenStack's Git server`_. `Bug reports`_
and `blueprints`_ may be submitted to the :code:`python-openstackclient` project
on `Launchpad`_.  Code may be submitted to the
:code:`openstack/python-openstackclient` project using `Gerrit`_.

.. _`on OpenStack's Git server`: https://git.openstack.org/cgit/openstack/python-openstackclient/tree
.. _Launchpad: https://launchpad.net/python-openstackclient
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _Bug reports: https://bugs.launchpad.net/python-openstackclient/+bugs
.. _blueprints: https://blueprints.launchpad.net/python-openstackclient
.. _PyPi: https://pypi.python.org/pypi/python-openstackclient
.. _tarball: http://tarballs.openstack.org/python-openstackclient

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
