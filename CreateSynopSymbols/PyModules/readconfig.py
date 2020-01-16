# -------------------------------------------------------------------
# - NAME:        readconfig.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-12
# -------------------------------------------------------------------
# - DESCRIPTION: Reading config file
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-12, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-12-12 14:58 on pc24-c707
# -------------------------------------------------------------------

import logging
log = logging.getLogger(__name__)

class readconfig( object ):

   # ----------------------------------------------------------------
   # Init reads the config file
   # ----------------------------------------------------------------
   def __init__( self, file="config.conf" ):
      """!Init method initializing, automatically reading the config file.
      @return Return will be an object of class readconfig containing the
      infos from the config file."""

      import sys, os
   
      # Exit if file is not available at all
      if not os.path.isfile( file ):
         self.exit("Cannot find config file %s. Stop." % file)
   
      # Open new ConfigParser
      import configparser
      CNF = configparser.ConfigParser()   
      CNF.read(file)

      # -------------------------------------------------------------
      # Loading [mysql] section
      # -------------------------------------------------------------
      try:
         self.mysql_host      = CNF.get("mysql","host")
         self.mysql_username  = CNF.get("mysql","username")
         self.mysql_password  = CNF.get("mysql","password")
         self.mysql_database  = CNF.get("mysql","database")
         self.mysql_table     = CNF.get("mysql","table")
      except Exception as e:
         log.error(e)
         log.error("Problems while reading the [mysql] section in readconfig. Stop.")
         sys.exit(9) 

      # -------------------------------------------------------------
      # Loading [main] section
      # -------------------------------------------------------------
      try:
         self.outdir        = CNF.get("main","outdir")
         self.imagewidth    = CNF.getint("main","imagewidth")
         self.imageheight   = CNF.getint("main","imageheight")
         self.fontsize      = CNF.getint("main","fontsize")
         self.dpi           = CNF.getint("main","dpi")
         tmp                = CNF.get("main","stations")
      except Exception as e:
         log.error(e)
         log.error("Problems while reading the [main] section in readconfig. Stop.")
         sys.exit(9) 
      
      # Check existence of the directories
      if not os.path.isdir( self.outdir ):
         self.exit("\"outdir\"=\"%s\" does not exist as specified in %s" % (self.outdir,file))

      # Splitting stations
      self.stations = []
      for rec in tmp.split(","):
         try:
            stn = int(rec)
         except:
            self.exit("Cannot convert \"%s\" into integer. Stop. Error in station config." % rec)
         self.stations.append( stn )

      # -------------------------------------------------------------
      # Reading font specifications 
      # -------------------------------------------------------------
      self.fonts = {}
      if CNF.has_section("font specifications"):
         for rec in CNF.items("font specifications"):
            self.fonts[str(rec[0])] = {"font":str(rec[1]),"color":"black"}
            if not os.path.isfile( str(rec[1]) ):
               self.exit("Cannot finf file \"%s\"=\"%s\" as specified." % (rec))
               
      # -------------------------------------------------------------
      # Reading font colors 
      # -------------------------------------------------------------
      if CNF.has_section("font colors"):
         for rec in CNF.items("font colors"):
            if not str(rec[0]) in self.fonts.keys(): next
            self.fonts[str(rec[0])]['color'] = str(rec[1])




   # ----------------------------------------------------------------
   # Simple exit handler
   # ----------------------------------------------------------------
   def exit(self,msg,level=9):
      log.error( msg )
      import sys; sys.exit(level)







