# -------------------------------------------------------------------
# - NAME:        database.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-11-04
# -------------------------------------------------------------------
# - DESCRIPTION: Class handling the mysql database connection.
#                Can be used as a separate class or as an extension
#                of another class like insertForecasts.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-11-04, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-12-12 14:59 on pc24-c707
# -------------------------------------------------------------------

import logging, logging.config
log = logging.getLogger(__name__)


class database( object ):

   db = None

   # ----------------------------------------------------------------
   # INIT when class is used directly. Not tested yet
   # ----------------------------------------------------------------
   def __init__( self, config ):

      self.config = config
      if not self.doesTableExist( self.config.mysql_table ):
         log.error("Table \"%s\" not existing in database. Stop." % self.config.mysql_table)
         sys.exit(9)

   
   # ----------------------------------------------------------------
   # CONNECTING DATABASE
   # ----------------------------------------------------------------
   def dbConnect( self ):
      """!Connect to mysql database based on self.config. There
      is an optional input argument \"connection\". As we have to
      use different login names and stuff, this can be used to 
      use different login configs from the config.
      @param connection. String, optional. If \"None\", the config
         from [mysql] out of the config file will be used. If set to
         \"WBfx\" the [mysql WBfx] config will be used to open the
         database connection (used by getWBFXdata.py)."""

      if not self.db is None: return
      import MySQLdb, sys

      # Default
      try:
         self.db = MySQLdb.connect( host   = self.config.mysql_host,
                                    user   = self.config.mysql_username,
                                    passwd = self.config.mysql_password,
                                    db     = self.config.mysql_database )
      except Exception as e:
         log.error(e)
         log.error("Problems connecting to database.")
         sys.exit(9)

      log.info("Database connection established")


   # ----------------------------------------------------------------
   # Loading obsevations for a certain time and station
   # ----------------------------------------------------------------
   def loadData(self,station,dt):
      """!Loading all observations for given datetime and station.
      @param station. Integer, required. Station number.
      @param dt. Datetime, required. Date and time.
      @return Either None, if no data could be found in the database,
         or a dict containing all values. Empty value will be
         dropped and not appended to the dict.
      """

      from datetime import datetime

      sql = []
      sql.append("SELECT * FROM %s" % self.config.mysql_table)
      sql.append("WHERE statnr = %d" % station)
      sql.append("AND datumsec = %s" % dt.strftime("%s"))

      cur = self.dbCursor()
      cur.execute( "\n".join(sql) )

      desc = cur.description
      data = cur.fetchone()

      # No data at all? Return None
      if data is None: return None

      result = {}
      for i in range(0,len(desc)): 
         key = str(desc[i][0]).lower()
         val = data[i]
         if val is None: continue
         result[key] = val

      # No valid data? Return None
      if len(result) == 0: return None

      # Else return dict
      return result

   # ----------------------------------------------------------------
   # Check if database table exists:
   # ----------------------------------------------------------------
   def doesTableExist( self, table ):
      if not self.db: self.dbConnect()

      # Check if a table is existing
      sql = []
      sql.append("SELECT * FROM information_schema.tables")
      sql.append("WHERE table_schema = '%s'" % self.config.mysql_database)
      sql.append("AND table_name = '%s' LIMIT 1" % table) 
      sql = " ".join(sql)

      cur = self.dbCursor()
      cur.execute( sql )
      res = cur.fetchone()

      if not res: return False 
      return True

   # ----------------------------------------------------------------
   # A few quick-access functions
   # ----------------------------------------------------------------
   def dbCursor( self ):
      if not self.db: self.dbConnect()
      return self.db.cursor()
   def dbClose( self ):
      if self.db: self.db.commit()
      if self.db: self.db.close()



   # ----------------------------------------------------------------
   # executes the incoming sql statment and returns column names
   # and data.
   # ----------------------------------------------------------------
   def dbFetchData( self, sql ):

      #log.debug("Calling: %s" % " ".join(sql))
      cur = self.dbCursor()
      cur.execute( sql )
      desc = cur.description
      data = cur.fetchall()

      # Nice column names list
      cols = []
      for rec in desc: cols.append( rec[0] )

      return cols,data

















