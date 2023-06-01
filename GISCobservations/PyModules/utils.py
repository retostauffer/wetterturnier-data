# -------------------------------------------------------------------
# - NAME:        utils.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-21
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-21, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-08-08 06:11 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


def movefile(config,stint,file,typ,ok):

   import sys, os

   if not typ == 'bufr' and not typ == 'synop':
      sys.exit('Problems calling utils.movefile. Input typ %s not allowed (use bufr/synop).' % typ)
   if not type(ok) == type(True):
      sys.exit('Problems calling utils.movefile. Input ok has to be logical.')

   # - Source file:
   print('    Source file: %s' % file)

   # - Destination directory
   #   not ok means ok == False .. however :D 
   if not ok:
      dstdir = '%s/%s/error' % (config['%s_outdir' % stint],typ)
   else:
      dstdir = '%s/%s/processed' % (config['%s_outdir' % stint],typ)

   # - Create dir if not existing
   if not os.path.isdir( dstdir ):
      os.system('mkdir -p %s' % dstdir)

   # - Destination file:
   dstfile = '%s/%s' % (dstdir,file.split('/')[-1])
   print('    Destination is: %s' % dstfile)

   os.rename(file,dstfile)

   return


from datetime import datetime as dt, timezone as tz
import numpy as np

def dt2str( datetime, fmt ):
   """datetime -> string"""
   datetime_str = datetime.strftime( fmt )
   return datetime_str

def dt2ts( datetime, min_time = False, tzinfo=tz.utc ):
   """convert today's datetime object to timestamp"""
   if min_time: dtts = dt.combine( datetime, dt.min.time() )
   else: dtts = datetime
   return int( dtts.replace( tzinfo = tz.utc ).timestamp() )

def str2dt( string, fmt, tzinfo=tz.utc ):
   """convert string to datetime object"""
   datetime = dt.strptime(string, fmt).replace( tzinfo=tzinfo )
   return datetime

def str2ts( string, fmt, min_time = False, tzinfo=tz.utc ):
   """string -> timestamp"""
   datetime = str2dt( string, fmt )
   return dt2ts( datetime, min_time = min_time, tzinfo=tzinfo )

hhmm_str = lambda integer : str(integer).rjust(2, "0")

class clock_iter:
   """Iterator class; adds 10 mins to the iterated variable"""
   def __init__(self, start="0000"):
      self.hh = start[0:2]; self.mm = start[2:]; self.time = start
   def __iter__(self):
      return self
   def __next__(self):
      if self.time == "2350":
         self.hh = "00"; self.mm = "00"; self.time = "0000"
         return self.time
      else: #for all other times
         if self.mm == "50":
            self.hh = hhmm_str( int(self.hh)+1 )
            self.mm = "00"
            self.time = self.hh + self.mm
            return self.time
         else: #self.hh remains unchanged!
            self.mm = str( int(self.mm)+10 )
            self.time = self.hh + self.mm
            return self.time
