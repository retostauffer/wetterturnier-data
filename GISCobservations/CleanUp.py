# -------------------------------------------------------------------
# - NAME:        CleanUp.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-08-01
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-03, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2018-01-21 12:51 on prognose2
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# - If started as main, searching bufr files (TODO)
# -------------------------------------------------------------------
if __name__ == "__main__":

   import sys, os, socket
   os.environ['TZ'] = 'UTC'
   sys.path.append('PyModules3')

   import utils
   from readconfig import * 

   print('  * Welcome to the cleanup/archive script called %s' % os.path.basename(__file__))

   # ----------------------------------------------------------------
   # - Reading inputs. The only option is to explicitly set an
   #   input file. 
   # ----------------------------------------------------------------
   import getopt
   try:
      opts,args = getopt.getopt(sys.argv[1:],'v',['verbose'])
   except Exception as e:
      print(e)
      sys.exit('Wrong input to this file.')
   verbose  = False
   for o, a in opts:
      if o in ['-v','--verbose']: verbose = True

   # ----------------------------------------------------------------
   # - Reading config file
   # ----------------------------------------------------------------
   configfile = '%s_config.conf' % socket.gethostname()
   if not os.path.isfile( configfile ):   configfile = 'config.conf' 
   print('    Reading config file: %s' % configfile)
   config = readconfig(configfile)


   # ----------------------------------------------------------------
   # - Initialize cleanup.
   # ----------------------------------------------------------------
   from cleanup import cleanup 
   print("  * Initialize CleanUp")
   cleanup = cleanup( config )
   
   # - delete old files
   cleanup.delete_old_raw_files()

   # - Migrate old data to archive database
   cleanup.live_database_to_archive()

   # - Delete old observations from live table
   cleanup.cleanup_live_table()


   print("")
   print("  * CleanUp has done his jobs.")
   cleanup.closeDB()


