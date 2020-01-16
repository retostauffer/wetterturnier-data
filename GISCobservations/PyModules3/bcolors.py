# -------------------------------------------------------------------
# - NAME:        bcolors.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2015-02-18
# -------------------------------------------------------------------
# - DESCRIPTION: Just some color definitions used for colorized
#                console output. Mainly for development.
#                To print something in Red e.g.,
#
#                print bcolors.OKRED,
#                print "This test should appear in red",
#                print bcolors.ENDC
#
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-18, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-02-18 08:15 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------

import sys, os
import re

class bcolors:
   HEADER = '\033[95m'
   OKBLUE = '\033[34m'
   OKLIGHTBLUE = '\033[94m'
   OKGREEN = '\033[92m'
   OKLILA  = '\033[35m'
   OKRED   = '\033[91m'
   WARNING = '\033[47m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'


