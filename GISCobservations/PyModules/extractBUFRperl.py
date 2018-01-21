# -------------------------------------------------------------------
# - NAME:        extractBUFR.py
# - AUTHOR:      Reto Stauffer (IMGI@prognose2)
# - DATE:        2015-02-04
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2018-01-21 17:58 on marvin
# -------------------------------------------------------------------


import sys, os, re
from bcolors import bcolors


# -------------------------------------------------------------------
# - BUFR DESCRIPTION OBJECT to handle the bufrdesc database
# -------------------------------------------------------------------
class bufrdesc(object):
   """
   This is a small helper class. I am loading the bufrdesc database
   as a list ob such bufrdesc classes which are easily iteratable.
   Used to store each record (each row of the
   :ref:`bufrdesc database table <table-bufrdesc>` as an object which
   is easy to iterate over.

   Args:
       rec (:obj:`tuple`): A record from the bufrdesc database table.
            The elements of the :obj:`tuple` are described
            by the second input argument ``cols``.
       cols (:obj:`list`): List of :obj:`str` describing the elements
            in the first argument (rec :obj:`tuple`).
   """
   
   # ----------------------------------------------------------------
   # - Store elemenets
   # ----------------------------------------------------------------
   def __init__(self,rec,cols):
      self.rec  = rec
      self.cols = cols
      # - Loading necessary elements
      self.bufrid = int(self.get('bufrid'))
      self.param  = self.get('param')
      self.desc   = self.get('desc')
      self.unit   = self.get('unit')
      self.offset = float(self.get('offset'))
      self.factor = float(self.get('factor'))

   # ----------------------------------------------------------------
   # - shows content 
   # ----------------------------------------------------------------
   def show(self):
      """
      Shows content of the object
      """
      print "    Content of the bufrdesc object:"
      print "    %-15s %d"   % ("%s:"%"BUFR ID",     self.bufrid )
      print "    %-15s %s"   % ("%s:"%"Parameter",   self.param  )
      print "    %-15s %s"   % ("%s:"%"Description", self.desc   )
      print "    %-15s %s"   % ("%s:"%"Unit",        self.unit   )
      print "    %-15s %.2f" % ("%s:"%"Offset",      self.offset )
      print "    %-15s %.2f" % ("%s:"%"Factor",      self.factor )

   # ----------------------------------------------------------------
   # - Helper class loading element
   # ----------------------------------------------------------------
   def get(self,what):
      """
      Returns element corresponding to input string 'what'. 
      If we cant find it in the columns from the database: stop!

      Args:
        what (:obj:`str`): Element to be returned.

      Returns:
        Returns the corresponding element if available, else stop.
      """
      try:
         i = self.cols.index( what )
      except Exception as e:
         print e
         sys.exit("[!] ERROR in object bufrdesc. Cannot find %s" % what)
      return self.rec[i]
      

# -------------------------------------------------------------------
# - BUFR ENTRY OBJECT to handle/parse the lines.
# -------------------------------------------------------------------
class bufrentry(object):
   """
   This is a small helper class. I store all entries from the
   bufr file in such bufrentry classes. A bufrenry class contains
   the specification of one single message.
   E.g., bufrid, value, description.

   Args:
      string (:obj:`str`): A bufrentry is a line as extracted by
        the Geo::BUFR bufrread.pl perl script.
      width (:obj:`int`): bufrread.pl allows to set a width for the
        description column. This width has to be known by :class:`bufrentry`
        to be able to properly extract the information from this line.
   """

   MISSING_VALUE = -9999.

   # ----------------------------------------------------------------
   # - Init. Does all you have to know.
   # ----------------------------------------------------------------
   def __init__(self,string,width):

      try:
         self.count  = int(string[0:6])
         self.bufrid = int(string[7:14])
         self.value  = str(string[15:(16+width)]).strip().upper()
         self.desc   = str(string[(16+width):]).strip().upper()
      except Exception as e:
         import sys
         print e
         print string
         sys.exit('ERROR in bfrentry class. Cannot extract necessary infos from \n%s\n' % string)

      # - Extracting unit from description
      tmp = re.findall(r'\[([^]]*)\]',self.desc)
      if len(tmp) == 0: sys.exit('CANNOT EXTRACT UNIT FROM STRING \"%s\"' % self.desc)
      # - Take first element as unit
      self.unit = '%s' % tmp[0]
      # - Remove unit from description
      self.desc = self.desc.replace("[%s]" % self.unit,"").strip()
      
      if self.value.strip().upper() == 'MISSING':
         self.value = self.MISSING_VALUE 
      elif self.unit.upper().find('CCITTIA5') >= 0:
         self.value = self.value.strip().replace('"','')
      else:
         self.value = float(self.value)

   # ----------------------------------------------------------------
   # - Helper function to show recotrd if necessary
   # ----------------------------------------------------------------
   def show(self):
      """
      Allows to print the content of this object, mainly for development.

      Returns:
        No return, creates output on stdout.
      """

      print "    - BUFR ENTRY:"
      print "      Count:       %6d"  % (self.count)
      print "      Bufrid:      %06d" % (self.bufrid)
      if type(self.value) == type(str()):
         print "      Value:       %s"   % (self.value)
      else:
         print "      Value:       %f"   % (self.value)
      print "      Description: %s"   % (self.desc)
      print "      Unit:        %s"   % (self.unit)


   def string(self):
      """
      Helper method to output the content of this object to console.

      Returns:
         Returns the information from the object in a string format.
      """
      x = " -- %3d %06d %-42s %-15s" % (self.count,self.bufrid,self.desc[0:40],self.unit)
      if type(self.value) == type(str()):
         x = '%s %s' % (x,self.value)
      else:
         x = '%s %f' % (x,self.value)
      return x


