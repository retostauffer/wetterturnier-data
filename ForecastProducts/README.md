

NOTE: VIRTUAL PYTHON ENVIRONMENT
================================
The local OS does not support sufficiently new python packages. Therefore
I installed a python virtual environment (in ../venv/bin/python) on the
wetterturnier server. Please use this one.

Activate venv:
- source ~/venv/bin/activate

Or just use the binaries:
- ~/venv/bin/python DownloadAll.py
- ../venv/bin/python DownloadAll.py


REQUIREMENTS
============
Requires python package 'pillow' for image manipulation with tiff.
If libtiff-devel is not installed while installing the python 'pillow'
package, the following error will be shown: decoder libtiff not available.

In this case first install libtiff (or libtiff-tools) and libtiff-devel on your
system and re-install 'pillow' (../venv/bin/pip install --no-cache-dir -I
pillow).  Newer versions of pip don't have the --no-cache-dir option, just call
it without (../venv/bin/pip install -I pillow).


HOW IT WORKS
============

Usage:
- ../venv/bin/python DownloadAll.py ## does all you need

You can also specify to process only one specific type (read
config.conf file to see which types are defined).
- ../venv/bin/python DownloadAll.py --type analysis


DOCUMENTATION
==============

TODO RETO







