# -------------------------------------------------------------------
# - NAME:        readconfig.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2015-02-04
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2018-01-15 12:17 on prognose2
# -------------------------------------------------------------------



def readconfig( file = 'config.conf' ):

   import sys, os
   if not os.path.isfile( file ): sys.exit("ERROR: readconfig cannot find file %s" % file)
   # - Else parse important data
   from configparser import ConfigParser
   CNF = ConfigParser()
   CNF.read( file )
   config = {}

   # ----------------------------------------------------------------
   # - Necessary directory settings
   #   indir: input directory where the bufr/synop messages are.
   #   outdir: output where we are moving the data to
   #   we need these two.
   # ----------------------------------------------------------------
   # - Try to read sortorder if available
   try:
      tmp                        = CNF.get('settings','sortorder')
      config['sortorder'] = []
      for rec in tmp.split(','): config['sortorder'].append(rec.strip().lower())
   except:
      config['sortorder'] = False
   # - Skip columns in showdata
   try:
      tmp                        = CNF.get('settings','showskip')
      config['showskip'] = []
      for rec in tmp.split(','): config['showskip'].append(rec.strip().lower())
   except:
      config['showskip'] = [] 
   # - Skip columns while writing to database 
   try:
      tmp                        = CNF.get('settings','dbskip')
      config['dbskip'] = []
      for rec in tmp.split(','): config['dbskip'].append(rec.strip().lower())
   except:
      config['dbskip'] = [] 

   # ----------------------------------------------------------------
   # The different file classes/different I/O
   # ----------------------------------------------------------------
   import re
   config['stints'] = []
   for section in CNF.sections():
      if not re.match(r"^(settings)(\s)(.?)",section): continue
      stint = section.split()[1]
      config['stints'].append( stint )
      print("    Found section/data type: %s (stint name)" % stint)
      try:
         config['%s_indir'  % stint] = CNF.get('settings %s' % stint,'indir')
         config['%s_outdir' % stint] = CNF.get('settings %s' % stint,'outdir')
      except Exception as e:
         print(e)
         sys.exit('Problems in config file. indir/outdir not set propperly.')
      # - Check if these exist
      if not os.path.isdir( config['%s_indir' % stint] ):
         sys.exit('Cannot find directory %s. Stop.' % config['%s_indir'  % stint])
      if not os.path.isdir( config['%s_outdir' % stint] ):
         sys.exit('Cannot find directory %s. Stop.' % config['%s_outdir' % stint])
   if len(config['stints']) == 0:
      sys.exit("Problems with configuration. Need at least one [settings stint] section " + \
               "where 'stint' is the name of the constraint of the data. At the moment: " + \
               "essential (data can be published for free as everyone can download these " + \
               "data anyway) and additional (additional licence necessary).")


   # ----------------------------------------------------------------
   # - Getting mysql config
   # ----------------------------------------------------------------
   try:
      config['mysql_host']          = CNF.get('mysql','host')
      config['mysql_user']          = CNF.get('mysql','user')
      config['mysql_passwd']        = CNF.get('mysql','passwd')
      config['mysql_database']      = CNF.get('mysql','database')
      config['wp_database']         = CNF.get('mysql','wp_database')
   except Exception as e:
      print(e)
      sys.exit("ERROR: readconfig problems reading mysql settings")


   # ----------------------------------------------------------------
   # - Getting dwd ftp config. Ignore if not specified properly.
   # ----------------------------------------------------------------
   try:
      config['dwd_ftp'] = {"host":     CNF.get('dwd ftp','host'),
                           "user":     CNF.get('dwd ftp','user'),
                           "passwd":   CNF.get('dwd ftp','passwd'),
                           "files":    CNF.get('dwd ftp','files'),
                           "dir":      CNF.get('dwd ftp','dir') }
   except Exception as e:
      print("[!] No valid dwd_ftp specification. Return None here.")
      config['dwd_ftp'] = None


   # ----------------------------------------------------------------
   # - Reading mysql table config files for synop messages
   # ----------------------------------------------------------------
   try:
      config['mysql_synop_tablename'] = CNF.get('mysql synop','tablename')
      config['mysql_synop_create']    = CNF.get('mysql synop','create')
      config['mysql_synop_columns']   = CNF.get('mysql synop','columns')
   except Exception as e:
      print(e)
      sys.exit('Problems with the [mysql synop] configuration in config file.')
   # - If these do not exist, stop
   if not os.path.isfile( config['mysql_synop_create'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql synop] create.' % \
               config['mysql_synop_create'])
   if not os.path.isfile( config['mysql_synop_columns'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql synop] columns.' % \
               config['mysql_synop_columns'])

   # ----------------------------------------------------------------
   # - Reading mysql table config files for bufr messages
   # ----------------------------------------------------------------
   try:
      config['mysql_bufr_tablename'] = CNF.get('mysql bufr','tablename')
      config['mysql_bufr_create']    = CNF.get('mysql bufr','create')
      config['mysql_bufr_columns']   = CNF.get('mysql bufr','columns')
   except Exception as e:
      print(e)
      sys.exit('Problems with the [mysql bufr] configuration in config file.')
   # - If these do not exist, stop
   if not os.path.isfile( config['mysql_bufr_create'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql bufr] create.' % \
               config['mysql_bufr_create'])
   if not os.path.isfile( config['mysql_bufr_columns'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql bufr] columns.' % \
               config['mysql_bufr_columns'])


   # ----------------------------------------------------------------
   # - Reading mysql table config files for bufr descriptions
   # ----------------------------------------------------------------
   try:
      config['mysql_bufrdesc_create']  = CNF.get('mysql bufrdesc','create')
   except Exception as e:
      print(e)
      sys.exit('Problems with the [mysql bufrdesc] configuration in config file.')
   # - If these do not exist, stop
   if not os.path.isfile( config['mysql_bufrdesc_create'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql bufrdesc] create.' % \
               config['mysql_bufrdesc_create'])

   # ----------------------------------------------------------------
   # - Reading mysql table config files for stations messages
   # ----------------------------------------------------------------
   try:
      config['mysql_stations_create']  = CNF.get('mysql stations','create')
   except Exception as e:
      print(e)
      sys.exit('Problems with the [mysql stations] configuration in config file.')
   # - If these do not exist, stop
   if not os.path.isfile( config['mysql_stations_create'] ):
      sys.exit('Missing \"%s\" as defined in the config [mysql stations] create.' % \
               config['mysql_stations_create'])


   # ----------------------------------------------------------------
   # - Read config parameters for the cleanup 
   # ----------------------------------------------------------------
   try:
      config['cleanup_srctable']  = CNF.get('cleanup','srctable');
   except Exception as e:
      config['cleanup_srctable']  = None # in this case: do not move obs into archive
   try:
      config['cleanup_dsttable']  = CNF.get('cleanup','dsttable');
   except Exception as e:
      config['cleanup_dsttable']  = None # in this case: do not move obs into archive
   # - Delete live database entries after X days
   try:
      config['cleanup_db_days'] = CNF.getint('cleanup','db_days');
   except:
      config['cleanup_db_days'] = 7
   # - Delete files from data-processed
   try:
      config['cleanup_file_days'] = CNF.getint('cleanup','file_days');
   except:
      config['cleanup_file_days'] = 2
   # - File postfixes which we should delete 
   try:
      config['cleanup_file_endings'] = []
      tmp = CNF.get('cleanup','file_endings')
      for rec in tmp.split(','):
         config['cleanup_file_endings'].append( rec.strip().lower() )
   except:
      sys.exit("[!] ERROR: misconfiguration in config file, cleanup file_endings list")
   # - Which stations should be migrated into the archive table
   try:
      from database import database
      wpdb = database(config, database="wp")
      config['cleanup_stations'] = wpdb.get_stations()
   except:
      sys.exit("[!] ERROR: cannot access wordpress database")


   return config



# -------------------------------------------------------------------
# - Reading bufr config. If input is a dict object (e.g., config)
#   we are appending all the new elements to this dict!
# -------------------------------------------------------------------
def readbufrconfig( input = None, file = 'bufr_config.conf' ):

   import sys, os
   from paramclass import paramclass
   if not os.path.isfile( file ):
      sys.exit("ERROR: readbufrconfig cannot find file %s" % file)
   # - Else parse important data
   from configparser import ConfigParser
   CNF = ConfigParser()
   CNF.read( file )
   config = {}

   # - Getting all parameters. [parameter t] means that this value
   #   will be stored in the database in column "t". We also need
   #   a search string corresponding to the key name of the BUFR
   #   file and some scaling if needed.
   config["parameter"] = []
   for sec in CNF.sections():
      if not sec[:10] == "parameter ": continue
      # - Else found section, extract parameter name
      paramname = sec[10:].strip()
      try:
         search = CNF.get(sec,'search')
      except Exception as e:
         print(e)
         sys.exit("ERROR: config file section [%s] not well defined (search string missing)" % sec)
      # - Loading bufrid from config. If bufrid
      #   is set (integer) bufrid will be used
      #   instead of 'search'. 'search' is not
      #   a good indicator.
      try:
         bufrid = CNF.getint(sec,'bufrid')
      except:
         bufrid = False
      # - Offset, scaling factor, and period if set
      try:
         offset = CNF.getfloat(sec,'offset')
      except:
         offset = False
      try:
         factor = CNF.getfloat(sec,'factor')
      except:
         factor = False
      try:
         repeat = CNF.getboolean(sec,'repeat')
      except:
         repeat = False
      try:
         period = CNF.get(sec,'period')
      except:
         period = False
      try:
         sensorheight = CNF.getfloat(sec,'height')
      except:
         sensorheight = False
      try:
         verticalsign = CNF.getint(sec,'verticalsign')
      except:
         verticalsign = False
      # - Append
      config['parameter'].append( paramclass(paramname,search,bufrid,offset, \
                                             factor,period,sensorheight,verticalsign,repeat) )

   for p in config['parameter']:
      print(p.show())

   # - appending
   if type(input) == type(dict()):
      for k in list(input.keys()):
         config[k] = input[k]

   return config

