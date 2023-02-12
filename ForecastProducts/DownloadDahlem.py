# -------------------------------------------------------------------
# - NAME:        DownloadAll.py 
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-17
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-17, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-06-11 23:07 on thinkreto
# -------------------------------------------------------------------

# - Logger settings
import logging, logging.config
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)



# -------------------------------------------------------------------
# Main script
# -------------------------------------------------------------------
if __name__ == "__main__":

   import sys, os
   os.environ['TZ'] = 'UTC' # Important, all dates/times in UTC
   sys.path.append('PyModules')

   # Import readconfig class
   from readconfig import readconfig
   # Import forecastmaps class
   from handler import handler

   # Reading the config(s)
   config = readconfig("config.conf") 

   import datetime 
   import numpy as np
   # Take latest full 6h
   # ROUND to last full 6h interval to be sure that we (i) only
   # process 00/06/12/18 UTC AND to be sure that the minute is
   # exactly 00 as well.
   current_timestamp = np.floor(int(datetime.datetime.now().strftime("%s")) / 21600) * 21600
   current_timestamp = datetime.datetime.fromtimestamp( current_timestamp )

   # Looping backwars over the last 12 hours.
   # Therefore we do not depend on when the images will be on the
   # ftp server. The handler itself automatically notices when a
   # figure was already processed.
   for lag in [-2,-1,0]: 

      # Compute 'loop timestamp'
      date_time = current_timestamp + datetime.timedelta(0,lag*21600) 

      print("\n\n")
      log.info("Processing date/time:    %s" % date_time.strftime("%Y-%m-%d %H:%M"))

      # Initialize the overall handler class
      obj = handler(config,date_time)

      # Looping over all forecastmaps 
      for rec in config.products:
         original_file = rec['original_file']
         products = rec['products']

         obj.getImages( rec )

      obj.close()



   # ----------------------------------------------------------------
   # Delete old files older than X days (see config file)
   # ----------------------------------------------------------------
   print("\n")
   log.info("Delete old files now ...") 

   # Delete files from originals directory
   cmd = "find %s -type f -mtime +%d -exec rm {} \\;" % (config.originals,config.delete_images)
   log.info("  - From originals directory, calling:")
   log.info("    %s" % cmd)
   os.system(cmd)

   # Delete files from images directory
   cmd = "find %s -type f -mtime +%d -exec rm {} \\;" % (config.meteogramsdir,config.delete_images)
   log.info("  - From meteograms directory, calling:")
   log.info("    %s" % cmd)
   os.system(cmd)

   # Delete files from images directory
   cmd = "find %s -type f -mtime +%d -exec rm {} \\;" % (config.imagedir,config.delete_images)
   log.info("  - From image directory, calling:")
   log.info("    %s" % cmd)
   os.system(cmd)

   # Delete lockbits
   cmd = "find %s -type f -mtime +%d -exec rm {} \\;" % (config.lockbitdir,config.delete_lockbits)
   log.info("  - From lockbit directory, calling:")
   log.info("    %s" % cmd)
   os.system(cmd)














