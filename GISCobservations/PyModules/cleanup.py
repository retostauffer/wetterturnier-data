# -------------------------------------------------------------------
# - NAME:        cleanup.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2015-08-01
# -------------------------------------------------------------------
# - DESCRIPTION: A class handling the cleanup process.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-08-01, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-12-12 13:13 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


# - New class
class cleanup(object):

   # - Initialize the object
   def __init__( self, config ):

      print "    Cleanup class initialized"
      self.config = config

      from database import database
      print "    Open database connection"
      self.db = database(config)

   # ----------------------------------------------------------------
   # - Delete old files on disc
   # ----------------------------------------------------------------
   def delete_old_raw_files( self ):
      """
      Method deleting files from disc in the directory 'outdir' as
      defined in the config.conf file. We do NOT decide between
      synop/bufr or processed/error here. Just kill them if they
      are older than 'file_days' as specified in config.conf.
      """

      import os, sys, time
      from datetime import datetime as dt
      import numpy as np

      for dir in [self.config['essential_outdir'],self.config['additional_outdir']]:

         days    = self.config['cleanup_file_days']
         postfix = self.config['cleanup_file_endings']
         maxage  = np.floor(time.time() / 86400)*86400 - days*86400

         print ""
         print "  - Searching for old files in \"%s\" older than about %d days" % (dir,days)
         print "    Or exactly: files older than %s" % dt.fromtimestamp( maxage ) 
         files = self.getOldFiles(dir,maxage,postfix)

         # - No old files? Pff
         if len(files) == 0:
            print "    No old files found. Skip this method. Done."
            return True

         # - Else delete these files
         print "    Found %d old files on disc" % len(files)

         # - Delete em all
         for file in files:
            #eprint file
            os.remove( file )

         print "    Old files removed from %s. Done." % dir

   # ----------------------------------------------------------------
   # - Helper function loading old files
   # ----------------------------------------------------------------
   def getOldFiles(self, dirPath, maxage, postfix): 
       """
       return a list of all files under dirPath older than days 
       """
       import sys, os, time, glob
       present = time.time()
       oldfiles = []
       for root, dirs, files in os.walk(dirPath, topdown=False):
           for name in dirs:
               subDirPath = os.path.join(root, name)
               for file in glob.glob("%s/*" % (subDirPath)):
                  # Checking file ending
                  tmp = file.split(".")[-1].lower()
                  if not tmp in postfix: continue
                  filePath = os.path.join(root,name,file)
                  if os.path.getmtime(filePath) < maxage:
                      oldfiles.append(filePath)

       return oldfiles






   # ----------------------------------------------------------------
   # - Cleaning up the database
   # ----------------------------------------------------------------
   def live_database_to_archive(self):
      """
      I would like to store some observation data longer than just
      a few days - however - we wont create a copy of the WMO
      observation data archive or simething. Therefore we are just
      archiving some stations as defined in 'cleanup:stations' in
      the config.conf file. Move them from 'cleanup:srctable' to
      'cleanup:dsttable' (see config.conf file).
      """

      print ""
      print "  - Migrate \"live\" database to \"archive\" database"

      srctable = self.config['cleanup_srctable']
      dsttable = self.config['cleanup_dsttable']
      stations = self.config['cleanup_stations']

      # - If one of both is None: skip
      if not srctable or not dsttable:
         print "    In config.conf: srctable or dsttable in [cleanup]"
         print "    not set. Archive of data not wished. Return."
         return True

      print "    From database:   %s" % srctable
      print "    To   database:   %s" % dsttable

      # - No stations
      if len(stations) == 0:
         print "    But no stations defined in the config.conf file"
         print "    in [cleanup]. Seems that you dont want any"
         print "    observation data in the archive table. Return."
         return True

      print "    Have to backup:  %s stations" % len(stations)

      # - Source table does not exist?
      if not self.db.__does_table_exist__( srctable ):
         print "[!] Source table %s does not exist! RETURN!\n" % srctable
         return False

      # - Check if table exists. 
      if not self.db.__does_table_exist__( dsttable ):
         print "[!] Table does not exist, we have to create it first"
         sql = "CREATE TABLE %s LIKE %s" % (dsttable,srctable)
         cur = self.db.cursor()
         cur.execute( sql )
         self.db.commit()
      else:
         print "    Table existing, migrate data ..."

      # - Checking columns in both tables. All columns in 'srctable'
      #   have to exist in the 'dsttable'. Else altering the dsttable.
      cur = self.db.cursor()

      # - Loading src columns
      cur.execute("SHOW COLUMNS FROM %s" % srctable)
      coldef = cur.fetchall() 
      srccols = []
      for x in coldef: srccols.append( x[0] )

      # - Loading dst columns
      cur.execute("SHOW COLUMNS FROM %s" % dsttable)
      tmp = cur.fetchall()
      dstcols = []
      for x in tmp: dstcols.append( x[0] )

      # - Checking columns
      for col in srccols:
         if col in dstcols: continue
         # - Search config
         print "[!] Column \"%s\" does not exist in table %s: ALTER" % (col,dsttable)
         for rec in coldef:
            if rec[0] == col:
               # - Create alter statement
               sql = 'ALTER TABLE %s ADD %s %s;' % (dsttable,rec[0],rec[1])
               cur.execute(sql)


      # -------------------------------------------------------------
      # - Now migrating the data
      # -------------------------------------------------------------
      statnr = ",".join(["%d"]*len(stations)) % tuple(stations)
      sql = "SELECT * FROM %s WHERE statnr in (%s)" % (srctable,statnr)
      cur = self.db.cursor()
      cur.execute(sql) 
      desc = cur.description
      data = cur.fetchall()

      print "    %d rows to copy from %s -> %s" % (len(data),srctable,dsttable)
      cols = []
      for rec in desc: cols.append( rec[0] )

      sql = "REPLACE %s (" % dsttable + ",".join(cols) + ") VALUES (" + ",".join( ["%s"]*len(cols)) + ")"
      cur.executemany( sql, data )

      self.db.commit()

      print "    Data copied to %s table. Done." % dsttable
   

       



   # ----------------------------------------------------------------
   # - Remove old observations from live table.
   # ----------------------------------------------------------------
   def cleanup_live_table(self):
      """
      We have a live and an archive table. These two tables are
      defined in the config.conf file. Here we are deleting all
      observations from the live table ('srctable') which are older
      than about 'db_days' days (as well defined in the config.conf file).
      """

      import os, sys, time
      from datetime import datetime as dt
      import numpy as np

      days    = self.config['cleanup_db_days']
      maxage  = np.floor(time.time() / 86400)*86400 - days*86400
      srctable = self.config['cleanup_srctable']

      print ""
      print "  - Delete old observations from %s table" % srctable

      # - Source table does not exist?
      if not self.db.__does_table_exist__( srctable ):
         print "[!] Source table %s does not exist! RETURN!\n" % srctable
         return False

      print "    Delete observations older than %s" % dt.fromtimestamp( maxage ) 


      # - SQL - delete
      sql = "DELETE FROM %s WHERE datumsec < %d" % (srctable,maxage)
      cur = self.db.cursor()
      cur.execute( sql )

      self.db.commit()

      print "    Old observations deleted. Done."



   # ----------------------------------------------------------------
   # - Close database
   # ----------------------------------------------------------------
   def closeDB(self):
      """
      Closing database.
      """
      self.db.close()
