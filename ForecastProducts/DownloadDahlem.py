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
   os.environ['TZ'] = 'UTC' # Important, all dates/times in UTC
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
   ftp.download( dahlem )
   ftp.close()
