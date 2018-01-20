# -------------------------------------------------------------------
# - NAME:        readconfig.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-18
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-18, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-06-11 22:53 on thinkreto
# -------------------------------------------------------------------

import logging, logging.config
log = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Reading the config file first
# -------------------------------------------------------------------
class readconfig( object ):

   def __init__( self, file ):
      import sys, os, re
      from ConfigParser import ConfigParser
      if not os.path.isfile(file):
         log.error("Cannot find config file: %s",file); sys.exit(9)

      self.file = file

      # Open config file
      CNF = ConfigParser()
      CNF.read(file)

      # -------------------------------------------------------------
      # Parsing input options
      # -------------------------------------------------------------
      from optparse import OptionParser
      usage = """usage: %prog [options]
      This script allows for some inputs. If nothing is set, all
      products will be run (and downloaded if available).

      The --type can be specified to run only a specific type of
      defined procuts. In the config file there can be several
      sections [products XXXX] where XXXX defines the type.
      - %prog --typ analysis
      - %prog --typ forecass

      """
      parser = OptionParser(usage=usage)

      # Strings
      parser.add_option('--type',         dest='type',        default=None,
                        help='The product type to be processed, see config file.')


      # Parsing inputs and save onto object
      (opts,args) = parser.parse_args()
      # Save inputs onto self.inputs
      self.inputs = opts


      # -------------------------------------------------------------
      # Reading ftp section
      # -------------------------------------------------------------
      try:
         self.ftp_server    = CNF.get("ftp","server")
         self.ftp_user      = CNF.get("ftp","user")
         self.ftp_password  = CNF.get("ftp","password")
         self.ftp_directory = CNF.get("ftp","directory")
      except Exception as e:
         log.error(e)
         self.exit("Problems reading the [ftp] section in %s" % file)
         
      # -------------------------------------------------------------
      # Reading main config, doing some checks afterwards. 
      # -------------------------------------------------------------
      try:
         self.productconfig   = CNF.get("main","productconfig")
         self.imagedir        = CNF.get("main","imagedir")
         self.meteogramsdir   = CNF.get("main","meteogramsdir")
         self.lockbitdir      = CNF.get("main","lockbitdir")
         self.originals       = CNF.get("main","originals")
         self.delete_images   = CNF.getint("main","delete_images")
         self.delete_lockbits = CNF.getint("main","delete_lockbits")
         self.store_originals = CNF.getboolean("main","store_originals")
      except Exception as e:
         log.error(e)
         self.exit("Problems reading the [main] section of %s." % file)

      try:
         self.devel        = CNF.getboolean("main","devel")
      except:
         self.devel        = False

      if not os.path.isdir( self.productconfig ):
         self.exit("Cannot find directory productconfig = \"%s\" as specified." % self.productconfig)
      if not os.path.isdir( self.meteogramsdir ):
         self.exit("Cannot find directory meteogramsdir = \"%s\" as specified." % self.meteogramsdir)
      if not os.path.isdir( self.imagedir ):
         os.mkdir( self.imagedir )
      if not os.path.isdir( self.lockbitdir ):
         os.mkdir( self.lockbitdir )
      if not os.path.isdir( self.originals ):
         os.mkdir( self.originals )


      # -------------------------------------------------------------
      # Reading forecastmaps product config section
      # -------------------------------------------------------------
      all_sections = CNF.sections()
      self.product_files = []

      # Looping over all sections
      for section in all_sections:
         # No products specification section? Skip.
         if not re.match("^products",section): continue

         # If user input type is set: only parse section if
         # it matches the user input on --type
         if self.inputs.type is not None:
            if not re.match("^products.*%s$" % self.inputs.type,section): continue

         # Extracting product type specification from [product xxxxx]
         type = re.match("^products\ ([a-zA-Z]{1,})$",section).group(1)

         log.info("Parsing section [%s] from config file %s" % (section,file))
         user_configs = CNF.items(section)
         for rec in user_configs:
            # If set to false: skip
            if not CNF.getboolean(section,rec[0]): continue
            # Else append to the list
            self.product_files.append( [type,"%s.conf" % rec[0]] )


      # Reading the forecast maps product files
      self.products = []
      for rec in self.product_files:
         tmp = self._ReadProductConfig_( rec[0], rec[1] )
         if tmp is None: continue
         self.products.append( tmp ) 

      # Stop if no products found
      if len(self.products) == 0:
         self.exit("Sorry, no products found. Wrong input type?")
      else:
         log.info("Found %d different products to process" % len(self.products)) 


   # ----------------------------------------------------------------
   # Processing a config file
   # ----------------------------------------------------------------
   def _ReadProductConfig_( self, type, file ):

      import sys, os
      file = os.path.join(self.productconfig,file)
      if not os.path.isfile( file ): 
         log.error("Cannot find defined file %s. SKIP THIS." % file)
         return None

      # Reading Products
      from datetime import datetime as dt
      today = dt.now().strftime("%Y%m%d")

      # Reading the config file
      from ConfigParser import ConfigParser
      CNF = ConfigParser(); CNF.read( file )

      # Save images into sub-directories based on the name of
      # the config file. "cosmoeu_xxxx_xxxx.conf" will store its
      # outputs into a folder called 'cosmoeu'.
      # ONLY USED FOR forecast maps. not for [product meteograms]
      # products as they will be stored in a different directory.
      subdirectory = os.path.basename(file).split("_")[0].lower()

      # Reading main section
      try:
         original_file = CNF.get("main","original_file")
         nrows         = CNF.getint("main","nrows")
         ncols         = CNF.getint("main","ncols")
      except Exception as e:
         log.error(e); self.exit("Problems reading [main] section from %s" % file)

      # If product config of type 'meteograms': reading lastrun entry if set.
      # Default (for all other products as well) is None
      lastrunfile = None
      if type == 'meteograms':
         try:
            lastrunfile = CNF.get("main","lastrunfile")
         except:
            lastrunfile = None

      # If a rotation is set: read rotation
      try:
         rotation = CNF.getint("main","rotation")
      except:
         rotation = None

      # Looping over all sections (except main)
      sections = CNF.sections()
      products = {}
      for section in sections:

         # Reading all image section entries
         if section == "main": continue

         # Getting section config
         products[section] = {}
         # For cropping ALL 4 have to be specified. If one missing,
         # cropping all 4 values will be set to None: no crop will take place 
         try:
            products[section]['row']       = CNF.getint(section,'row')
            products[section]['col']       = CNF.getint(section,'col')
         except Exception as e:
            log.error(e)
            self.exit("Wrong specification in file %s section [%s]" % (file,section))

         # Reading resize. If both are not available: both will be set to None
         # with means that we do not have to resize the image at the end.
         # If both are set, these will be used (but depending on specification,
         # the aspect of the image can be modified). If only one is given, the other
         # one will be computed dynamically. Keeps aspect, output image size depends
         # on original file size or cropping selection.
         try:
            products[section]['resize_x'] = CNF.getint(section,'resize_x')
         except:
            products[section]['resize_x'] = None
         try:
            products[section]['resize_y'] = CNF.getint(section,'resize_y')
         except:
            products[section]['resize_y'] = None
         
      return {"original_file":original_file,"nrows":nrows,"ncols":ncols, \
              "type":type,"lastrunfile":lastrunfile,"subdirectory":subdirectory, \
              "rotation":rotation,"products":products}               


   # Small exit routine
   def exit( self, msg, errorcode = 9 ):
      log.error(msg)
      import sys; sys.exit(errorcode)



