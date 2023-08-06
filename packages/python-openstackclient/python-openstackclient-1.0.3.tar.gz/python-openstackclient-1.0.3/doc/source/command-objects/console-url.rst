===========
console url
===========

Server remote console URL

Compute v2

console url show
----------------

Show server's remote console URL

.. program:: console url show
.. code:: bash

    os console url show
        [--novnc | --xvpvnc | --spice]
        <server>

.. option:: --novnc

    Show noVNC console URL (default)

.. option:: --xvpvnc

    Show xpvnc console URL

.. option:: --spice

    Show SPICE console URL

.. describe:: <server>

    Server to show URL (name or ID)
