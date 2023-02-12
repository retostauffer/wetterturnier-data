# -------------------------------------------------------------------
# - NAME:        database.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-09
# -------------------------------------------------------------------
# - DESCRIPTION: Handling MySQL database access to store the data.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-09, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-08-02 08:24 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------

import sys, os, pymysql

class database( object ):

   import sys, os, pymysql

   def __init__(self,config,type=None,stationtable='stations',database="obs"):
      
      # - Simply pick the infos we need.
      host        = config['mysql_host']
      user        = config['mysql_user']
      passwd      = config['mysql_passwd']
      if database == "obs":
         db = config['mysql_database']
      elif database == "wp":
         db = config['wp_database']
      else:
         sys.exit("ERROR: Unknown database type")

      # - Try to connect to the database. If not, exit.
      try:
         self.db = pymysql.connect(host=host,user=user,password=passwd,database=db)
      except Exception as e:
         print(e)
         sys.exit('Cannot connect to the database.')

      # - Store config
      self.config       = config

      if database == "obs":
         
         # - Store table name
         self.table        = None
         self.type         = type
         self.stationtable = stationtable

         # - Create 'bufr' table. If not existing using
         #   config['mysql_bufr_create'] file to create the table.
         if not self.type == None:
            self.table = config["mysql_%s_tablename" % self.type]
            self.__check_or_create_table__(self.table,config['mysql_%s_create'        % self.type]) 
            self.__check_or_create_table__(self.stationtable,config['mysql_%s_create' % self.stationtable]) 


   # ----------------------------------------------------------------
   # - Checks if table exists
   # ----------------------------------------------------------------
   def __does_table_exist__(self,name):

      sql = 'SELECT * FROM information_schema.tables WHERE table_name = \"%s\"' % name
      cur = self.db.cursor()
      cur.execute( sql )
      if not cur.fetchone() == None:
         cur.close()
         return True
      cur.close()
      return False


   # ----------------------------------------------------------------
   # - Reading table setup
   # ----------------------------------------------------------------
   def read_table_setup(self):

      # - File containing the table setup/column config
      setup = self.config['mysql_%s_columns' % self.type] 

      if not os.path.isfile( setup ):
         sys.exit('ERROR: File \"%s\" does not exist. Stop.' % setup)

      # - Reading the file
      try:
         fid = open( setup, 'r' )
      except Exception as e:
         print(e)
         sys.exit('Problems reading file \"%s\".' % setup)

      # - Now reading content
      lines = fid.readlines()
      fid.close()

      # - Parsing
      res = {}
      for line in lines:
         if   len(line.strip()) == 0: continue
         elif line.strip()[0] == '#': continue
         # - Need three elments
         tmp = line.split(';')
         if not len(tmp) == 2:
            sys.exit('ERROR: line \"%s\" wrong defined in \"%s\"' % (line,setup))
         # - Append
         res[tmp[0].strip()] = {'type':tmp[1].strip()}

      return res 

   # ----------------------------------------------------------------
   # - Loading columns from database
   #   stores a dict containing column name
   #   Need this later on to fill the data tuples.
   # ----------------------------------------------------------------
   def loadcolumns(self):
   
      cur = self.db.cursor()
      cur.execute('SELECT * FROM %s LIMIT 0' % self.table)
      result = []
      for rec in cur.description: result.append( rec[0] )
      return result


   # ----------------------------------------------------------------
   # - Checking columns and alter table if necessary
   # ----------------------------------------------------------------
   def __check_columns__(self,columns):

      # - Check if columns exists. Else append.
      cur = self.db.cursor()
      cur.execute('SELECT * FROM %s LIMIT 0' % self.table)
      db_columns = []
      for rec in cur.description: db_columns.append( str(rec[0]) )
      for rec in columns:
         if not rec in db_columns:
            # - WOOOO column does not exist.
            #   Tell the database object to ALTER the table
            #   and append the column.
            self.addcolumn( rec )



   # ----------------------------------------------------------------
   # - Based on DBSETUP: Append column to existing database table.
   # ----------------------------------------------------------------
   def addcolumn(self,name):

      import re

      print('    Appending column to existing database: %s' % name)
      
      # - If setupfile not read: do
      DBSETUP   = self.read_table_setup()
      # - If not DBCOLUMNS: read columns
      DBCOLUMNS = self.loadcolumns()

      # - Is name in columns?
      if not name in DBCOLUMNS:

         # - If this is a time column, take the time
         #   definition from the DBSETUP. All the same.
         if not name in DBSETUP and not re.match('.*_[0-9]{1,2}$',name) == None:
            basename = name.split('_')[0]
            if not basename in DBSETUP:
               sys.exit('SORRY, CANNOT FIND \'%s\' IN DBSETUP.' % basename)
            else:
               col = DBSETUP[basename]
         elif not name in DBSETUP:
            sys.exit('SORRY, CANNOT FIND \"%s\" IN DBSETUP.' % name)
         else:
            col = DBSETUP[name]
         # - Create alter statement
         sql = 'ALTER TABLE %s ADD %s %s IF NOT EXISTS;' % (self.table, \
               name,col['type'])

         # - Append column
         cur = self.db.cursor()
         cur.execute( sql )
         self.db.commit()
         # - Append column name to self.DBCOLUMNS
         self.DBCOLUMNS = self.loadcolumns()
         

   # ----------------------------------------------------------------
   # - Check and or create data table
   # ----------------------------------------------------------------
   def __check_or_create_table__(self,name,createfile):

      ##TEST##if name == 'bufrdesc':
      ##TEST##   sys.exit( "check or create table %s using template %s" % (name,createfile) )

      # - If allready existing, just skip
      if self.__does_table_exist__(name):
         #print("Table bufrdesc already exists!")
         return

      # - Create
      print('    - Table %s does not exist, create now' % name)

      # - We are using the scheme from the ZAMG synop table.
      #   Check if we can find the file. If not, stop.
      if not os.path.isfile( createfile ):
         sys.exit('CANNOT FIND FILE %s CONTAINING THE CREATE TABLE STATEMENT.' % createfile )
      # - Reading the file
      fid = open( createfile, 'r' )
      content = fid.readlines()
      fid.close()

      # - Check if we can find 'table_name' in CREATE stetemtn.
      #   If not, stop. Else replace 'table_name' with
      #   self.config['mysql_datatable'] and create the table.
      create = '\n'.join( content )

      # - Replace
      create = create.replace('table_name',name)

      cur = self.db.cursor()
      cur.execute( create )
      cur.close()

   def rollback(self):
      print("[!] Database rollback called ...")
      self.db.rollback()

   def commit(self):
      print("[!] Database commit called ...")
      self.db.commit()

   def cursor(self):
      return self.db.cursor()

   def close(self):
      print('    Close database now')
      self.db.commit()
      self.db.close()


   # ----------------------------------------------------------------
   # - get tournament stations from wordpress database (obs needs read permits)
   # ----------------------------------------------------------------
   def get_stations(self, active=True):
    
      #connect to wpwt database as obs user (read-only)
      active = " WHERE active=1" if active else ""
      
      sql = "SELECT dwd,wmo FROM wp_wetterturnier_stations" + active

      cur = self.db.cursor()
      cur.execute(sql)
      
      ids = []

      for i in cur.fetchall():
         if i[0]:
            ids.append(i[0])
         else:
            ids.append(i[1])

      return ids


   def get_wmo(self, dwd):
      
      sql = f'SELECT wmo FROM wp_wetterturnier_stations WHERE dwd LIKE "{dwd}"'

      cur = self.db.cursor()
      cur.execute(sql)
      
      try:
         res = cur.fetchone()
         return int(res[0])
      except:
         return None
