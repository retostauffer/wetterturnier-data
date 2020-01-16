# -------------------------------------------------------------------
# - NAME:        main.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-03
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-03, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2018-01-15 13:03 on prognose2
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# - Extracting bufr file
# -------------------------------------------------------------------
def extract_bufr_file(config,stint,file,verbose):

   from extractBUFRperl import extractBUFR

   obj = extractBUFR( file, config, stint, verbose )
   if obj.error:
      print("\nPROBLEMS READING THE BUFR FILE. RETURN\n")
      return None

   obj.extractdata()
   #print "----------------- dropped --------------------"
   obj.showdropped()
   #print "----------------- dropped --------------------"


   check = obj.manipulatedata()
   if check == None: return

   obj.showdata()

   # - Write data (observations) to database after preparation
   obj.prepare_data()
   print('       - file - %s' % file)
   obj.write_to_db()

   # - Now update stations database table
   obj.update_stations()
   
   obj.dbClose()

   return True


# -------------------------------------------------------------------
# - If started as main, searching bufr files
# -------------------------------------------------------------------
if __name__ == "__main__":

   import sys, os, socket
   os.environ['TZ'] = 'UTC'
   sys.path.append('PyModules3')

   import utils
   from readconfig import * 

   print('\n  * Welcome to the extractor script called %s' % os.path.basename(__file__))

   # ----------------------------------------------------------------
   # - Reading inputs. The only option is to explicitly set an
   #   input file. 
   # ----------------------------------------------------------------
   import getopt
   try:
      opts,args = getopt.getopt(sys.argv[1:],'f:v',['file=','verbose'])
   except Exception as e:
      print(e)
      sys.exit('Wrong input to this file.')
   manually = False
   verbose  = False
   files = None
   for o, a in opts:
      if o in ['-f','--file']:
         files = [a] 
         manually = True
      elif o in ['-v','--verbose']:
         verbose = True

   # ----------------------------------------------------------------
   # - Reading config file
   # ----------------------------------------------------------------
   configfile = '%s_config.conf' % socket.gethostname()
   if not os.path.isfile( configfile ):   configfile = 'config.conf' 
   print('    Reading config file: %s' % configfile)
   config = readconfig(configfile)
   config = readbufrconfig(config)

   # ----------------------------------------------------------------
   # - There can be different stints (e.g., additional and essential
   #   data). Processing them one by one 
   #   Input and output directory are/can be different, data will
   #   be labeled in the database.
   # ----------------------------------------------------------------
   for stint in config['stints']:

      print("\n  * Processing data stint %s" % stint)

      # -------------------------------------------------------------
      # - Checking files
      # -------------------------------------------------------------
      if not manually:
         import glob
         files = glob.glob('%s/*' % config['%s_indir' % stint])
      # - Number of files
      print('    Number of BUFR files found in %s (*.bin): %d' % \
               (config['%s_indir' % stint], len(files)))

      # -------------------------------------------------------------
      # - Extracting data
      # -------------------------------------------------------------
      for file in files:
         cx = extract_bufr_file(config,stint,file,verbose)

         if manually:
            print('    Manual -f/--file input. Do not move the files to %s' % \
                  config['%s_outdir' % stint])
         else:
            if not cx or cx == None:
               utils.movefile(config,stint,file,'bufr',False)
            else:
               utils.movefile(config,stint,file,'bufr',cx)


   # ----------------------------------------------------------------
   # - Compute derived variables
   # ----------------------------------------------------------------
   from derived3 import compute_derived
   print("\n  * Calling compute_derived from derived.py to compute")
   print("    derived variables like relative humidity if only")
   print("    temperature and dew point are given.")
   compute_derived( config )


   # ----------------------------------------------------------------
   # - End of the script 
   # ----------------------------------------------------------------
   print('\n  * All done, good night!\n')
