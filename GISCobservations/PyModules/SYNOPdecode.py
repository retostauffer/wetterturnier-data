# -------------------------------------------------------------------
# - NAME:        SYNOPdecode.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-15
# -------------------------------------------------------------------
# - DESCRIPTION: Deparsing synop code files.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-15, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-07-20 17:52 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


import sys, os

# -------------------------------------------------------------------
# - Main class for decoding BUFR
# -------------------------------------------------------------------
class SYNOPdecode( object ):
   """Deparsing Synop Code ASCII Files"""

   # - Initialization 
   def __init__( self, config, file, verbose = False ):

      self.file     = file 
      self.VERBOSE  = verbose
      self.data     = None
      self.DECODED  = []
      self.PREPARED = None
      self.db       = None
      self.ERROR    = False


      if not os.path.isfile(file):
         sys.exit('ERROR BUFRbin: cannot read file %s' % file)
      self.file = file
      self.config = config

      # - Initialize database
      from database import database
      self.db = database(config,'bufr')

      # - Reading tye ASCII file on init
      self.date = self.__get_yyyymm_from_filename__(file)
      raw  = self.__read_synop_file__()
      if raw == None:
         print('[!] Could not find any messages. Return None')
         self.ERROR = True
         return
      head,station,data = self.__parse_raw_data__(raw)
      #for line in data:
      #   print line
      if data == None:
         print('[!] File content seems to be unpropper. Return None')
         self.ERROR = True
         return
      # - Write data to self.data
      self.data = data

      # - Else checking date
      self.date = self.__check_date__(self.date,head)

   # ----------------------------------------------------------------
   # - Correcting first guess date if necessary. Note that
   #   for files where the date is not contained in the file name
   #   the script imagines that the message is from this or the
   #   previous month because we do not have any other information!!
   # ----------------------------------------------------------------
   def __check_date__(self, date, head):

      import datetime as dt
      import re

      # - Find date in head
      head_date = re.findall('(?<=[A-Z]{4}\ )[0-9]{6}',head.upper())
      if len(head_date) == 1:
         head_day = int(head_date[0][0:2])
         date_day = int(date.strftime('%d'))

         # - If the day from the file is bigger than
         #   'date' we have picked 'today' as best guess
         #   for the date of the synop message, but the
         #   file was from a few days ago (yesterday e.g.,)
         #   which was a different month. In this case we have
         #   re-adjust our first guess.
         if head_day > date_day:
            day = head_day
            mon = int(date.strftime('%m')) - 1
            year = int(date.strftime('%Y'))
            if mon < 0:
               mon = mon+12   
               year = year -1
            # - Date
            date = dt.date(year,mon,day)
      
            print('[!] Corredted expected date to: %s' % date.strftime('%Y-%m-%d'))

      return date

   # ----------------------------------------------------------------
   # - Synop messages only contain Day of the month and hour.
   #   Therefore we are checking if there is a date in the
   #   file name (YYYYMMDD). If not, we have to expect that the
   #   message is for the current year/month/day.
   # ----------------------------------------------------------------
   def __get_yyyymm_from_filename__(self,file):

      import re
      import datetime as dt

      date = re.findall(r'2[0-9]{7}',file)
      if date == None:
         date = dt.date.today()
      else:
         try:
            date = dt.datetime.strptime(date,'%Y%m%d')
         except:
            date = dt.date.today()

      print('    - Expected date of the synop file: %s' % date.strftime('%Y-%m-%d'))
      return date


   # ----------------------------------------------------------------
   # - Reading ASCII file RAW first
   # ----------------------------------------------------------------
   def __read_synop_file__(self):

      fid = open( self.file, 'r' )
      raw = fid.readlines()
      fid.close()

      import re

      # - Replace carriage return and line breaks and tabulators
      for i in range(0,len(raw)):
         raw[i] = re.sub(r'(\n)?(\t)?(\r)?','',raw[i]) 

      return raw


   # ----------------------------------------------------------------
   # - Extracting header line, Station indicator, and data
   # ----------------------------------------------------------------
   def __parse_raw_data__( self, raw ):

      # - First checking if this is a land station indicated
      #   by the keyword AAXX. If not, stop at the moment.
      if ' '.join(raw).find('AAXX') < 0:
         print('[!] COULD NOT FIND INDICATOR \"AAXX\".')
         print('    Skip this file ...')
         return None,None,None

      # - As long as we have not found 'AAXX' we append the
      #   data to the header section.
      head    = None 
      station = None
      tmp     = []
      found_aaxx = False
      for line in raw:
         if line.find('AAXX') >= 0:
            found_aaxx = True
            station = line
            continue
         elif not found_aaxx:
            head = line
         else:
            tmp.append( line )

      # - WARNING: single messages can be splitted in two lines.
      #   now splitting 'tmp' at '=' to get line-by-line messages.
      data = []
      for line in ' '.join(tmp).split('='):
         if len(line.strip()) == 0: continue
         data.append( '%s %s=' % (station.strip(),line.strip()) )

      # - Station indicator not found?
      #   Return None three times to indicate that the
      #   file was emtpy or not in propper format.
      if not found_aaxx: return None,None,None

      return head, station, data


   # ----------------------------------------------------------------
   # - Extracting information from the messages. This is the main
   #   part of the SYNOPdecoder.
   # ----------------------------------------------------------------
   def decode( self, msg = None ):

      from SYNOPclass import synop 
      import re

      # - No data?
      if self.data == None:
         print('[!] Problem in SYNOPcode.decode: no data loaded.')
         return None

      # - Which message?
      if not msg == None:
         if msg < 0 or msg > len(self.data):
            sys.exit('Problem in SYNOPcode.decode: input msg was out of range.')
         data = [self.data[msg]]
      else:
         data = self.data

      # - For rec in data: extract necessary infos
      for rec in data:
         print(rec)
         if re.findall('AAXX',rec) < 0: continue # no propper message

         # - Create synop object out of this message
         rec = synop( rec, self.date )
         if rec.NIL:
            continue
         elif self.VERBOSE: 
            rec.show()

         self.DECODED.append(rec)

   # ----------------------------------------------------------------
   # - Prepares the data.
   #   Puts the data we found bevore in the single messages into
   #   a matrix style variable called "res". Stores parameter
   #   (column description of the matrix) and the data matrix into
   #   self.PREPARED.
   # ----------------------------------------------------------------
   def prepare_data( self ):

      res = ()
      par = []
      # - First check out how many different parameter we have in the
      #   data.
      for rec in self.DECODED:
         for data in rec.DATA:
            if not data[0] in par:
               # - Append column/parameter
               par.append( data[0] )

      # - Create numpy matrix to store all the values
      import numpy as np
      res = np.ndarray( (len(self.DECODED),len(par)), dtype="float" )

      self.db.__check_columns__(par)

      # - Create empty results array and fill
      #   with emptyvalues from the setup file
      res[:,:] = None 

      # - Fill in the data
      for r in range(0,len(self.DECODED)): 
         for data in self.DECODED[r].DATA:
            c = par.index( data[0] )
            res[r,c] = data[1]

      self.PREPARED = {'parameter':par,'data':res} 


   def show_prepared(self):

      if not self.PREPARED:
         print('[!] No data prepared. Can\'t show the data.')
         return

      # - Print header
      for p in self.PREPARED['parameter']:
         print("%-8s" % p, end=' ')
      print('')
   
      # - Print data
      for r in range(0,self.PREPARED['data'].shape[0]):
         for c in range(0,self.PREPARED['data'].shape[1]):
            print("%8.2f" % self.PREPARED['data'][r,c], end=' ')
         print('')

   # ----------------------------------------------------------------
   # - Write the data we have found into the database now.
   # ----------------------------------------------------------------
   def write_to_db(self):

      if self.db == None:
         print('[!] Database connection not established. Return.')
         return

      # - No data?
      if self.PREPARED['data'].shape[0] == 0:
         print('    No data to write into the database.')
         return

      # - Columns
      columns = self.PREPARED['parameter']
      self.db.__check_columns__( columns )

      # - Prepare update statement
      update = []
      for col in columns: update.append('%s=VALUES(%s)' % (col,col))

      sql = []
      sql.append('INSERT INTO bufr') #### % self.config['mysql_datatable'] )
      sql.append('  (msgtyp,%s)' % ', '.join( columns ))
      sql.append('  VALUES')
      sql.append('  (\'synop\',%s)' % ', '.join( ['%s']*len(columns) ))
      sql.append('ON DUPLICATE KEY UPDATE')
      sql.append('  %s' % ", ".join( update ))

      data = []
      import numpy as np
      for i in range(0,self.PREPARED['data'].shape[0]):
         ##data.append( tuple(self.PREPARED['data'][i,]) )
         df = self.PREPARED['data'][i,].tolist()
         for i in range(0,len(df)):
            if np.isnan( df[i] ): df[i] = None
         data.append( df )


      print("    Write %d entries into the database" % len(data))
      cur = self.db.cursor()
      cur.executemany( '\n'.join(sql), data )


   # ----------------------------------------------------------------
   # - Helper function to close the database
   # ----------------------------------------------------------------
   def closedb(self):
      self.db.close()









