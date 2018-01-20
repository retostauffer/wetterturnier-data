# -------------------------------------------------------------------
# - NAME:        bo.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-12
# -------------------------------------------------------------------
# - DESCRIPTION: Using bodenkarten fonts to draw synop images.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-12, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-06-20 10:35 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


# - Logger settings
import logging, logging.config
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

if __name__ == "__main__":

   import sys, os
   os.environ['TZ'] = 'UTC'
   sys.path.append("PyModules")

   import matplotlib
   matplotlib.use("Agg")

   from database import database
   from synopsymbol import synopsymbol
   from readconfig import readconfig

   config = readconfig("config.conf")

   db  = database(config)

   from datetime import datetime as dt
   import numpy as np

   # Gives full last hour
   now_timestamp = int(np.floor(float(dt.now().strftime("%s"))/3600)*3600)

   # If tmax > 0 the thing will perform the creation of SynopSymbols
   # tmax hours backwards in time. For recreation. Default is 0, only
   # the latest hour will be visualized.
   tmax = 10
   for t in range(0, tmax+1):

      # Note: the (tmax-t) is required as - if reproducing figures - the
      # newest one should be created at the end, else the "current" figures
      # will be of an old date/time.
      time = dt.fromtimestamp( now_timestamp - (tmax-t)*3600 )
      for station in config.stations:
   
         # If file is already existing: skip
         filename = "synop_%s_%d.png" % (time.strftime("%Y%m%d_%H%M"),station)
         if os.path.isfile( os.path.join(config.outdir,filename) ) and tmax == 0:
            log.info("Image %s/%s is existing, skip this one" % (config.outdir,filename))
            continue
      
         # Else loading data
         data = db.loadData(station,time)
         if data is None:
            log.warning("No data for station %d: skip this one ..." % station)
            continue
   
         # Initialize synop symbol 
         synop = synopsymbol(config)
         synop.addValue("day", int(time.strftime("%d")) )
         synop.addValue("hour",int(time.strftime("%H")) )
         for key,val in data.iteritems():
            if not type(val) in [type(int()),type(float())]: continue
            synop.addValue( key,val ) ## FF IN METERS PER SECOND PLEASE
   
         synop.showValues()
   
         synop.drawSymbol(filename)


   db.dbClose()


   # Delete old images from the output directory
   log.info("Remove all images \"synop_*.png\" older than 2 days from %s" % config.outdir)
   cmd = "find %s -type f -name 'synop_*.png' -mtime +2 -exec rm {} \\;" % config.outdir
   os.system( cmd )












