GISCobservations
=========================

This thing is named **GISC observations** as we get some data from
the DWD GISC interface. Ideally all data would come from this one
system, however, that was not possible (did not got access, furthermore
station 11320 Universitaet Innsbruck is not included in the GISC at all).

.. note:: There are is a version ``extractBUFReccodes.py`` which has the
    very same structure as ``extractBUFRperl.py`` and makes use of the
    ecmwf eccodes python library to extract the BUFR files. This is
    non-finished code! However, in case one has to switch over to
    the eccodes library one might use this draft. All you would have to
    do at the end is to change the include in the :file:`bufr.py` file.

    However, the documentation only provides information about the
    currently used ``extractBUFRperl.py`` script.


The worker script
-----------------------

.. _script-bufr:

The main script to be executed is :file:`bufr.py`. If started without
any input arguments the default input folders will be checked for new
incoming bufr files. There are two incoming folders specified via
:file:`config.conf`. Depending on the folder where the files are stored
the data get different labels in the database, either *essential* (means
open data, can be used and downloaded by everyone) or *additional* (closed
data, access will only be given to logged in users when using the
`Wetterturnier Wordpress Plugin <https://github.com/retostauffer/wp-wetterturnier>`_.
For both data types (essential and additional) an incoming directory (``indir``)
and an outgoing directory (``outdir``) is specified in the :file:`config.conf` file.

The script :file:`bufr.py` automatically checks the incoming folders for new files.
If there are new files the files are processed using :class:`extractBUFRperl::extractBUFR`
and moved into the output directory. The will be stored either in a subfolder
``error`` if the BUFR file could not have been extracted/processed or in a subfolder
``processed`` if successfully processed.

To run the script please note that the corresponding BUFR tables have to be
available. They can either be located in the system wide default folder or 
specified via environment variable ``BUFR TABLES``.
Note that some BUFR files require custom BUFR TABLE files (e.g., for a specific
subcentre using custom BUFR entries). WMO style BUFR TABLES can for example be
downloaded `on the ECMWF website <https://software.ecmwf.int/wiki/display/BUFR/BUFRDC+Home>`_.
WARNING: the BUFR tables in this archive have the suffix ``.txt`` while
``bufrread.pl`` is looking for ``.TXT`` files. Simple solution: link all your files
``.txt`` to ``.TXT`` and try.

To get this script to run:

.. code-block:: bash

    ## Make a copy of the config template file and adjust
    ## the settings, namely mysql database access information
    ## and input/output directories in the [essentials] and [additionals]
    ## section.
    cp config.conf.template config.conf 

    ## If required: set BUFR TABLES environment variable
    export BUFR_TABLES=/path/to/your/bufrtables

    ## Execute script (keep care using the virtualenv if you do so)
    python bufr.py

For testing a specific file can be specified using the ``-f/--file`` flag.
In this case this file will be read and *not moved* after execution.

.. code-block:: bash

    ## Processing af specific bufr file (keep care using the virtualenv if you do so)
    python bufr.py --file <path/to/buf/file>




The cleanup script
----------------------

.. _script-cleanup:

To keep the databaes small only a subset of data will be archived while the
live table is a rolling table containing the last N days of data only.
Furthermore, old unused BUFR files should be removed from the disc.
The :file:`CleanUp.py` script does this job using the configuration from the
:file:`config.conf` file (mysql access config and the ``[cleanup]`` section).

To get the script running:

.. code-block:: bash

    ## Make a copy of the config template file if you havn't done this
    ## yet and adjsut the settings, namely mysql database access information
    ## and input/output directories in the [essentials] and [additionals]
    ## section. For the archive table: check the list of stations in the
    ## [cleanup] section which should be moved from the live table (``srctable``)
    ## to the archive table (``dsttable``).
    cp config.conf.template config.conf 

    ## Run the script
    python cleanup.py

The script ...

* Reads the :file:`config.conf` file
* Creates an object of class :class:`cleanup`
  * Deletes old raw (BUFR) files from the disc
  * Moves a subset of observations from the live table into the archive table
  * Removes old observations from the live table


Class: cleanup
--------------------

This is the class used by the :file:`CleanUp.py`.

.. autoclass:: cleanup::cleanup
    :members:


Class: extractBUFR
------------------------

Main class, extracting observations from BUFR data files using the
`Geo::BUFR <http://search.cpan.org/dist/Geo-BUFR/lib/Geo/BUFR.pm>`_ ``bufrread.pl``
script. ``bufrread.pl`` converts the BUFR files into ASCII whcih will be parsed
by :class:`extractBUFRperl::extractBUFR` and stored into the database.

.. autoclass:: extractBUFRperl::extractBUFR
    :members:
    :private-members:
    :special-members:

Class: bufrentry
-------------------------

:class:`extractBUFRperl::extractBUFR` uses the perl library
`Geo::BUFR <http://search.cpan.org/dist/Geo-BUFR/lib/Geo/BUFR.pm>`_ ``bufrread.pl``
to extract the binary BUFR files (called internally via ``subprocess.Popen``) 

The script ``bufrread.pl`` returns the content of the BUFR file in ASCII where each
line in the data section corresponds to one BUFR entry.
:class:`extractBUFRperl::extractBUFR` stores each line in a
:class:`extractBUFRperl::bufrentry` object which are easy to iterate over.

.. autoclass:: extractBUFRperl::bufrentry
    :members:
    :private-members:
    :special-members:

Class: bufrdesc
-----------------------

The class :class:`extractBUFRperl::extractBUFR` uses
:class:`extractBUFRperl::bufrdesc` classes to handle the bufr parameter
configuration read from the :file:`bufr_config.conf` file.  Each entry
(:obj:`bufrentry`) read from the BUFR file has to match a parameter configured
in :file:`bufr_config.conf` and will be dropped else.

For ease of use the configuration of :file:`bufr_config.conf` is read piece-wise
and each config is stored as a :class:`extractBUFRperl::bufrdesc` object.

.. autoclass:: extractBUFRperl::bufrdesc
    :members:
    :private-members:
    :special-members:

