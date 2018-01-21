Database Tables
===============

.. _database-obs:

.. _tables:

live
----

.. _table-live:

The ``live`` table is used to store incoming observations.  Please note that
only a subset of all columns is shown in the table below. The script processing
the observations and saving them into this database table automatically creates
additional columns if there are data. ``...`` in the table indicate the data
columns (e.g,. temperature observations, cloud cover observations, ...).

The ``live`` table is a rolling database containing the latest observations for
all incoming stations. The script :ref:`CleanUp.py <script-cleanup>` cleans the database from time
to time moving the observations for some specific stations into the
:ref:`archive <table-archive>` database table and deletes all others.


.. include:: dbtables/live.rsx


archive
-------

.. _table-archive:

The archive table has the same structure as the :ref:`live <table-live>`
database table and contains long-term archive data for a set of specified
stations. We keep the data for the tournament stations and drop all others
as we don't want to keep a copy of all observations (would be a huge database
and an unnecessary and unused copy of everything).

.. include:: dbtables/archive.rsx


.. _database-wetterturnier:

stations
----------

.. _table-stations:

Station information as read from the BUFR files.

.. include:: dbtables/stations.rsx




bufrdesc
----------

.. _table-bufrdesc:

BUFR description as read from the BUFR files.

.. include:: dbtables/bufrdesc.rsx



