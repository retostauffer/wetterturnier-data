# -------------------------------------------------------------------
# - NAME:        synopsymbol.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-12
# -------------------------------------------------------------------
# - DESCRIPTION: Small library handling the plot for synop symbol.s
#                Main class is synopsymbol.
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-12, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-06-22 21:36 on prognose2
# -------------------------------------------------------------------

import logging
log = logging.getLogger(__name__)

import drawbarb

class synopsymbol( drawbarb.drawbarb ):
   """!Synopsymbol class extending the drawbarb class drawing the
   vector wind barbs onto the figure."""

   def __init__( self, config ):
      """!Initialize a synopsymbol class. Inputs needed: config from
      @see readconfig.readconfig. It contains the fonts and other stuff
      we need later.
      @return Returns the initialized class itself."""

      self.config = config
      self.data = {}


   # ----------------------------------------------------------------
   # Appending data
   # ----------------------------------------------------------------
   def addValue( self, key, value ):

      key=key.lower()
      if not type(value) == type(int()) and not type(value) == type(float()):
         self.exit("Only integer and float arguments allowed for addValues")
      if key in self.data.keys():
         log.warning("\"%s\" has already been added. Overwrite." % key)
      self.data[key] = value


   # ----------------------------------------------------------------
   # Shows stored values, development/logging function.
   # ----------------------------------------------------------------
   def showValues(self):
      log.info("Values added to the class:")
      for key,val in self.data.iteritems():
         log.info("  - %-10s %6.2f" % (key,val))


   # ----------------------------------------------------------------
   # Draw the symbol now
   # ----------------------------------------------------------------
   def drawSymbol( self, file="out.png" ):

      import os, sys
      outfile = os.path.join( self.config.outdir, file )
      log.info("[+] Create new figure:   %s" % outfile)

      # Open figure
      self._open_figure_()

      # day and hour
      if "day" in self.data:
         self._draw_day_value_( self.data['day'] )
      if "hour" in self.data:
         self._draw_hour_value_( self.data['hour'] )

      # Now adding the different things. There are small subfunctions
      # handling the different elements.
      if "cc" in self.data:
         self._draw_cloudcover_symbol_( self.data['cc'] )
      else:
         self._draw_cloudcover_noobs_()
      if "ch" in self.data:
         self._draw_cloudhigh_symbol_( self.data['ch'] )
      if "cm" in self.data:
         self._draw_cloudmid_symbol_( self.data['cm'] )
      if "cl" in self.data:
         self._draw_cloudlow_symbol_( self.data['cl'] )
      if "t" in self.data:
         self._draw_temperature_value_( self.data['t'] )
      if "td" in self.data:
         self._draw_dewpoint_value_( self.data['td'] )
      if "pmsl" in self.data:
         self._draw_pressure_value_( self.data['pmsl'] )
      if "pch" in self.data:
         self._draw_pressurechange_value_( self.data['pch'] )
      if "ptend" in self.data:
         self._draw_pressurechange_symbol_( self.data['ptend'] )
      if "ww" in self.data:
         self._draw_currentweather_symbol_( self.data['ww'] )
      if "dd" in self.data and "ff" in self.data:
         # FF in METERS PER SEC PLEASE
         self._draw_windbarb_(0,0,self.data['ff'],self.data['dd'])

      # Save figure
      self._save_figure_(outfile)
      self._create_current_(outfile)


   # ----------------------------------------------------------------
   # Draw temperature and dew point temperature
   # ----------------------------------------------------------------
   def _draw_day_value_(self,value):
      string = "%02d" % value
      opts = {"verticalalignment":"bottom","horizontalalignment":"right",
              "color":"gray","fontsize":self.config.fontsize*0.6}
      self._place_symbol_(.9,-.95,string,"xxx",opts)
   def _draw_hour_value_(self,value):
      string = "%02d" % value
      opts = {"verticalalignment":"bottom","horizontalalignment":"right",
              "color":"gray","fontsize":self.config.fontsize*0.6}
      self._place_symbol_(.9,-.7,string,"xxx",opts)

   # ----------------------------------------------------------------
   # Placing cloud symbol
   # ----------------------------------------------------------------
   def _draw_cloudcover_symbol_(self,value):
      # In database this shit is in percent Compute octa values.
      import numpy as np
      value = int(value)
      if value > 0:
         value = int(np.floor( float(value) / 100. * 8. ))
      string = "%d" % value ###int(np.round(float(value)/100*8))
      opts = {"verticalalignment":"center","horizontalalignment":"center"}
      self._place_symbol_(0,0,string,"cc",opts)
   def _draw_cloudcover_noobs_(self):
      opts = {"verticalalignment":"center","horizontalalignment":"center","color":"gray"}
      self._place_symbol_(0,0,"X","xxx",opts)
   def _draw_cloudhigh_symbol_(self,value):
      string = "%d" % int(value)
      opts = {"verticalalignment":"center","horizontalalignment":"center"}
      self._place_symbol_(0,.8,string,"ch",opts)
   def _draw_cloudmid_symbol_(self,value):
      string = "%d" % int(value)
      opts = {"verticalalignment":"center","horizontalalignment":"center"}
      self._place_symbol_(0,.6,string,"cm",opts)
   def _draw_cloudlow_symbol_(self,value):
      string = "%d" % int(value)
      opts = {"verticalalignment":"center","horizontalalignment":"center"}
      self._place_symbol_(0,-.8,string,"cl",opts)

   # ----------------------------------------------------------------
   # Current weather
   # ----------------------------------------------------------------
   def _draw_currentweather_symbol_(self,value):
      if value >= 100:
          return #No weather have been reported. Issue arise due to the WWs fpr automatic weather ststions
      else:
          string = "%02d" % int(value)
          print(value)
      opts = {"verticalalignment":"center","horizontalalignment":"center"}

      self._place_symbol_(-.8,0,string,"ww",opts)

      # Setting background color if needed
      font_color,bg_color = self._currentweather_get_colors_("%d" % value)
      if bg_color is not None:
         import matplotlib.patches as patches
         self.ax.add_patch( patches.Rectangle((-1,-1), 2, 2, \
                  facecolor=bg_color, linewidth=0) )


   # ----------------------------------------------------------------
   # Draw temperature and dew point temperature
   # ----------------------------------------------------------------
   def _draw_temperature_value_(self,value):
      import numpy as np
      value = float(value)/10
      string = ["%d" % np.floor(value),"%d" % np.round(value*10-(np.floor(value)*10))]
      opts = {"verticalalignment":"bottom","horizontalalignment":"left"}
      self._place_symbol_(-.9,.55,string,"t",opts)
   def _draw_dewpoint_value_(self,value):
      import numpy as np
      value = float(value)/10
      string = ["%d" % np.floor(value),"%d" % np.round(value*10-(np.floor(value)*10))]
      opts = {"verticalalignment":"bottom","horizontalalignment":"left"}
      self._place_symbol_(-.9,-.95,string,"td",opts)

   # ----------------------------------------------------------------
   # Current pressure value
   # ----------------------------------------------------------------
   def _draw_pressure_value_(self,value):
      import numpy as np
      string = "%d" % np.round(float(value)/10.)
      string = string[-3:]
      opts = {"verticalalignment":"bottom","horizontalalignment":"right"}
      self._place_symbol_(.9,.55,string,"pmsl",opts)
   def _draw_pressurechange_value_(self,value):
      import numpy as np
      string = "%03d" % np.round(float(value)/10.)
      string = string[-2:]
      opts = {"verticalalignment":"top","horizontalalignment":"right",
               "fontsize":float(self.config.fontsize)*0.5}
      self._place_symbol_(.9,.55,string,"pch",opts)
   def _draw_pressurechange_symbol_(self,value):
      import numpy as np
      string = "%d" % value 
      opts = {"verticalalignment":"center","horizontalalignment":"center"}
      self._place_symbol_(.8,0,string,"ptend",opts)


   # ----------------------------------------------------------------
   # Used for current weather. Returns (depending on the value)
   # font color, and background color. Or None,None if not needed.
   # ----------------------------------------------------------------
   def _currentweather_get_colors_(self,orig_string):
      # Default no color
      font_color = None
      bg_color   = None
      # Yellow for fog
      if orig_string in ["28","41","42","43","44","45","46","47","48","49"]:
         font_color = "#ffd903"
         bg_color   = "#ffffd8"
      elif orig_string in ["08","09","10","11","12","40"]:
         font_color = "#fed804"
         bg_color   = "#ffffff"
      # Green for rain
      elif orig_string[0] in ["5","6","7"] or orig_string in ["20","21","22","23","24"]:
         font_color = "#009933"
         bg_color   = "#d9efe0"
      elif orig_string in ["14","15","16"]:
         font_color = "#009933"
         bg_color   = "#ffffff"
      # Blue for shower
      elif orig_string[0] in ["8"] or orig_string in ["25","26","27","90"]:
          font_color = "#0000cc"
          bg_color   = "#d9e0ef"
      # Red for thunderstorms
      elif orig_string in ["17","29","91","92","93","94","95","96","97","98","99"]:
          font_color = "#f30000"
          bg_color   = "#ffe8e8"
      elif orig_string in ["13","18","19"]:
          font_color = "#f30000"
          bg_color   = "#ffffff"
      return font_color,bg_color

   # ----------------------------------------------------------------
   # Helper function to place test/symbols (depending on the font
   # it will be either a string (text) or a symbol (as we are using
   # special fonts to draw the symbols).
   # ----------------------------------------------------------------
   def _place_symbol_(self,x,y,string,what,opts):

      # First setting default font options and overwrite with the 
      # ones specified by the user. If set.
      fontopts = dict(verticalalignment='top',
                      horizontalalignment='center',
                      color="black",fontsize=self.config.fontsize)
      for key in fontopts.keys():
         if key in opts: fontopts[key] = opts[key]

      from matplotlib.font_manager import FontProperties
      font = FontProperties()
      font.set_style('normal')
      font.set_size( fontopts['fontsize'] )

      # For current weather we have to "select" the font
      if what == "ww":
         # We need a font called wX where X is the first character
         # of the string we got. If not existing, return.
         orig_string = string
         what        = "w%1s" % string[0]
         string      = "%1s" % string[1]
         if not what in self.config.fonts: return
         fontopts['color'] = self.config.fonts[what]['color']
         font.set_file(self.config.fonts[what]['font'])
         font_color,bg_color = self._currentweather_get_colors_(orig_string)
         if font_color is not None:
            fontopts['color'] = font_color
      elif what in self.config.fonts:
         fontopts['color'] = self.config.fonts[what]['color']
         font.set_file(self.config.fonts[what]['font'])
      else:
         font.set_family("monospace")
         

      # - Draw symbol
      self.test = []
      if type(string) == type(list()):
         self.ax.text(x,y,string[0],fontdict=fontopts,fontproperties=font)

         # Rendering text, compute offset for superscript
         import matplotlib
         bb = matplotlib.textpath.TextPath((0,0), string[0],
               size=fontopts['fontsize'])
         bb = bb.get_extents()
         x2 = x+bb.width/self.config.dpi*4.5
         ###########x2 = x + 0.1*len(string[0])
         font.set_size( font.get_size() * 0.7 ) 
         self.ax.text(x2,y,string[1],fontdict=fontopts,fontproperties=font)
      else:
         self.ax.text(x,y,string,fontdict=fontopts,fontproperties=font)



   # ----------------------------------------------------------------
   # Initializes new matplotlib figure
   # ----------------------------------------------------------------
   def _open_figure_(self):
      """!Helper function opening the new matplotlib.pyplot.figure
      object, setting axis properly. 
      @param No input parameters, all needed is on self.config.
      @return No return, stores axis and figure handler onto
      self.ax and self.fig."""

      import matplotlib.pyplot as plt

      # Create new figure, setting axis to limits, axis off
      w = int(self.config.imagewidth  / self.config.dpi)
      h = int(self.config.imageheight / self.config.dpi)
      self.fig = plt.figure(figsize=(1,1),frameon=False)
      self.ax = self.fig.add_axes([0, 0, 1, 1])
      self.ax.axis("off")

      self.ax.set_xlim(-1,1)
      self.ax.set_ylim(-1,1)
      self.ax.set_xticks([])
      self.ax.set_yticks([])


   # ----------------------------------------------------------------
   # Saving figure
   # ----------------------------------------------------------------
   def _save_figure_(self,file):
      """!Saves the figure self.fig into the output file specified.
      @param file. Required, string. Name of the output file.
      @return No return."""
      
      log.info("SAVE FIGURE NOW AS:  %s" % file)
      with open(file, 'w') as outfile:
         self.fig.canvas.print_png(outfile)

   # ----------------------------------------------------------------
   # Copy to current (last produced == current synop)
   # ----------------------------------------------------------------
   def _create_current_(self,file):

      import re
      # Searching for this string. Only valid if it occurring
      # once, and only once!
      m = re.findall(".*(synop_[0-9]{8}_[0-9]{4}_).*",file)
      if not len(m) == 1:
         log.warning("Cannot create link - could not find proper string")
         return 

      new = file.replace(m[0],"synop_current_")
      log.info("Create copy from %s to %s" % (file,new))
      import shutil
      shutil.copy(file,new)


   # ----------------------------------------------------------------
   # Simple exit handler
   # ----------------------------------------------------------------
   def exit( self, msg, level=9 ):
      log.error(msg); import sys; sys.exit(level)


















