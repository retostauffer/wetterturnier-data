# -------------------------------------------------------------------
# - NAME:        derived.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-03
# -------------------------------------------------------------------
# - DESCRIPTION: Compute derived values like relative humidity
#                if only dew point temperature is available.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-03, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-08-01 14:47 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# - Has to be a function as I am also using this function from
#   bufr.py. However, as also called by the __main__ script this
#   python script can be run standallone.
# -------------------------------------------------------------------
def compute_derived(config):

   # ----------------------------------------------------------------
   # - Establishing database connection
   # ----------------------------------------------------------------
   from derivedvars import derivedvars
   obj = derivedvars(config)

   nhours = 100 # how long to go back in time

   # ----------------------------------------------------------------
   # - Compute rh from (t,td), compute td from (t,rh)
   # ----------------------------------------------------------------
   obj.compute_rh_from_td(nhours)
   obj.compute_td_from_rh(nhours)

   # ----------------------------------------------------------------
   # - Closes database 
   # ----------------------------------------------------------------
   obj.close()


# -------------------------------------------------------------------
# - If started as main
# -------------------------------------------------------------------
if __name__ == "__main__":

   import sys, os
   import socket
   # - On prognose server: change working dir
   if socket.gethostname() == "prognose2.met.fu-berlin.de":
      os.chdir('/home/imgi/gisc-mail')
   os.environ['TZ'] = 'UTC'
   sys.path.append('PyModules')

   import utils
   from readconfig import * 

   print '  * Welcome to the derived vars calculus script called %s' % os.path.basename(__file__)

   # ----------------------------------------------------------------
   # - Reading inputs. The only option is to explicitly set an
   #   input file. 
   # ----------------------------------------------------------------
   import getopt
   try:
      opts,args = getopt.getopt(sys.argv[1:],'v',['verbose'])
   except Exception as e:
      print e
      sys.exit('Wrong input to this file.')
   verbose  = False
   for o, a in opts:
      if o in ['-v','--verbose']: verbose = True

   # ----------------------------------------------------------------
   # - Reading config file
   # ----------------------------------------------------------------
   configfile = '%s_config.conf' % socket.gethostname()
   if not os.path.isfile( configfile ):   configfile = 'config.conf' 
   print '    Reading config file: %s' % configfile
   config = readconfig(configfile)

   compute_derived(config)

   print '\n  * All done, good night!\n'