# -------------------------------------------------------------------
# - The main extractBUFR data class. 
# -------------------------------------------------------------------
class extractBUFR( object ):
   """
   Main class, extracting data from the BUFR file.

   This object uses `subprocess.Popen` to call the Geo::BUFR bufrread.pl
   file (see `<http://search.cpan.org/dist/Geo-BUFR/lib/Geo/BUFR.pm>`_,
   `<https://wiki.met.no/bufr.pm/start>`_). If not installed None will
   be returned. To install Geo::BUFR check the readme of the package.
   It is as simple as:

   .. code-block:: bash

     cpan Geo::BUFR

   Please note that you will also have to have the BUFRTABLES installed on
   your system at either one of the default locations or by setting the
   environment variable ``BUFR_TABLES=<path>`` corresponding to the location
   of the bufr files.

   BUFR Tables can e.g. be downloaded here:
   <https://software.ecmwf.int/wiki/display/BUFR/BUFRDC+Home>`_. The files in
   this archive are named ``.txt`` while ``.TXT`` files are expected. bufrread.pl
   will drop a corresponding message. Simply link the ``.txt`` files to a corresponding
   ``.TXT`` version in your BUFR_TABLES folder to get around this.

   Args:
      config (:obj:`str`): Name of the config file.
      stint (:obj:`str`): Used to store a flag into the database
        from which source the messages come. In this case "bufr".
        Keep in mind that the database column type is "ENUM" and
        only allows a distinct set of strings.
      verbose (:obj:`bool`): Boolean True/False whether the object
        should be verbose or not.
      filterfile (:obj:`str`): Default is None, a filter file can be
        specified forwarded to Geo::BUFR bufrread.pl.
   """

   # Width used for the ACII output format from bufrread.pl
   WIDTH         = 40
   # Replace 'missing' string with this value.
   MISSING_VALUE = -9999.
   # Attribute used to store the database handler later on
   db            = None
   # Whether or ont the object should be verbose or not.
   VERBOSE       = True

   # ----------------------------------------------------------------
   # - Initializing extractBUFR object first
   # ----------------------------------------------------------------
   def __init__(self,file,config,stint,verbose,filterfile=None):

      import os
      os.environ['TZ'] = 'UTC'
      self.file = file

      self.VERBOSE    = verbose
      self.stint      = stint
      self.filterfile = filterfile

      if not os.path.isfile( file ):
         sys.exit('Sorry, cannot find file %s' % file)

      # - Save config
      self.config = config
      self.raw   = self.__read_bufr_file__(file)

      # - Connect to database
      self.dbConnect() 

      # - Check if bufrdesc table exists containing the
      #   parameter description for all data ever pushed into
      #   the database. If not existing, create.
      self.db.__check_or_create_table__('bufrdesc',config['mysql_bufrdesc_create'])

      # - Loading bufrdesc data and store object list
      self.bufrdesc = self.load_bufr_description('bufrdesc')

      # - If self.raw == None:
      #   Setting self.error = True indicating that
      #   we could not read the data.
      if self.raw == None:
         self.error = True
      else:
         self.error = False

      # - Dict to store the values later on
      self.keys = [] # stor all unique keys
      self.data = [] # store data dicts
      self.dropped = [] # store dropped items 


   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def load_bufr_description( self, table ):
      """
      Loading data from 'table' and returns a list object containing
      one 'bufrdesc' object for each of the rows in the database.

      Args:
        table (:obj:`str`): Name of the database table containing
            the bufr descriptions.

      Returns:
        list: Returns a list of :obj:`bufrdesc` objects containing
        the definition/description.
      """
      cur = self.db.cursor()
      cur.execute( "SELECT * FROM %s" % table )
      tmp  = cur.description
      data = cur.fetchall()

      # List with columns (in order as selected)
      cols = []
      for rec in tmp: cols.append( rec[0] )

      # Append to results list   
      res = []
      for rec in data:
         res.append( bufrdesc( rec, cols ) )

      return res

   # ----------------------------------------------------------------
   # - Reading bufr file
   # ----------------------------------------------------------------
   def __read_bufr_file__(self,file,filterfile=None):
      """
      Function reading the BUFR file. Actually calling the perl
      Geo::BUFR library to convert the binary files into ASCII table
      and pase the output to extract the necessary information.

      Args:
        file (:obj:`str`): Path/Name of the BUFR file (binary file).
        filterfile (:obj:`str`): Default None, dan be set and will be
            forwarded to Geo::BUFR bufrread.pl to set specific filters.
            If set only this subset of the bufr file will be extracted/processed.

      Returns:
         list: Returns a list of lists, each containing a set of :obj:`bufrentry`
         objects. The length of the most outer list corresponds to the number
         of messages in the BUFR file. The first nested lists are the messages
         each consisting of a set of :obj:`bufrentry` entries with the data.
      """

      import os
      import subprocess as sub

      #### NOTE: not calling perl bufrread.pl. bufrread.pl
      #### shuld be installed in /usr/locale/bin/bufrread.pl and
      #### can be called directly
      cmd = ['bufrread.pl',file,'--on_error_stop', \
             '--data_only','--width','%d' % self.WIDTH]
      if filterfile:
         cmd.append("--filter"); cmd.append(filterfile)

      if self.VERBOSE: print "[]-> Calling: %s" % " ".join(cmd)
      p = sub.Popen(cmd,stdout=sub.PIPE,stderr=sub.PIPE)
      out, err = p.communicate()
      if not p.returncode == 0:
         print out
         print err
         print 'subprocess reading BUFR with perl script returned error.'
         return None 

      content = out.split('\n')

      # - Store the "sections" from content to dict array
      all_sections = []
      tmp = []
      in_data_section = False
      for line in content:
         if line.find('Subset') >= 0:
            # - Indicate that we are in the "data" section now.
            in_data_section = True
            # - Store last subset if allready read one
            if len(tmp) > 0: all_sections.append( tmp )
            # - Resetting temporary dict to store the content
            #   for the section we have found
            tmp = []
            continue
         # - End of section (if we are in_data_section)
         elif line.find('Message') >= 0:
            in_data_section = False
            # - Store last subset if allready read one
            if len(tmp) > 0: all_sections.append( tmp )
            # - Resetting temporary dict to store the content
            #   for the section we have found
            tmp = []
            continue
         elif not in_data_section: continue
         elif len(line.strip()) == 0: continue
   
         # - Else store the information to tmp
         entry = bufrentry(line,self.WIDTH)
         tmp.append( entry )

      # - Appending last section to all_sections
      all_sections.append(tmp)

      return all_sections


   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def __getval__(self,x):
      """
      Get value: if the value is a string: simply return.
      Else convert value to :obj:`float`. If the value is extremely
      large or extremely small: return ``MISSING_VALUE``.

      Returns:
        Properly prepare the value.
      """
      if type(x) == type(str()):
         return x 
      if float(x) < -1.e20 or float(x) > 1.e20:
         return self.MISSING_VALUE
      return float(x)


   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def extractdata(self):
      """
      Looping trough self.raw (raw information returned by
      __read_bufr_file__ and prepares the data.
      """

      import sys

      # - If no parameters defined in the config: return nothing.
      if len(self.config['parameter']) == 0:
         return

      # - Looping over all sections
      for sec in range(0,len(self.raw)):

         if self.VERBOSE: print "    - Extracting section %d/%d" % (sec,len(self.raw))

         tmp_sec = {}

         # - First of all the displacement time is 0 (for observations
         #   valid for a certain time).
         displacement = 0

         # - Sensor height, set to -999 if not specified yet.
         sensorheight = -9

         # - Similar to the displacement there are some variables (cloud cover
         #   and cloud type) on different levels. These levels are called
         #   008002 VERTICAL SIGNIFICANCE (see code table 0 08 002). I'll 
         #   store the latest verticalsign on a variable so that we can
         #   map cloud amounts and cloud types to one of these levels.
         verticalsign = -9

         # - Looping trough the RAW data dict scanning the 
         #   entries we got. If we cannot find, drop (store
         #   on 'dropped'). Else store on self.data
         for rec in self.raw[sec]: 

            if self.VERBOSE: print '%6d %s' % (displacement,rec.string())
            if rec.value == self.MISSING_VALUE: continue

            # - Check if current message defines a displacement time.
            #   if it does, return value will be integer (seconds)
            #   defining the current displacement time/period.
            #   Else return 'false' -> than it is an observation
            #   and we have to search for the parameter name.
            check_displacement = self.__check_displacement__(rec)
            if not check_displacement == False:
               displacement = check_displacement
               #print '     + set displacement time to %8d' % displacement
               continue

            # - Checking sensor height
            check_sensorheight = self.__check_sensorheight__(rec)
            if not check_sensorheight == False:
               sensorheight = check_sensorheight
               #print '     + set sensorheight to %10.2f' % sensorheight
               continue

            # - Check if current message defines a vertical significance
            #   layer. If it does, save the value onto verticalsign and
            #   jump to the next message.
            check_verticalsign = self.__check_verticalsign__(rec)
            if not check_verticalsign == False:
               verticalsign = check_verticalsign
               # print '     + set vertical significance to %8d' % verticalsign
               continue

            # - Returns paramclass object if found 
            drop, param = self.__get_param_obj__( rec, displacement, verticalsign, sensorheight )
         
            # - Dropped: Ignore current entry and go further
            if drop:
               drop = '%5d  %06d %7.2fm \"%s\" (%s)' % (displacement,
                      rec.bufrid, sensorheight, rec.desc, rec.unit)
               if not drop in self.dropped:
                  self.dropped.append( drop )
               continue

            if self.VERBOSE: print '        -- %s' % param.name

            # - Load/scale data 
            data = rec.value 
            if type(data) == type(float()):
               # - Do not scale missing value.
               if not data == self.MISSING_VALUE:
                  if not param.offset == False: data = data + param.offset
                  if not param.factor == False: data = data * param.factor

            # - If 'repeat' is not set to True we can easily
            #   add this parameter to the list.
            if not param.repeat:
               tmp_sec[ param.name ] = data
               # - Appending unique keys
               if not param.name in self.keys: self.keys.append( param.name )
            # - If this is a repeat parameter we have to search for
            #   the occurance of param.nameX in the tmp_sec. Increase
            #   index if necessary and add.
            else:
               for i in range(0,100):
                  rep_name = '%s_%d' % (param.name,i)
                  if not rep_name in tmp_sec: break 
               tmp_sec[ rep_name ] = data
               # - Appending unique keys
               if not rep_name in self.keys: self.keys.append( rep_name )

            # - Check if current bufrentry is already in the bufrdesc
            #   database (has its equivalent in self.bufrdesc). If not,
            #   we have to insert a new line into the obs.bufrdesc table.
            self.__check_bufrdesc_and_add_if_necessary__(rec,param)
   

         # - Append full block to self.data
         self.data.append( tmp_sec )


   # ----------------------------------------------------------------
   # - Check and extends bufrdesc table if necessary
   # ----------------------------------------------------------------
   def __check_bufrdesc_and_add_if_necessary__(self,rec,param):
      """
      Adding bufr entry to database table :ref:`bufrdesc <table-bufrdesc>` if
      necessary.  Input rec is a bufrentry object.  Input param has to be of
      class paramclass.  Checks if entry is already in the bufrdesc database.
      If not, we have to add a row.

      Args:
        rec (:class:`bufrentry`): Object to be added.
        param (:class:`bufrdesc`): Bufr description object.
      """
      desc = None
      for elem in self.bufrdesc:
         if param.name == elem.param:
            desc = elem
            break;
      
      # - If not found:
      if desc == None:
         print "    %s not in bufrdesc database: append row" % param.name

         # - Pick period, offset, and factor
         if param.period == False:
            period = 0.
         else:
            period = param.period
         if param.factor == False:
            factor = 0.
         else:
            factor = param.factor
         if param.offset == False:
            offset = 0.
         else:
            offset = param.offset
         # - Picking name and unit
         bufrid = rec.bufrid 
         desc   = rec.desc
         unit   = rec.unit 

         # - Create sql statement
         sql = []
         sql.append("REPLACE INTO bufrdesc")
         sql.append("(`bufrid`,`param`,`desc`,`unit`,`period`,`offset`,`factor`) VALUES")
         sql.append("(%d,'%s','%s','%s',%d,%f,%f)" % (bufrid,param.name,desc,unit, \
                  period,offset,factor))

         ###print "\n".join(sql)
         ###rec.show()
         ###param.show()
         ###sys.exit()

         # - Write to database
         cur = self.db.cursor()
         cur.execute( "\n".join(sql) )

   # ----------------------------------------------------------------
   # - Check if current message contains a displacement time/period.
   #   If not, return False. Else return displacement time in
   #   seconds. 
   # ----------------------------------------------------------------
   def __check_displacement__(self,rec):
      """Check if current record is a time displacement specification.
      If so the value of the time displacement value will be returned
      as :obj:`int` in seconds. If not :obj:`bool` ``False`` is returned.

      Args:
          rec (:class:`bufrentry`): Object to check.

      Returns:
          Returns :obj:`bool` ``FALSE`` or :obj:`int`.
      """

      is_displacement = False
      if rec.bufrid in [004024,004025]:
         is_displacement = True
      elif rec.desc.find("TIME PERIOD OR DISPLACEMENT") >= 0:
         is_displacement = True
      
      # - No displacement entry?
      if not is_displacement: return False


      if not rec.value: return False
      if rec.value == self.MISSING_VALUE: return False

      # - Unit
      if rec.unit in ['H','HOUR']:
         period = rec.value * 3600
      elif rec.unit in ['M','MIN','MINUTE']:
         period = rec.value * 60
      elif rec.unit in ['S','SEC','SECOND']:
         period = rec.value * 60
      elif rec.unit in ['D','DAY']:
         period = rec.value * 86400

      ###print "  [---]  %f %s -> %f " % (rec.value, rec.unit, period)

      return abs(int( period ))


   # ----------------------------------------------------------------
   # Check if entry is sensor height. Required as different temperatures
   # have the same BUFRID but are for different heights (e.g., 2m or
   # 0.05m temperatures).
   # ----------------------------------------------------------------
   def __check_sensorheight__(self,rec):
      """Check if current record is a sensorheight specification.
      If so the value of the sensorheight value will be returned
      (float). If not a :obj:`bool` ``False`` is returned.

      Args:
          rec (:class:`bufrentry`): Object to check.

      Returns:
          Returns :obj:`bool` ``FALSE`` or :obj:`float`.
      """

      is_sensorheight = False
      if rec.bufrid in [00703]:
         is_sensorheight = True
      elif rec.desc.find("HEIGHT OF SENSOR ABOVE LOCAL GROUND") >= 0:
         is_sensorheight = True
      
      # - No sensorheight entry?
      if not is_sensorheight: return False

      if not rec.value: return False
      if rec.value == self.MISSING_VALUE: return False

      # Return float sensor height
      return float(rec.value)


   # ----------------------------------------------------------------
   # - Check if current message contains a vertical significance layer
   #   information. If not, return False. Else return value. 
   # ----------------------------------------------------------------
   def __check_verticalsign__(self,rec):
      """Check if current record is a vertical significance specification.
      If so the value of the vertical significance value will be returned
      (absolute value as integer). If not a :obj:`bool` ``False`` is returned.

      Args:
          rec (:class:`bufrentry`): Object to check.

      Returns:
          Returns :obj:`bool` ``FALSE`` or :obj:`int`.
      """

      is_verticalsign = False
      if rec.bufrid == 8002:
         is_verticalsign = True
      elif rec.desc.find("VERTICAL SIGNIFICANCE") >= 0:
         is_verticalsign = True
      
      # - No verticalsign entry?
      if not is_verticalsign: return False


      if not rec.value: return False
      if rec.value == self.MISSING_VALUE: return False

      return abs(int( rec.value ))

   # ----------------------------------------------------------------
   # - Show data
   # ----------------------------------------------------------------
   def __get_param_obj__(self,search,displacement,verticalsign,sensorheight):
      """The config file :file:`bufr_config.conf` contains a set of
      parameter definitions. This method is used to finde the appropriate
      parameter description given the inputs which directly come from the
      BUFR entry extracted from the BUFR file using Geo::BUFR buffread.pl.

      We are therefore matching each data line from the BUFR file with one
      of our specified parameter configs from the :file:`bufr_config.conf`
      and use them to further process the data.

      Args:
        search (:obj:`burentry`): Bufrentry object.
        displacement (:obj:`int`): Lates time displacement value, seconds.
        verticalsign (:obj:`int`): Latest vertical significance value.
        sensorheight (:obj:`float`): Latest sensor height value.

      Returns:
         Returns two values, the first one is a :obj:`bool` whether to
         drop the message or not. If no parameter entry can be matched to
         the current bufrentry this value is ``True`` (drop message, unknown).
         Else ``False`` will be returned (don't drop). The second argument
         is :obj:`bool` False if we cannot find the parameter entry, or
         a parameter entry of class :class:`bufrdesc` else.
      """

      param = False
      drop  = True
      import numpy as np

      # -------------------------------------------------------------
      # - First looping trough and searching for bufrid matching.
      # -------------------------------------------------------------
      for rec in self.config['parameter']:
         if search.bufrid == rec.bufrid:

            param = rec

            # If all additional parameters are 'False' we'll take
            # this 'param'. Break and return.
            if type(rec.period)       == type(False) and \
               type(rec.verticalsign) == type(False) and \
               type(rec.sensorheight) == type(False):
               break

            # - Else checking additional parameters which have to fit
            check = []
            if rec.period:
               if rec.period == displacement:       check.append(True)
               else:                                check.append(False)
            if rec.sensorheight:
               if sensorheight in rec.sensorheight: check.append(True)
               else:                                check.append(False)
            if rec.verticalsign:
               if verticalsign in rec.verticalsign: check.append(True)
               else:                                check.append(False)

            # If at least one is False: kick
            if not np.all( check ):
               param = False
            else:
               break


      # - Prepare parameter
      if param == False:
         return drop, param

      # - Else prepare return
      return False, param


   def manipulatedata(self):
      """Manipulate data. Is looking for some meta information such as
      ``wmoblock``, ``statnr``, ``year``, ``month``, ``hour``, and ``minute``
      and creates the columns ``datumsec`` (unix time stamp), ``stdmin``
      (hour/minute integer, e.g., 7:00 UTC is 700), and ``statnr`` (a combination
      of the wmoblock and station number information from the bufr file).
      """

      if len(self.data) == 0:
         print '[!] Cannot manipulate data - no data loaded yet.'
         return

      # - Store sections to drop (if time information wrong)
      to_drop = []

      # - Kees we need
      necessary = ['wmoblock','statnr','year','month','hour','minute']

      # - Check if keys exist and manipulate if necessary.
      for sec in range(0,len(self.data)):

         # - Take out record
         rec       = self.data[sec]
         keys      = rec.keys()
         skip_this = False

         # - If one of the necessary keys is missing, append
         #   section index to 'to_drop' and set skip_this = True.
         #   If skip_this is True: continue afterwards.
         #   'to_drop' sections will be removed at the end.
         for nec in necessary:
            if not nec in keys:
               print 'UPS: missing key \"%s\" in \"%s\" drop.' % (nec,self.file.split("/")[-1])
               to_drop.append(sec)
               skip_this = True
               break

         # - Skip 
         if skip_this: continue

         # - Manipulate station
         rec['statnr'] = rec['wmoblock']*1e3 + rec['statnr']
   
         # - Create different date formats
         from datetime import datetime as dt
         if rec['year'] < 0 or rec['month'] < 1 or rec['day'] < 1 or rec['hour'] < 0 or \
            rec['hour'] > 24 or rec['minute'] < 0 or rec['minute'] > 60:
            print '[!] Problems with time description! Fancy values. Skip this.'
            
            print "   Year: %4d Month: %2d Day: %2d Hour: %2d Minute: %2d" % \
                  (rec['year'],rec['month'],rec['day'],rec['hour'],rec['minute'])

            # - Remove this entry from self.data!
            #   We cannot do this here because then the loop index
            #   will get crazy. Therefore mark this section as
            #   'to drop'. We do that at the end of the manipulation
            #   method.
            to_drop.append(sec); continue

         # - Everything ok with date, convert.
         date = dt(int(rec['year']),int(rec['month']),int(rec['day']), \
                   int(rec['hour']),int(rec['minute']) )
         
         # - Store date/time
         rec['datumsec']  = int(date.strftime('%s'))
         rec['datum']     = int(date.strftime('%Y%m%d'))
         rec['stdmin']    = int(date.strftime('%H%M'))
   
         del rec['wmoblock']
         del rec['year']
         del rec['month']
         del rec['day']
         del rec['hour']
         del rec['minute']

         # - Write block back 
         self.data[sec] = rec

      # - If there were sections with corrupt date/time info,
      #   drop them.
      print '    Dropping %d messages from totally %d' % (len(to_drop),len(self.data))
      if len(to_drop) > 0:
         hold = self.data; self.data = []
         for sec in range(0,len(hold)):
            if not sec in to_drop: self.data.append( hold[sec] )

      # - No messages left?
      if len(self.data) == 0: return False

      print "    Leftover (valid messages): %d" % (len(self.data))

      # - Remove from keys
      self.keys.remove('wmoblock')
      self.keys.remove('year')
      self.keys.remove('month')
      self.keys.remove('day')
      self.keys.remove('hour')
      self.keys.remove('minute')

      return True 


   def prepare_data( self ):
      """Prepares the data.
      Puts the data we found bevore in the single messages into
      a matrix style variable called "res". Stores parameter
      (column description of the matrix) and the data matrix into
      self.PREPARED.
      """

      res = ()
      par = []
      # - First check out how many different parameter we have in the
      #   data.
      for rec in self.data:
         for key in rec.keys():
            if key in self.config['dbskip']:
               continue
            elif not key in par:
               # - Append column/parameter
               par.append( key )

      # - Create numpy matrix to store all the values
      import numpy as np
      res = np.ndarray( (len(self.data),len(par)), dtype="float" )

      self.db.__check_columns__(par)

      # - Create empty results array and fill
      #   with emptyvalues from the setup file
      res[:,:] = None

      # - Fill in the data
      for r in range(0,len(self.data)):
         for key in self.data[r].keys():
            if self.data[r][key] == self.MISSING_VALUE: continue
            if not key in par: continue
            c = par.index( key )
            res[r,c] = self.data[r][key]

      self.PREPARED = {'parameter':par,'data':res}

      # - If verbose, show data which we would like to insert
      #   into the database.
      if self.VERBOSE:
         print "    PREPARED DATA FOR DATABASE:"

         for i in range(0,len(self.PREPARED['parameter'])):
            print "    - %-10s " % self.PREPARED['parameter'][i],
            for j in range(0,len(self.PREPARED['data'])):
               val = self.PREPARED['data'][j][i],
               if np.isnan(val): val = -999
               print "%12d " % val, 
            print ""


   # ----------------------------------------------------------------
   # - Write the data we have found into the database now.
   # ----------------------------------------------------------------
   def write_to_db(self):
      """Write data to database.
      """

      if self.db == None:
         print '[!] Database connection not established. Return.'
         return

      # - No data?
      if self.PREPARED['data'].shape[0] == 0:
         print '    No data to write into the database.'
         return

      # - Columns
      columns = self.PREPARED['parameter']
      self.db.__check_columns__( columns )

      # - Prepare update statement
      update = []
      for col in columns: update.append('%s=VALUES(%s)' % (col,col))

      sql = []
      sql.append('INSERT INTO %s'        % self.db.table)
      sql.append('  (msgtyp,stint,%s) VALUES'  % ', '.join( columns ))
      sql.append('  (\'%s\',\'%s\',%s)'  % (self.db.type, self.stint, ', '.join( ['%s']*len(columns))) )
      sql.append('ON DUPLICATE KEY UPDATE ucount=ucount+1, ')
      sql.append('  %s' % ", ".join( update ))


      data = []
      import numpy as np
      for i in range(0,self.PREPARED['data'].shape[0]):
         df = self.PREPARED['data'][i,].tolist()
         for i in range(0,len(df)):
            if np.isnan( df[i] ): df[i] = None
         data.append( df )
         #data.append( tuple(self.PREPARED['data'][i,]) )

      print "    Write %d entries into the database" % len(data)
      cur = self.db.cursor()
      cur.executemany( '\n'.join(sql), data )



   # ----------------------------------------------------------------
   # - Update stations table
   # ----------------------------------------------------------------
   def update_stations( self ):
      """Update station database. Update the station database with the
      information from the bufr message. Plase note that we do simply
      update the database row and do not take care of history (e.g.,
      if a station would be renamed or moved the latest name/location
      will be stored and the old information is simply overwritten).
      """

      print "\n  * Update stations table in the database"

      cur = self.db.cursor()
      cur.execute( "SELECT statnr FROM stations" )
      tmp = cur.fetchall()
      stations = []
      for rec in tmp: stations.append( int(rec[0]) )

      res = []
      for rec in self.data:
         # - If in database: skip
         try:
            if rec['statnr'] in stations: continue
         except:
            continue
         # - Else create tuple and append to res
         try:
            tmp = (rec['statnr'],0,rec['stationname'], \
                   "%f10.4" % rec['lon'], "%f10.4" % rec['lat'], \
                   rec['height'],rec['hbaro'])
         except:
            continue # if something was missing
         # - Append now
         res.append( tmp )

      # - Update
      print "    Updating stations database table: adding %d stations" % len(res)
      sql = "INSERT INTO obs.stations (statnr,nr,name,lon,lat,hoehe,hbaro) " + \
            "VALUES (%s,%s,%s,%s,%s,%s,%s)"
      cur.executemany( sql, res )


   # ----------------------------------------------------------------
   # - Show dropped entries 
   # ----------------------------------------------------------------
   def showdropped(self):
      """If a bufrentry cannot be attributed (is not defined by bufr_config.conf)
      we will ignore these lines. To see what has been dropped and whether there
      is important information being dropped the dropped lines will be kept.

      This method allows to print the dropped lines to stdout.
      """

      if len( self.dropped ) == 0:
         print '\n    NO DROPPED ENTRIES/VARIABLES AT THE MOMENT\n\n'

      print '\n    DROPPED THE FOLLOWING ENTRIES/VARIABLES (not defined in config)'
      for rec in self.dropped:
         print '    - %s' % rec
      print ''


   # ----------------------------------------------------------------
   # - Getting output sort order - if set. 
   # ----------------------------------------------------------------
   def __showdata_sort_order__(self,force=None):
      """Takes care of the order of the columns in the output.
      """
   
      if not self.config['sortorder']: return self.data.keys()

      # - Else create new sort list
      if force == None:
         sort = []
      elif type(force) == type(list()):
         sort = force
      else:
         sys.exit('Problem in __showdata_sort_order__. Force was set, but was no list!')
      keys = self.keys
      
      # - Loop trough user defined sort order. If user defined key
      #   is in self.data: append. Else skip.
      for rec in self.config['sortorder']:
         if rec in self.config['showskip']: continue
         if rec in keys: sort.append(rec)

      # - Now loop trough all keys. If a key is not allready in
      #   the sort list: append.
      for rec in keys:
         if rec in self.config['showskip']: continue
         if not rec in sort: sort.append( rec )

      return sort


   # ----------------------------------------------------------------
   # - Show data
   # ----------------------------------------------------------------
   def showdata(self):
      """
      Helper function to print the data to stdout.
      """

      # - No data?
      if len(self.data) == 0:
         print '[!] NO DATA TO SHOW RIGHT NOW!'
         return

      # - Create key sort list 
      column_order = self.__showdata_sort_order__(force=['statnr','datum','stdmin','datumsec'])

      # - Flag to indicate if head was allready printed or not.
      head_shown = False

      # - Looping over all observations we hve found first (Dates)
      #   And show date, station number and position and such shit.
      for sec in range(0,len(self.data)):

         # - Take record
         rec = self.data[sec]

         if not head_shown:
            head_shown = True
            # - If there are data: show data
            if len(self.data) > 0:
               for col in column_order: 
                  print ' %7s' % col,
               print '\n',

         # - If there are data: show data
         for col in column_order:
            if not col in rec.keys():
               print " %7.1f" % self.MISSING_VALUE,
            else:
               value = self.__getval__( rec[col] )
               print ' %7.1f' % value, 
         print '\n',


   def dbConnect(self):
      """Method to open the database connection. Uses the settings
      on self.config. No return, saves the database handler on the
      object itself.
      """
   
      if self.db == None:
         if self.VERBOSE: print '  * Establishing database connection' 
         from database import database
         self.db = database(self.config,type='bufr')
      else:
         if self.VERBOSE: print '    Database connection already open.' 

   def cursor(self):
      """
      Alias for MySQLdb.close.
      
      Returns:
        Returns a MySQL.cursor object.
      """
      self.db.db.commit()
      return self.db.db.cursor()
   def commit(self):
      """
      Alias for MySQLdb.commit.
      """
      self.db.db.commit()
   def dbClose(self):
      """
      Alias for MySQLdb.close.
      """
      if self.VERBOSE: print '    Close database connection'
      self.db.db.close()


























