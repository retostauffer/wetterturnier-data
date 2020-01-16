# -------------------------------------------------------------------
# - NAME:        SYNOPclass.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-15
# -------------------------------------------------------------------
# - DESCRIPTION: Deparsing synop message 
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-15, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-03-13 14:06 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------

import sys, os
import re
from bcolors import bcolors

# -------------------------------------------------------------------
# -------------------------------------------------------------------
class synop(object):

   NIL = False
   MISSING_INT =  255
   MISSING_NUM = -999
   VERBOSE = False
   KNOTS2MS = 0.51444444444 # factor from knots -> meters per second

   def __init__(self,rec,date=None):

      self.DATA = []
      self.date = date
      # - If Message contains NIL: no data
      if 'NIL' in rec:
         self.NIL = True
      else:
         # - Extracting the blocks first
         self.getinfo(rec)

         # - Filling data dict
         self.__datadict__()


   # ----------------------------------------------------------------
   def getinfo(self,rec):

      res = re.findall(r'(?<=AAXX).?(.*)',rec)
      if not len(res) == 1:
         sys.exit('Problems decoding %s in synop class' % rec) 
      # - Else extracting basic infos
      res = res[0].split(' ')
      self.day  = int(res[0][0:2])
      self.hour = int(res[0][2:4])
      if len(res[0]) == 5:
         self.minute = 0
         self.iw     = int(res[0][4:])
      else:
         self.minute = int(res[0][4:6])
         self.iw     = int(res[0][6:])

      # - Station or ship number
      self.station = int(res[1])

      # - Getting the blocks
      self.b0 = self.__block__(rec,0)
      self.b3 = self.__block__(rec,3)
      self.b4 = self.__block__(rec,4)
      self.b5 = self.__block__(rec,5)
      self.b6 = self.__block__(rec,6)
      self.b9 = self.__block__(rec,9)

      # - Show blocks if VERBOSE
      if self.VERBOSE:
         print(rec)
         print(bcolors.OKBLUE)
         print("    Block 0:  %s" % self.b0)
         print("    Block 3:  %s" % self.b3)
         print("    Block 4:  %s" % self.b4)
         print("    Block 5:  %s" % self.b5)
         print("    Block 6:  %s" % self.b6)
         print("    Block 9:  %s" % self.b9)
         print(bcolors.ENDC)


   # ----------------------------------------------------------------
   # - Returns string beginning with pattern. If patter does not
   #   occure, return empty string.
   # ----------------------------------------------------------------
   def __beginwith__(self,search,string):
      if type(search) == type(str()):
         x = re.search(r'(?<=%s).*' % search, string)
         if x == None: return('')
         return( x.group(0).strip() )
      else:
         count = 0
         for s in search:
            x = re.search(r'(?<=%s).*' % search, string)
            if x == None: continue
            count = count + 1
            string = x.group(0) 
         if count == 0: return('')
         return(string.strip())


   # ----------------------------------------------------------------
   # - Returns string ending with pattern. 
   # ----------------------------------------------------------------
   def __endswith__(self,search,string):
      if type(search) == type(str()):
         x = re.search(r'^(.*)(?=%s)' % search, string)
         if x == None: return(string)
         return( x.group(0).strip() )
      else:
         for s in search:
            x = re.search(r'(.*)(?=%s)' % s, string)
            if x == None: continue
            string = x.group(0) 
         return(string.strip())


   # ----------------------------------------------------------------
   def __block__(self,rec,block):

      # - Block 0 
      if block == 0:
         rec = self.__endswith__([' 333 ',' 444 ',' 555 ',' 666 ',' 999 ','='],rec)
      elif block == 3:
         rec = self.__beginwith__(' 333 ',rec)
         rec = self.__endswith__([' 444 ',' 555 ',' 666 ',' 999 ','='],rec)
      elif block == 4:
         rec = self.__beginwith__(' 444 ',rec)
         rec = self.__endswith__([' 555 ',' 666 ',' 999 ','='],rec)
      elif block == 5:
         rec = self.__beginwith__(' 555 ',rec)
         rec = self.__endswith__([' 666 ',' 999 ','='],rec)
      elif block == 6:
         rec = self.__beginwith__(' 666 ',rec)
         rec = self.__endswith__([' 999 ','='],rec)
      elif block == 9:
         rec = self.__beginwith__(' 999 ',rec)
         rec = self.__endswith__(['='],rec)
      else:
         sys.exit('Input protblem to __block__ method')

      return rec


   # ----------------------------------------------------------------
   # - Shows content of self.DATA. Development routine.
   # ----------------------------------------------------------------
   def show(self):

      if self.NIL:
         print('    - MESSAGE CONTAINED \"NIL\": no data')
      else:
         print('    - %-20s %02d%02d%02d%d' % ('YYGGggIw:',self.day,self.hour,self.minute,self.iw)) 
         print('    - %-20s %7d'            % ('Station:',self.station))


      if len(self.DATA) > 0:
         print(bcolors.OKRED)
         for i in range(0,len(self.DATA)):
            print('    [] %-10s ' % self.DATA[i][0], end=' ') 
            if type(self.DATA[i][1]) == type(int()):
               print('%8d' % self.DATA[i][1])
            else:
               print(self.DATA[i][1])
         print(bcolors.ENDC)


   # ----------------------------------------------------------------
   # - Extracting data
   # ----------------------------------------------------------------
   def __datadict__(self):

      # - Extracting different elements. First from block 0
      self.__get000_station__()

      # - Extracting date and shit
      day, hour, minute = self.__get000_date__()
      import datetime as dt
      if self.date == None:
         date = dt.date.today()
      else:
         date = self.date
      # - Manipulate the date if necessary
      if day == date.day:
         date = dt.datetime.strptime( '%s-%0d %02d:%02d' % \
                (date.strftime('%Y-%m'),day,hour,minute), '%Y-%m-%d %H:%M' ) 
      elif day < date.day:
         date = dt.datetime.strptime( '%s-%0d %02d:%02d' % \
                (date.strftime('%Y-%m'),day,hour,minute), '%Y-%m-%d %H:%M' ) 
      elif day > date.day:
         tmp_year = date.year
         tmp_mon  = date.month - 1
         if tmp_mon < 1:
            tmp_mon  = tmp_mon + 12
            tmp_year = tmp_year - 1
         date = dt.datetime.strptime( '%04d-%02d-%02d %02d:%02d' % \
                (tmp_year,tmp_mon,day,hour,minute), '%Y-%m-%d %H:%M' )

      ###print '   %s %3d %3d %3d' % (date.strftime('%Y-%m-%d %H:%M'),day,hour,minute)
      # - Appending some necessary keys
      self.DATA.append( ('datum',   int(date.strftime('%Y%m%d'))) )
      self.DATA.append( ('stdmin',  int(date.strftime('%H%M'))) )
      self.DATA.append( ('datumsec',int(date.strftime('%s'))) )

      self.hour   = int(date.strftime('%H'))
      self.minute = int(date.strftime('%M'))

      # -------------------------------------------------------------
      # - Block 0 
      # -------------------------------------------------------------
      if self.VERBOSE: print(' EXTRACTING BLOCK 000 NOW ... ')
      # - Extracting wind idx
      self.knots = False # will be changed if Iw == 3 or Iw == 4
      if len(self.b0.split()) > 3:
         self.__get000_Iw__()
         self.__get000_IrIxhVV__()
         self.__get000_Nddff__()
         # - Optional block 00fff if available
         self.__get000_00fff__()
         # - Temperature an dew point temperature
         self.__get000_1sTTT__()
         self.__get000_2sTTT__()
         # - Pressure
         self.__get000_3pppp__()
         self.__get000_4pppp__()
         self.__get000_5appp__()
         self.__get000_6RRRt__()
         # - Weather
         self.__get000_7www1w2__() 
         # - Clouds and stuff
         self.__get000_8nhchcmcl__() 
         # - Ignoring block 9GGgg

      # -------------------------------------------------------------
      # - Block 3
      # -------------------------------------------------------------
      if self.VERBOSE: print(' EXTRACTING BLOCK 333 NOW ... ')
      if not len(self.b3) == 0:
         self.__get333_1sTTT__()
         self.__get333_2sTTT__()
         self.__get333_3EsTT__()
         self.__get333_4Esss__()
         self.__get333_55SSS__()

         self.__get333_6RRRtr__()
         self.__get333_7RRRR__()
         self.__get333_8NsChs__()
         self.__get333_9SSss__()



   # ----------------------------------------------------------------
   # - Block 0:   Station and date information
   # ----------------------------------------------------------------
   # - Day, Hour, [Minute], and Wind indicator
   def __get000_date__(self):
      rec = self.b0.split(' ')[1]
      try:
         day = int(rec[0:2])
      except:
         day = self.MISSING_INT
      try:
         hour = int(rec[2:4])
      except:
         hour = self.MISSING_INT
      if len(rec) == 5:
         minute = 0
      else:
         try:
            minute = int(rec[-2:])
         except Exception as e:
            print(e)
            sys.exit('Problems extracting the minute from %s' % rec)
            minute = self.MISSING_INT
      return day, hour, minute
   # -------------------------------
   def __get000_Iw__(self):
      try:
         Iw = int(self.b0.split(' ')[1][-1])
      except:
         Iw = self.MISSING_INT
      # - If Iw == 3 or Iw == 4 the measurements of wind speeds
      #   are in knots and we have to transform them.
      self.DATA.append( ('Iw',Iw) )
   # -------------------------------
   # - Station number
   def __get000_station__(self):
      try:
         val = int(self.b0.split(' ')[2])
      except:
         val = self.MISSING_INT
      self.DATA.append( ('statnr',val) )

   # ----------------------------------------------------------------
   # - Block 0:   ir|ix|h|vv
   #              1  1  1  2
   # ----------------------------------------------------------------
   # - Ir indicator for precipitation groups 
   # - Ix indicator for station type and weather groups
   # - h  ceiling (height of lowest clouds)
   # - VV Horizontal visibility
   def __get000_IrIxhVV__(self):
      try:
         Ir = int(self.b0.split(' ')[3][0])
      except:
         Ir = self.MISSING_NUM
      self.DATA.append( ('Ir',Ir) )
      try:
         Ix = int(self.b0.split(' ')[3][1])
      except:
         Ix = self.MISSING_NUM
      self.DATA.append( ('Ix',Ix) )
      try:
         h = int(self.b0.split(' ')[3][2])
         self.DATA.append( ('h', h ) )
      except:
         h = self.MISSING_NUM
      # - Loading and converting horizontal visibility vv
      try:
         VV = int(self.b0.split(' ')[3][-2:])
         if   VV <= 50.: return VV * 100
         elif VV <= 80.: return (VV - 50) * 1000
         elif VV <= 88.: return (30. + (VV-80) * 5) * 1000
         elif VV == 89.: return 70001
         elif VV == 90.: return    49
         elif VV == 91.: return    50 
         elif VV == 92.: return   200 
         elif VV == 93.: return   500 
         elif VV == 94.: return  1000
         elif VV == 95.: return  2000
         elif VV == 96.: return  4000
         elif VV == 97.: return 10000
         elif VV == 98.: return 20000
         elif VV == 99.: return 50001
         sys.exit('UNKNOWN CODE %f IN __get_vv__. Check this please.' % val )
         self.DATA.append( ('vv',VV) )
      except:
         VV = self.MISSING_NUM

   # ----------------------------------------------------------------
   # - Block 0:   N|dd|ff
   #              1  2  2
   # ----------------------------------------------------------------
   # - N: cloud cover 
   # - dd: wind direction 
   # - ff: wind speed 
   def __get000_Nddff__(self):
      rec = self.b0.split(' ')[4]
      try:
         N = int(rec[0])
         self.DATA.append( ('N',N) )
      except:
         N = self.MISSING_INT
      try:
         dd = int(rec[1:3]) * 10
         self.DATA.append( ('dd',dd) )
      except:
         dd = self.MISSING_NUM
      try:
         ff = int(rec[-2:]) * 10
         # - If observations in knots: convert
         if self.knots: ff = int(float(ff * self.KNOTS2MS))
         self.DATA.append( ('ff',ff) )
      except:
         ff = self.MISSING_NUM

   # ----------------------------------------------------------------
   # - Getting block 00fff if available
   # ----------------------------------------------------------------
   def __get000_00fff__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('00[0-9]{3}',rec)
      if rec == None: return
      try:
         ff = int(rec.group()[-3]) * 10
      except:
         return
      # - If observations in knots: convert
      if self.knots: ff = int(float(ff * self.KNOTS2MS))
      # - Replace ff in self.DATA if existing
      replaced = False
      tmp = []
      for i in range(0,len(self.DATA)):
         if self.DATA[i][0] == 'ff':
            replaced = True
            tmp.append( ('ff',ff) )
         else:
            tmp.append( self.DATA[i] )
      self.DATA = tmp

   # ----------------------------------------------------------------
   # - Getting block 1sTTT if available
   # ----------------------------------------------------------------
   def __get000_1sTTT__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('1[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         sign = int(rec[1]) 
         if sign == 0:    val = int(rec[-3:]) 
         else:            val = int(rec[-3:]) * (-1)
      except:
         print(e)
         val = self.MISSING_NUM
      self.DATA.append( ('t',val) )

   # ----------------------------------------------------------------
   # - Getting block 1sTTT if available
   # ----------------------------------------------------------------
   def __get000_2sTTT__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('2[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         sign = int(rec[1])
         val  = int(rec[-3:])
         if   sign == 0:
            self.DATA.append( ('td',val) )
         elif sign == 1:
            self.DATA.append( ('td',val * (-1)) )
         elif sign == 9:
            self.DATA.append( ('rh',val) )
      except Exception as e:
         td  = self.MISSING_NUM
         rel = self.MISSING_INT

   # ----------------------------------------------------------------
   # - Getting block 3PPPP if available
   # ----------------------------------------------------------------
   def __get000_3pppp__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('3[0-9]{4}',rec)
      if rec == None: return self.MISSING_NUM
      rec = rec.group()
      try:
         if rec[-1:] == '/':   val = int(rec[1:4]) * 100
         else:                 val = int(rec[-4:]) * 10
         if val < 50000:       val = val + 100000
      except:
         val = self.MISSING_NUM
      self.DATA.append( ('psta',val) )

   # ----------------------------------------------------------------
   # - Getting block 4PPPP if available
   # ----------------------------------------------------------------
   def __get000_4pppp__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('4[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         if rec[-1:] == '/':   val = int(rec[1:4]) * 100
         else:                 val = int(rec[-4:]) * 10
         if val < 50000:       val = val + 100000
      except:
         val = self.MISSING_NUM
      self.DATA.append( ('pmsl',val) )

   # ----------------------------------------------------------------
   # - Getting block 5appp if available
   # ----------------------------------------------------------------
   def __get000_5appp__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('5[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         a = int(rec[1])
         if a < 5:     val = int(rec[-3:]) * 10
         else:         val = int(rec[-3:]) * (-10)
      except:
         val = self.MISSING_NUM
      self.DATA.append( ('ptend',a) )
      self.DATA.append( ('pch',val) )

   # ----------------------------------------------------------------
   # - Getting block 6RRRt if available
   # ----------------------------------------------------------------
   def __get000_6RRRt__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('6[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         tr  = rec[-1:]
         if tr == '/':        tr = -1
         else:                tr = int(tr)
      except:
         tr  = self.MISSING_INT
      try:
         RRR = int(rec[1:4]) 
         if   RRR ==   0:     RRR = -1 # No precipitation
         elif RRR == 990:     RRR =  0 # Not measurable
         elif RRR  > 990:     RRR = RRR - 990
      except:
         RRR = self.MISSING_NUM

      # - Where to append depends on the time
      #   stored in the tr object.
      #   0 -- nicht aufgefhrter oder vor dem Termin endender Zeitraum
      #   1 -- 6 Stunden
      #   2 -- 12 Stunden
      #   3 -- 18 Stunden
      #   4 -- 24 Stunden
      #   5 -- 1 Stunde bzw. 30 Minuten (bei Halbstundenterminen)
      #   6 -- 2 Stunden
      #   7 -- 3 Stunden
      #   8 -- 9 Stunden
      #   9 -- 15 Stunden
      if   tr == 1:        col = 'rrr6'
      elif tr == 2:        col = 'rrr12'
      elif tr == 3:        col = 'rrr18'
      elif tr == 4:        col = 'rrr24'
      elif tr == 6:        col = 'rrr2'
      elif tr == 7:        col = 'rrr3'
      elif tr == 8:        col = 'rrr9'
      elif tr == 9:        col = 'rrr15'
      elif tr == 5 and self.minute == 0:  col = 'rrr1'
      elif tr == 5:        col = 'rrr05'
      else:
         sys.exit(' Exit in __get000_6RRRt')
      self.DATA.append( (col,RRR) )
      ####self.DATA.append( ('tr',tr) )

   # ----------------------------------------------------------------
   # - Getting block 7www1w2 if available
   # ----------------------------------------------------------------
   def __get000_7www1w2__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('7[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         ww = rec[1:3];  ww = self.MISSING_INT if ww == '//' else int(ww)
         w1 = rec[3];    w1 = self.MISSING_INT if w1 == '/'  else int(w1)
         w2 = rec[4];    w2 = self.MISSING_INT if w2 == '/'  else int(w2)
      except:
         ww = self.MISSING_INT 
         w1 = self.MISSING_INT
         w2 = self.MISSING_INT
      if not ww == self.MISSING_INT: self.DATA.append( ('ww',ww) )
      if not w1 == self.MISSING_INT: self.DATA.append( ('w1',w1) )
      if not w2 == self.MISSING_INT: self.DATA.append( ('w2',w2) )

   # ----------------------------------------------------------------
   # - Getting block 8nhchcmcl if available
   # ----------------------------------------------------------------
   def __get000_8nhchcmcl__(self):
      rec = ' '.join(self.b0.split(' ')[5:])
      rec = re.search('8[0-9]{4}',rec)
      if rec == None: return
      rec = rec.group()
      try:
         nh = rec[1];  nh = self.MISSING_INT if nh == '//' else int(nh)
         ch = rec[2];  ch = self.MISSING_INT if ch == '//' else int(ch)
         cm = rec[3];  cm = self.MISSING_INT if cm == '//' else int(cm)
         cl = rec[4];  cl = self.MISSING_INT if cl == '//' else int(cl)
      except:
         nh = self.MISSING_INT
         ch = self.MISSING_INT 
         cm = self.MISSING_INT
         cl = self.MISSING_INT
      if not nh == self.MISSING_INT: self.DATA.append( ('Nh',nh) )
      if not ch == self.MISSING_INT: self.DATA.append( ('CH',ch) )
      if not cm == self.MISSING_INT: self.DATA.append( ('CM',cm) )
      if not cl == self.MISSING_INT: self.DATA.append( ('CL',cl) )


   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------


   # ----------------------------------------------------------------
   # - Getting block 1sTTT if available
   # ----------------------------------------------------------------
   def __get333_1sTTT__(self):
      rec = re.search('1[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         sign = int(rec[1]) 
         if sign == 0:    val = int(rec[-3:])
         else:            val = int(rec[-3:]) * (-1)
      except:
         val = self.MISSING_NUM
      # - Time period depends on hour
      self.DATA.append( ('tmax12',val) )

   # ----------------------------------------------------------------
   # - Getting block 2sTTT if available
   # ----------------------------------------------------------------
   def __get333_2sTTT__(self):
      rec = re.search('2[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         sign = int(rec[1]) 
         if sign == 0:    val = int(rec[-3:])
         else:            val = int(rec[-3:]) * (-1)
      except:
         val = self.MISSING_NUM
      # - Depends on hour
      if self.hour == 9:
         self.DATA.append( ('tmin15',val) )
      else:
         self.DATA.append( ('tmin12',val) )

   # ----------------------------------------------------------------
   # - Getting block 3EsTT if available
   # ----------------------------------------------------------------
   def __get333_3EsTT__(self):
      rec = re.search('3[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         E    = int(rec[1]) 
         sign = int(rec[2]) 
         if sign == 0:    val = int(rec[-2:]) 
         else:            val = int(rec[-2:]) * (-1)
      except:
         return
      self.DATA.append( ('E',E) )
      # - Depends on hour
      if self.hour == 9:
         self.DATA.append( ('tgnd15',val) )
      else:
         self.DATA.append( ('tgnd15',val) )

   # ----------------------------------------------------------------
   # - Getting block 4Esss if available
   # ----------------------------------------------------------------
   def __get333_4Esss__(self):
      rec = re.search('4[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         Eschnee = int(rec[1]) 
         self.DATA.append( ('Esnow',Eschnee) )
      except:
         Es  = self.MISSING_INT
      try:
         schnee = int(rec[-3:])
         self.DATA.append( ('snow',schnee) )
      except:
         snow = self.MISSING_INT

   # ----------------------------------------------------------------
   # - Getting block 55SSS if available
   # ----------------------------------------------------------------
   def __get333_55SSS__(self):
      records = re.findall('55[0-9]{3}',self.b3)
      if len(records) == 0: return
      for rec in records:
         if int(rec[0:3]) == 553:
            try:
               sonne = int(rec[-2:])
               self.DATA.append( ('sun',sonne) )
            except:
               sonne = self.MISSING_INT
         else:
            try:
               sonnetag = int(rec[-3:])
               self.DATA.append( ('sunday',sonnetag) )
            except:
               sonnetag = self.MISSING_INT


   # ----------------------------------------------------------------
   # - Getting block 6RRRtr if available
   # ----------------------------------------------------------------
   def __get333_6RRRtr__(self):
      rec = re.search('6[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         tr3  = float(rec[-1:])
      except:
         return 
      try:
         RR3 = int(rec[1:4])
      except:
         return 
      if RR3 == 0:
         RR3 = -1 # No precipitation
      elif RR3 == 990:
         RR3 =  0 # Not measurable
      elif RR3 > 990:
         RR3 = RR3-990
      # - If tr is not 7 this is not 3hrly sum RRR block
      #   as it should be. Stop. Else append.
      if not tr3 == 7: return
      self.DATA.append( ('rr3',RR3) )

   # ----------------------------------------------------------------
   # - Getting block 7RRRR if available
   # ----------------------------------------------------------------
   def __get333_7RRRR__(self):
      rec = re.search('7[0-9]{4}',self.b3)
      if rec == None: return
      rec = rec.group()
      try:
         RR24 = int(rec[-4:])
      except:
         return 
      if RR24 == 0:
         RR24 = -1 # No precipitation
      elif RR24 == 9999:
         RR24 =  0 # Not measurable
      self.DATA.append( ('rr24',RR24) )

   # ----------------------------------------------------------------
   # - Getting block(s) 8NsCHsHs if available
   # ----------------------------------------------------------------
   def __get333_8NsChs__(self):
      records = re.findall('8[0-9]{4}',self.b3)
      if len(records) == 0: return
      for i in range(0,len(records)):
         rec = records[i]
         try:
            Ns = int(rec[1])
         except:
            Ns  = self.MISSING_INT
         self.DATA.append( ('ca_%d' % (i+1),Ns) )
         try:
            hs = int(rec[-2:])
         except:
            hs = self.MISSING_INT
         # - Convert hs
         if   hs  <   0:        hs = hs # as it is. Missing value. 
         elif hs ==   0:        hs = 0 # lower than 30 meters
         elif hs <=  50:        hs = hs * 30 # 30m, 60m, 90m, ..., 1500m
         elif hs <=  80:        hs = (hs - 50) * 300 # 1800m, 2100m, ..., 9000m 
         elif hs <=  89:        hs = (hs - 80) * 1500 + 9000 # 10500m, ..., 21000m+
         self.DATA.append( ('ch_%d' % (i+1),hs) )

   # ----------------------------------------------------------------
   # - Getting block(s) 9SSss if available
   # ----------------------------------------------------------------
   def __get333_9SSss__(self):
      records = re.findall('9[0-9]{4}',self.b3)
      if len(records) == 0: return

      for rec in records:
         try:
            key = int(rec[0:3])
            val = int(rec[-2:])
         except:
            return 
         # - Gust last 10 min
         if   key == 910:
            # - If observations in knots: convert
            if self.knots: val = int(float(val * self.KNOTS2MS))
            self.DATA.append( ('ffx',val * 10) )
         # - Gust since last main observation time
         elif key == 911:
            # - If observations in knots: convert
            if self.knots: val = int(float(val * self.KNOTS2MS))
            self.DATA.append( ('ffx1',val * 10) )
         # - Maximum of 10min-mean wind speed since last main observation time
         elif key == 912:
            # - If observations in knots: convert
            if self.knots: val = int(float(val * self.KNOTS2MS))
            self.DATA.append( ('ffmax1',val * 10) )
         # - Mean wind speed since last main observation time
         ###elif key == 913:
         ###   # - If observations in knots: convert
         ###   if self.knots: val = int(float(val * self.KNOTS2MS))
         ###   self.DATA.append( ('w1ffmean',val * 10) )
         #### - Minimum of 10min-mean wind speed since last main observation time
         ###elif key == 914:
         ###   # - If observations in knots: convert
         ###   if self.knots: val = int(float(val * self.KNOTS2MS))
         ###   self.DATA.append( ('w1ffmin',val * 10) )
         ###elif key == 930:  
         ###   self.DATA.append( ('w1RR',val) )
         elif key == 931:
            self.DATA.append( ('newsnow',val) )


   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
      
























