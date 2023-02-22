# -------------------------------------------------------------------
# - NAME:        DownloadDahlem.py 
# - AUTHOR:      Juri Hubrig
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
   os.environ['TZ'] = 'MET' # Important, all dates/times in MET
   sys.path.append('PyModules')
   
   # Import readconfig class
   from readconfig import readconfig
   # Import ftphandler class
   from ftphandler import ftphandler
   
   # Reading the config(s)
   config = readconfig("config.conf") 
   
   dahlem = config.ftp_dahlem
   
   ftp = ftphandler( config )
   
   print(f"Download file '{dahlem}'")
   ftp.download( dahlem, "dahlem" )
   ftp.close()
   
   # Now we count the number of lines in the file. If it is 64 or more, we consider the day as finished.
   # If all observations for this day are in, we copy the file to "dahlem/hwerte_YYYYMMDD.txt (date of yesterday).
   
   hwerte = "dahlem/hwerte_"
   
   with open( dahlem, "r", encoding="ISO-8859-1" ) as fp:
      
      lines = len(fp.readlines())
      if lines >= 64:
         
         from shutil import copy2
         from datetime import date, timedelta
         
         day = date.today().strftime("%Y%m%d")
         copy2( hwerte + "neu.txt", hwerte + "{day}.txt" )
