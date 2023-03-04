# -------------------------------------------------------------------
# - NAME:        ftphandler.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-18
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-18, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2016-01-05 12:00 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------

import logging, logging.config
log = logging.getLogger(__name__)

class ftphandler( object ):

   ftp    = None
   config = None

   # ----------------------------------------------------------------
   # Initialization
   # ----------------------------------------------------------------
   def __init__( self, config ):
      """!ftphandler is an own small class handling the ftp connection
      and data transfer.
      @param config. Readconfig class object (@see readconfig.readconfig)
      @return No return, initializes a ftphandler object."""

      # Save config object
      self.config = config


   # ----------------------------------------------------------------
   # Open ftp connection
   # ----------------------------------------------------------------
   def _ftp_connect_( self ):
      """!Opens the ftp connection, saves connection handler on self.ftp."""

      import ftplib
      log.info("Login to ftp server now")
      self.ftp = ftplib.FTP( self.config.ftp_server )
      self.ftp.login( self.config.ftp_user, self.config.ftp_password )
      self.ftp.cwd(self.config.ftp_directory)



   # ----------------------------------------------------------------
   # Loading file list (ls) from ftp
   # ----------------------------------------------------------------
   def getFilelist( self, hash ):
      """!Retreiving file list from the ftp. Only from the directory
      specified in your config.conf file (open ftp connection already
      changed to this directory).
      @param hash. File identifier, wildcards allowed.
      @return Returns a list with the file listing."""

      # If ftp connection not established, open
      if not self.ftp: self._ftp_connect_()
      # Reading listing
      log.info("  Loading file list from FTP matching:")
      log.info("  - %s" % hash)
      raw = []
      try:
         self.ftp.retrlines("LIST %s" % hash, callback=raw.append)
      except:
         log.debug("Cannot find file matching the search string.")

      # Extractinf file-name only
      files = []
      for rec in raw: files.append( rec.split()[-1] )
      log.info("  - Found %d files matching the search hash" % len(files))
      return files


   # ----------------------------------------------------------------
   # Just download the raw file
   # ----------------------------------------------------------------
   def download( self, filename, outpath ):
      """Downloads the given file and saves it on disk.
      @param filename. Name of the file. Can include wildcards,
         but if not exactly one file matches the string, the
         method will return False instead of the filename.
      @return Returns the name of the downloaded file if succesful.
         If the download failed it returns False."""
      
      filename_split = filename.rsplit( '/', 1 )
      # get the path location
      path = filename_split[0]
      # removing the path to get just the filename
      filename  = filename_split[1]
      # path to which we download the file 
      outfile = outpath + "/" + filename
      print("outfile:", outfile)

      # If ftp connection not established, open
      if not self.ftp: self._ftp_connect_()
      # Change directory to filepath
      self.ftp.cwd( "/" + path )

      # Downloading the file
      try:
         self.ftp.retrbinary(f"RETR {filename}" , open( outfile, 'wb').write )
      # To avoid all possible errors.
      except:
         print("ERROR! Could not download file:")
         print(filename)
         return False
      
      return outfile

   # ----------------------------------------------------------------
   # Loading image from ftp (into temporary file)
   # ----------------------------------------------------------------
   def getImage( self, filename ):
      """!Loading an image from the ftp server given a file name.
      If there are more than two files matching the file name (if
      wildcard is included or so), the method will return False.
      If there is no file matching your file name, the method
      will return False as well.
      Else the image will be downloaded and saved on a spooled
      temporary file (in memory). The return value will be the
      temporary file name handler.
      @param filename. Name of the file. Can include wildcards,
         but if not exactly one file matches the string, the
         method will return False instead of an image.
      @return Returns a file handler on a spooled temporary
         file object if succesfully downloaded, else False."""

      import tempfile
      from PIL import Image
      log.info("Loading file from ftp server %s:" % (self.config.ftp_server))
      log.info("  %s" % filename)

      # If ftp connection not established, open
      if not self.ftp: self._ftp_connect_()
      # Create new temporary file
      tmpfile = tempfile.SpooledTemporaryFile()
      # Downloading the image
      try:
         self.ftp.retrbinary("RETR %s" % filename , tmpfile.write )
      except EOFError:
         print("EOF (end of file) error! Could not download file:")
         print(filename)
         return False

      # Reading the image
      img = Image.open( tmpfile )
      return img


   # ----------------------------------------------------------------
   # Close ftp connection
   # ----------------------------------------------------------------
   def close( self ):
      if self.ftp:
         log.info("Close ftp connection now")
         self.ftp.close()
