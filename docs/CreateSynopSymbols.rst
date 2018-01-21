CreateSynopSymbols
=====================

This will be outdated soon when no weather type reports are delivered anymore.
This is very quick'n'dirty code to procude synop style images using python.
For Marcus Bayer this was always the most important element of Wetterturnier
wherefore I've implemented it using this code.

The script reads trought he observation database (see :ref:`table-live`) to
get the latest observations for all stations configured in the 
:file:`config.conf` file. For each station and observed time a png figure
will be produced once (won't be re-created if output figure exists).

Uses the :py:class:`synopsymbol.synopsymbol`, see below.
Requires the python matplotlib package to be installed.

To get the script run:

.. code-block:: bash

    ## Make a copy of the config template file and adjust
    ## the settings, namely mysql database access information
    ## and input/output directories in the [essentials] and [additionals]
    ## section.
    cp config.conf.template config.conf 

    ## Execute script (keep care using the virtualenv if you do so)
    python CrateSynopSymbols.py




Class: synopsymbol
----------------------

.. autoclass:: synopsymbol::synopsymbol
    :members:
    :private-members:
    :special-members:



