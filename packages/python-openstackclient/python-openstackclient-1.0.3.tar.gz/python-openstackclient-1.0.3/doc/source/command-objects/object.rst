======
object
======

Object Store v1

object create
-------------

Upload object to container

.. program:: object create
.. code:: bash

    os object create
        <container>
        <filename> [<filename> ...]

.. describe:: <container>

    Container for new object

.. describe:: <filename>

    Local filename(s) to upload

object delete
-------------

Delete object from container

.. program:: object delete
.. code:: bash

    os object delete
        <container>
        <object> [<object> ...]

.. describe:: <container>

    Delete object(s) from <container>

.. describe:: <object>

    Object(s) to delete

object list
-----------

List objects

.. program object list
.. code:: bash

    os object list
        [--prefix <prefix>]
        [--delimiter <delimiter>]
        [--marker <marker>]
        [--end-marker <end-marker>]
        [--limit <limit>]
        [--long]
        [--all]
        <container>]

.. option:: --prefix <prefix>

    Filter list using <prefix>

.. option:: --delimiter <delimiter>

    Roll up items with <delimiter>

.. option:: --marker <marker>

    Anchor for paging

.. option:: --end-marker <end-marker>

    End anchor for paging

.. option:: --limit <limit>

    Limit number of objects returned

.. option:: --long

    List additional fields in output

.. option:: --all

    List all objects in <container> (default is 10000)

.. describe:: <container>

    Container to list

object save
-----------

Save object locally

.. program:: object save
.. code:: bash

    os object save
        [--file <filename>]
        [<container>]
        [<object>]

.. option:: --file <filename>

    Destination filename (defaults to object name)

.. describe:: <container>

    Download <object> from <container>

.. describe:: <object>

    Object to save

object show
-----------

Display object details

.. program:: object show
.. code:: bash

    os object show
        <container>
        <object>

.. describe:: <container>

    Display <object> from <container>

.. describe:: <object>

    Object to display
