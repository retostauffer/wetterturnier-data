# -------------------------------------------------------------------
# - NAME:        paramclass.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-08
# -------------------------------------------------------------------
# - DESCRIPTION: A class where I store all the parameters from the
#                config file on. Need it to translate the
#                parameter names and duration stuff into
#                nice parameter names while scanning the BUFR file.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-08, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-27 13:48 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------



class paramclass( object ):

   def __init__(self,name,search,bufrid,offset,factor,period,sensorheight,verticalsign,repeat):

      self.name         = name
      self.search       = search
      self.bufrid       = bufrid
      self.offset       = offset
      self.factor       = factor
      self.repeat       = repeat
      self.verticalsign = verticalsign
      self.sensorheight = sensorheight

      # - Parsing period, if set.
      if not period:
         self.period = period
      else:
         try:
            p,u = period.split(' ')
            self.period = int(p)
         except Exception as e:
            print(e)
            import sys
            sys.exit('paramclass: cannot parse period %s correctly!' % period) 

         # - Unit
         if u.strip().upper() in ['H','HOUR']:
            self.period = self.period * 3600
         elif u.strip().upper() in ['M','MIN','MINUTE']:
            self.period = self.period * 60
         elif u.strip().upper() in ['S','SEC','SECOND']:
            self.period = self.period * 60
         elif u.strip().upper() in ['D','DAY']:
            self.period = self.period * 86400

         self.period = abs(int( self.period ))

   def show(self):

      print("    - PARAMCLASS ENTRY:")
      print("      Name:     %s" % self.name)
      print("      Search:   %s" % self.search)
      print("      BufrID:   %06d" % self.bufrid)
      print("      Offset:   ",self.offset)
      print("      Factor:   ",self.factor)
      print("      Period:   ",self.period," (%d h)" % int(self.period/60))
      print("      height:   ",self.sensorheight)




