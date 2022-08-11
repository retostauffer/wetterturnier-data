# -------------------------------------------------------------------
# - NAME:        derivedvars.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2015-07-22
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-07-22, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-12-13 08:31 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


from database import database
import os, sys

class derivedvars( object ):

   def __init__(self, config, table = 'live' ):

      self.config = config
      self.table  = table
      self.db     = database( config )


   # ----------------------------------------------------------------
   # - Compute relative humidity based on temperature and dew point
   # ----------------------------------------------------------------
   def compute_rh_from_td( self, nhours ):

      from datetime import datetime as dt
      import numpy as np

      # - Oldest entry to check
      oldest = int(dt.now().strftime('%s')) - nhours*3600
      # - Getitng data and column description
      desc,data = self.__get_data__(['td','t'],'rh',oldest)
      # - Index of the elements we need
      try:
         i_statnr   = desc.index('statnr')
         i_datumsec = desc.index('datumsec')
         i_msgtyp   = desc.index('msgtyp')
         i_td       = desc.index('td')
         i_t        = desc.index('t')
      except Exception as e:
         print(e)
         sys.exit("Problems to find variable indizes!!!")

      print("    Found %d entries where we have to compute rh (from t/td)" % len(data))
      
      # - Comute new values. Store in list with corresponding
      #   data we need for the update (statnr, datumsec, msgtyp)
      result = []
      for rec in data:
         td = np.float( rec[i_td] ) / 10. # in celsius
         t  = np.float( rec[i_t]  ) / 10. # in celsius

         rh = 100. * ( np.exp((17.625*td)/(243.04+td)) \
                       / np.exp((17.625*t)/(243.04+t))  )
         rh = np.minimum(np.maximum( rh,0),100)
         rh = int( np.round(rh) )
         # - Append result
         result.append( (rh, rec[i_statnr], rec[i_datumsec], rec[i_msgtyp]) )

      # - Update database
      sql = "UPDATE " + self.table + \
            " SET rh = %s WHERE statnr=%s AND datumsec=%s AND msgtyp=%s"
      cur = self.db.cursor()
      try:
         cur.executemany(sql,result)
      except Exception as e:
         print(e)
         self.db.rollback()
         sys.exit('Problems executing statement %s' % sql)

      self.db.commit() 


   # ----------------------------------------------------------------
   # - Compute dew point temperature from relative humidity
   # ----------------------------------------------------------------
   def compute_td_from_rh( self, nhours ):

      from datetime import datetime as dt
      import numpy as np

      # - Oldest entry to check
      oldest = int(dt.now().strftime('%s')) - nhours*3600
      # - Getitng data and column description
      desc,data = self.__get_data__(['rh','t'],'td',oldest)
      # - Index of the elements we need
      try:
         i_statnr   = desc.index('statnr')
         i_datumsec = desc.index('datumsec')
         i_msgtyp   = desc.index('msgtyp')
         i_rh       = desc.index('rh')
         i_t        = desc.index('t')
      except Exception as e:
         print(e)
         sys.exit("Problems to find variable indizes!!!")

      print("    Found %d entries where we have to compute td (from t/rh)" % len(data))
      
      # - Comute new values. Store in list with corresponding
      #   data we need for the update (statnr, datumsec, msgtyp)
      result = []
      for rec in data:
         rh = np.float( rec[i_rh] ) / 100. # between 0 and 1
         t  = np.float( rec[i_t]  ) / 10.  # in celsius

         td = 243.04 * ( np.log(rh)+((17.625*t)/(243.04+t)) ) \
                     / ( 17.625-np.log(rh)-((17.625*t)/(243.04+t)) )
         print(td,'  ', end=' ')
         td = int(np.round(td*10))
         # - Append result
         result.append( (td, rec[i_statnr], rec[i_datumsec], rec[i_msgtyp]) )

      # - Update database
      sql = "UPDATE " + self.table + \
            " SET td = %s WHERE statnr=%s AND datumsec=%s AND msgtyp=%s"
      cur = self.db.cursor()
      try:
         cur.executemany(sql,result)
      except Exception as e:
         print(e)
         self.db.rollback()
         sys.exit('Problems executing statement %s' % sql)

      self.db.commit() 


   # ----------------------------------------------------------------
   # - Loading data 
   # ----------------------------------------------------------------
   def __get_data__( self, cols, nullcol, oldest ):

      if not cols:
         sys.exit("[!] Error in __get_data__: columns have to be set!")

      where = list()
      for c in cols: where.append("NOT %s IS NULL" % c)

      sql = list()
      sql.append("SELECT statnr, datumsec, msgtyp, %s" % ", ".join(cols))
      sql.append("FROM %s WHERE"  % self.table )
      sql.append("%s IS NULL AND" % nullcol    )
      sql.append("datumsec >= %d AND %s" % (oldest," AND ".join( where )))
      sql = "\n".join(sql)

      cur = self.db.cursor()

      cur.execute( sql )
      # - Column description
      desc = []
      for d in cur.description: desc.append( str(d[0]) )
      # - Data
      data = cur.fetchall()

      return desc,data

   # ----------------------------------------------------------------
   # - Closes database
   # ----------------------------------------------------------------
   def close(self):

      self.db.close()
