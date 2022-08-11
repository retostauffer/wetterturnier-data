# -------------------------------------------------------------------
# - NAME:        DWDOpendataDownload.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2017-07-31
# -------------------------------------------------------------------
# - DESCRIPTION: Downloading BUFR from dwd opendata ftp
# -------------------------------------------------------------------
# - EDITORIAL:   2017-07-31, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2018-01-15 13:40 on prognose2
# -------------------------------------------------------------------

#import sys
#sys.exit("Currently offline, seems ftp access changed aniways.")

if __name__ == "__main__":

   import ftplib
   import re, os, sys
   from datetime import datetime as dt

   os.environ["TZ"] = "UTC"
   
   ftp_server = "opendata.dwd.de"
   ftp_username = ""
   ftp_password = ""
   ftp_dirs     = ["weather/weather_reports/synoptic/germany/","weather/weather_reports/synoptic/international/"]

   
   outputdir = "incoming-essential"
   checkdir  = "data-processed/bufr/processed"
   
   # FTP listing
   for ftp_dir in ftp_dirs:
      ftp = ftplib.FTP( ftp_server )
      ftp.login( ftp_username, ftp_password )
      print(ftp_dir)
      ftp.cwd( ftp_dir )
      data = []
      ftp.dir(data.append)
      
      # Looping trough listing, search for a specific type of file
      # and download the data if not yet on disc.
      now = int(dt.now().strftime("%s"))
      for line in data:
         # Extract file name
         #mtch = re.match("^.*(Z__C_EDZW_[0-9]{14}_bda01,synop_bufr_GER_.*__MW_.*.bin)$",line)
         mtch = re.match("^.*(Z__C_.*.bin)$",line)
         if not mtch: continue
         filename = mtch.group(1)

         # Extracting time stamp from file name
         mtch = re.match("^.*_([0-9]{14})_.*$",filename)

         filedatetime = int(dt.strptime(mtch.group(1),"%Y%m%d%H%M%S").strftime("%s"))
         fileage      = now - filedatetime

         # File older than 24h: skip
         if fileage > 86400: continue
         if os.path.isfile( "{0:s}/{1:s}".format(outputdir,filename) ):
            #print "File exists on disc, skip"
            continue
         if os.path.isfile( "{0:s}/{1:s}".format(checkdir,filename) ):
            #print "File exists on disc, skip"
            continue
      
         # Downloading file
         print("Downloading {0:s}".format(filename))
         ftp.retrbinary('RETR %s' % filename, open("{0:s}/{1:s}".format(outputdir,filename),"wb").write )
      
   ftp.close()
