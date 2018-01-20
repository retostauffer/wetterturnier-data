

CreateSynopSymbols
==================

This is a small script I created to be able to show some
synop symbols on wetterturnier.de. The backend uses a
mysql database table where the observations for the wetterturnier
are stored. If you would like to use this script for any other
purpose, you have to change the way how the data will be loaded.


How to use
==========

Warning: on the wetterturnier server there is a virtual python
environmnet offering the latest version of matplotlib, which is
needed to create the figures. Therefore call the script like
following:

- ../venv/bin/python CreateSynopSymbols.py

The Script then reads the [config.conf] file and automatically
opens a mysql database connection. The data are stored in
obs.live (latest observations from bufr decoder).


Some tips and hints
===================

By default, the script only recreates the synop symbols of the
current hour. This is the "live" mode. If a figure exists on disc,
it wont be recreated again. This allows to run the script in a
short regular interval (cronjob) without the need of a lot of
performance on the server.

However, if you would like to re-create the symbols, lets say
for the last 10 hours, there is a "tmax" option inside
CreateSynopSymbols.py. Is soon as "tmax > 0" (default is "tmax = 0")
the script re-creates the figures for the last "tmax" hours.
In this mode, each figure will be re-drawn, no matter if it already
exists on disc or not. Dont use this as an operational setting!


File description
================

Python script files
-------------------
It is not a full python package right now, the script files
needed and loaded are located in the PyModules directory.

- database.py: creates a database handling object
- readconfig.py: creates a readconfig object, reading the config files
- drawbarb.py: draws the wind barbs. Is used by synopsymbols.py
- synopsymbols.py: main class handling the whole creation. Extends the drawbarb class.

Fonts files
-----------
To draw the images, I am using some own fonts instead of coding
each symbol. For example: a "ww = 42" (current weather) will use the
font "w4.ttf" and in there the character "2" whic is the synop symbol for
"ww42". The svg files located in this cirectory contain the font original
files (you can easily modify them using e.g., Inkscape, read a manual on
"how to create your own font with Inkscape"). To use them in python, the
svg font files have to be converted to proper true type fonts (ttf files).
There are some online converters which work quite well.

- a.ttf: pressure tendency symbols
- CH.ttf: high cloud symbols
- CL.ttf: low cloud symbols
- CM.ttf: mid level cloud symbols
- ff.ttf: unused i guess
- n.ttf: cloud cover symbols
- w0.ttf: current weather, ww00 to ww09 [on characters 0-9]
- w1.ttf - wX.ttf: equivalent to w0.ttf
- wpast.ttf: past weather symbols




















