

DWD BUFR TABLES
================
Weiss noch nicht obs geht :). Aber ich wollte den Link 
mal speichern.
https://github.com/mknx/smarthome/wiki/DWD

Der DWD stellt seit heute das Verzeichnis "/gds/OBS/BUFRTABLES/" mit
allen derzeitigen BUFR-Tabellen zum Download zur Verfuegung.

TODO 2015-07-19
===============
Ich brauche ein lockbit

KNOWN PROBLEMS 2015-07-19
=========================
Sometimes, ffx is recorded twice. I just take the "latter"
observed value. Sometimes the values (first and second 
recorded ffx, displacement 10min) were the same, some
times they were different. However, take last one and
dont think about the consequences :).

Each binary files opens the database once. I have to find
a nicer way where I am loading all data and push them
to the database once or so.


