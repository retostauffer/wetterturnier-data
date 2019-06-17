# -------------------------------------------------------------------
# - NAME:        DWDOpendataDownload.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2017-07-31
# -------------------------------------------------------------------
# - DESCRIPTION: Downloading BUFR from dwd opendata ftp
# -------------------------------------------------------------------
# - EDITORIAL:   2017-07-31, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-06-08 22:13 on prognose2
# -------------------------------------------------------------------

if __name__ == "__main__":

   import ftplib
   #from ftplib import FTP_TLS
   import re, os, sys, socket
   from datetime import datetime as dt

   os.environ['TZ'] = 'UTC'
   sys.path.append('PyModules')

   import utils
   from readconfig import *

   print '\n  * Welcome to the extractor script called %s' % os.path.basename(__file__)

   # ----------------------------------------------------------------
   # - Reading config file
   # ----------------------------------------------------------------
   configfile = 'config.conf'
   #configfile = '%s_config.conf' % socket.gethostname()
   #if not os.path.isfile( configfile ):   configfile = 'config.conf'
   print '    Reading config file: %s' % configfile
   config = readconfig(configfile)
   config = readbufrconfig(config)

   # No valid config? Stop.
   if not config["dwd_ftp"]:
      sys.exit("No valid dwd_ftp config from config file. Stop  here.")

   # FTP listing
   print "  * Establishing ftp connection"
   ftp = ftplib.FTP( config["dwd_ftp"]["host"] )
   #ftp = FTP_TLS( config["dwd_ftp"]["host"] )
   
   ftp.login( config["dwd_ftp"]["user"], config["dwd_ftp"]["passwd"] )
   ftp.cwd( config["dwd_ftp"]["dir"] )
   data = []
   print "    Reading ftp file listing"
   ftp.dir(data.append)

   # Specify where to store and check the files
   outputdir = config["additional_indir"]
   checkdir  = config["additional_outdir"] + "/bufr/processed"

   # Looping trough listing, search for a specific type of file
   # and download the data if not yet on disc.
   print "    Check for matching files"
   now = int(dt.now().strftime("%s"))
   pattern = "(\w{3}\s+\d+\s+\d+:\d+)\s+" + "({0:s})".format(config["dwd_ftp"]["files"])
   for line in data:
      # Extract file name
      mtch = re.findall( pattern, line )

      # Ignore file if they do not match the pattern
      if not mtch: continue

      # Else check whether we have to download the file
      filename = mtch[0][1]

      if os.path.isfile( "{0:s}/{1:s}".format(outputdir,filename) ) or \
         os.path.isfile( "{0:s}/{1:s}".format(checkdir,filename) ):
         #print "File exists on disc, skip"
         continue

      # Downloading file
      print "Downloading {0:s}".format(filename)
      ftp.retrbinary('RETR %s' % filename, open("{0:s}/{1:s}".format(outputdir,filename),"wb").write )
   
   print "    Close ftp connection ..."
   ftp.quit()

   print "  * All done ..."
