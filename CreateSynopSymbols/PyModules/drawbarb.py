# -------------------------------------------------------------------
# - NAME:        drawbarb.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-12
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-12, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-12-12 15:05 on pc24-c707
# -------------------------------------------------------------------

import logging
log = logging.getLogger(__name__)

class drawbarb( object ):

   def _draw_windbarb_(self,x,y,ff,dd,col='black'):

      import numpy as np

      #align = False
      align = True
  
      # - Converting ff to knots
      ff = float(ff)/10 # to get meters per second. database holds m/s*10
      ff = int(np.round(ff*1.94384449/5)*5)
      log.info("Drawing wind barb with ff=%f and dd=%f" % (ff,dd))
  
      # - Compute correct xy values
      offset = 0.012*float(self.config.fontsize)
      scaling = offset * 3.0 # scaling: controls barb size
      lwd    = float(self.config.fontsize)/9
  
      # - First definition of a barb. Always
      #   x,y (line)
      #   Centered around (0,0)
      #   positive to northeast
      barbs = {}
      barbs['b0']    = ( ((0.0,0.00),(0.0,1.00)), )
      barbs['b5']    = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,0.85),(0.2,0.95)), )
      barbs['b10']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)), )
      barbs['b15']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.2,0.95)), )
      barbs['b20']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)), )
      barbs['b25']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)),
                         ((0.0,0.70),(0.2,0.80)), )
      barbs['b30']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)),
                         ((0.0,0.70),(0.4,0.90)), )
      barbs['b35']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)),
                         ((0.0,0.70),(0.4,0.90)),
                         ((0.0,0.55),(0.2,0.65)), )
      barbs['b40']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)),
                         ((0.0,0.70),(0.4,0.90)),
                         ((0.0,0.55),(0.4,0.75)), )
      barbs['b45']   = ( ((0.0,0.00),(0.0,1.00)),
                         ((0.0,1.00),(0.4,1.20)),
                         ((0.0,0.85),(0.4,1.05)),
                         ((0.0,0.70),(0.4,0.90)),
                         ((0.0,0.55),(0.4,0.75)),
                         ((0.0,0.40),(0.2,0.50)), )
      barbs['error'] = ( (( 0.0,0.0),(0.0,1.0)),
                         ((-0.4,0.6),(0.4,1.4)),
                         ((-0.4,1.4),(0.4,0.6)), )



      # - Search value 'needle' in array 'haystack'
      def inarray(haystack,needle):
         for i in range(len(haystack)):
            if haystack[i] == needle:
               return(True)
         return(False)
  
      # - Take barb definition (or error barb)
      if inarray(barbs.keys(),'b'+str(int(ff))):
         b = barbs['b'+str(int(ff))]
      else:
         b = barbs['error']

      # - dd in radiant, meteorologically corrected
      ddrad = float(90+float(dd))/180.*np.pi
  
      # - Rotating vectors. rot has to be in radiant
      def rotxy(x,y,rot):
         d = np.sqrt(x**2.+y**2.)
         a = np.arctan2(x,y)
         x = -d*np.cos(rot+a)
         y = d*np.sin(rot+a)
         return(x,y)
  
      for i in range(len(b)):
         if align:
            x1 = (b[i][0][0])*scaling+offset
            x2 = (b[i][1][0])*scaling+offset
            y1 = (b[i][0][1]-0.5)*scaling
            y2 = (b[i][1][1]-0.5)*scaling
         else:
            x1 = b[i][0][0]*scaling
            x2 = b[i][1][0]*scaling
            y1 = b[i][0][1]*scaling+offset
            y2 = b[i][1][1]*scaling+offset
  
         # - Vector rotation happens here
         x1,y1 = rotxy(x1,y1,ddrad)
         x2,y2 = rotxy(x2,y2,ddrad)
  
         # - Rotating
         self.ax.plot((x+x1,x+x2),(y+y1,y+y2),color=col,
                       linewidth=lwd,solid_capstyle='round')


  

