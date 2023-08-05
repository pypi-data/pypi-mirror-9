Python Middleware for OpenStack Identity API (Keystone)
=======================================================

This is the middleware provided for integrating with the OpenStack
Identity API and handling authorization enforcement based upon the
data within the OpenStack Identity tokens. Also included is middleware that
provides the ability to create audit events based on API requests.

Contents:

.. toctree::
   :maxdepth: 1

   middlewarearchitecture
   audit

Contributing
============

Code is hosted `on GitHub`_. Submit bugs to the Keystone project on
`Launchpad`_. Submit code to the ``openstack/keystonemiddleware`` project
using `Gerrit`_.

.. _on GitHub: https://github.com/openstack/keystonemiddleware
.. _Launchpad: https://launchpad.net/keystonemiddleware
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow

Run tests with ``python setup.py test``.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

