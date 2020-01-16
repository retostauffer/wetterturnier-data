# -------------------------------------------------------------------
# - NAME:        handler.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-12-18
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-12-18, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-06-11 23:00 on thinkreto
# -------------------------------------------------------------------

import logging, logging.config
log = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Loading the files from the ftp and manipulate them
# -------------------------------------------------------------------
class handler( object ):

   def __init__( self, config, date_time ):
      """!Initialize new handler object. Actually doing nothing
      than store the config settings here and appends a ftphandler
      object internally.
      @param config. readconfig object containing the necessary 
         cofiguration settings.
      @param date_time. A datetime object containing the date and
         hour/minute for which the download of the files should take
         place. Plese note that year, month, day, hour and minute
         will be taken from this 'date_time' input variable.
         Be sure that your minute is '00' if you would like to
         process files for 'YYYY-mm-dd HH:00'.
      @return No return, just initializes a new instance of the
         handler object."""

      import datetime
      if not type(date_time) == type(datetime.datetime.now()):
         self.exit("Input \"date_time\" was no 'datetime' object. Stop.")

      self.date_time = date_time
      self.YYYYmmdd  = date_time.strftime("%Y%m%d") 
      self.HHMM      = date_time.strftime("%H%M")

      # Save config
      self.config = config

      import ftphandler
      self.ftp = ftphandler.ftphandler( config )

      # Loading ALL available file names from the ftp server matching
      # YYYYmmdd*HHMM and save them into self.ftp_files. This will be
      # used as a lookup-list later - to check if a requested file
      # is available on the ftp server or not.
      self.ftp_files = self.ftp.getFilelist("*%s*%s*" % (self.YYYYmmdd,self.HHMM))



   # ----------------------------------------------------------------
   # Rotates image if needed
   # ----------------------------------------------------------------
   def _rotate_image_( self, img, rotation ):
      """!Rotates image if needed
      @param img. Image object
      @param rotation. Integer or None. If integer: image will be roated.
         Else the image will be returned as it is.
      @return Returns Image object, rotated if requested."""

      if rotation is None: return img 
      log.info("  Rotating image: %d deg" % rotation)
      return img.rotate( rotation, expand=1 ) 


   # ----------------------------------------------------------------
   # Crops image if needed
   # ----------------------------------------------------------------
   def _crop_image_( self, img, nrows, ncols, attr ): 
      """!Crops an image.
      @param img. Image object.
      @param right. Integer, right corner for crop. Same for upper, left, and lower.
      @return Returns cropped Image object."""

      import numpy as np

      # Full image width
      img_w, img_h = img.size

      # Compute crop window
      if nrows == 1 and ncols == 1:
         return img_w,img_h,img 

      # Compute left, upper, right, lower pixels
      if nrows == 1:
         upper = 0; lower = img_h-1 
      else:
         upper = int( (attr['row']-1) * np.floor(img_h/nrows) )
         lower = int( (attr['row'])   * np.floor(img_h/nrows) )

      if ncols == 1:
         left = 0;  right = img_w-1 
      else:
         left  = int( (attr['col']-1) * np.floor(img_w/ncols) )
         right = int( (attr['col'])   * np.floor(img_w/ncols) )


      log.info("  [left/upper/right/lower]: %d %d %d %d" % (left,upper,right,lower))
      width  = np.abs(left-right)
      height = np.abs(lower-upper)
      return width, height, img.crop( (left,upper,right,lower) )
 
   # ----------------------------------------------------------------
   # Resize image
   # ----------------------------------------------------------------
   def _resize_image_( self, img, attr, width, height ): 
      """!Resizes an image if needed.
      @param img. Image object
      @param attr. Dict (from readconfig) containing the crop extent
         and the resize attributes.
      @return Returns Image object."""

      from PIL import Image
      #import Image

      # Resize image?
      if not attr['resize_x'] == None or not attr['resize_y'] == None:
         # Compute corresponding dimensions if only one is set
         if attr['resize_x'] is None:
            attr['resize_x'] = int( width  * attr['resize_y'] // height ) 
         if attr['resize_y'] is None:
            attr['resize_y'] = int( height * attr['resize_x'] // width  ) 
 
         # Resize now
         resize = ( (attr['resize_x'],attr['resize_y']) )
         log.info("  - [Resize x/y]: %d %d" % resize) 
         return img.resize( resize, Image.ANTIALIAS )


   # ----------------------------------------------------------------
   # Download and crop the images/products as specified
   # in the config files.
   # ----------------------------------------------------------------
   def getImages( self, product ):
      """!Downloading an image from the ftp and crops/slices the image
      as specified in the different config files. The inputs are 
      coming from readconfig.readconfig.products.
      @param product. Dict containing the original_file (the name of
         the file on the ftp server), and a list of dicts including
         the name of the product (which will be used as ouput file
         name for a 'slice'), and the left/upper/right/lower pixels
         for the image cropping.
      @return Returns boolean True/False value OR boolean list.
         If a single bool value will be returned, there was a major
         problem with the inputs. If a list will be returned, each
         of the bool flags correspond to one of the slices specified
         in the config file.""" 

      import os
      import fnmatch
      from PIL import Image
      from copy import copy

      # Extracting the necessary infos
      original_file = product['original_file']
      original_file = original_file.replace("<YYYYmmdd>",self.YYYYmmdd).replace("<HHMM>",self.HHMM)
      products      = product['products']

      if len(products) == 0:
         log.error("In handler.getImages I got no product definition. Not good. Return False.")
         return False 
      
      # Loading correct file name from ftp listing
      filename = fnmatch.filter(self.ftp_files,original_file)
      if len(filename) == 0:
         log.error("Could not find any file on the ftp matching \"%s\". Return False." % original_file)
         log.debug("... while processing products \"%s\"" % products)
         return False
      elif len(filename) == 2:
         log.warning("Got %d images for \"%s\". Take second (alphanumeric sort)." % \
                  ( len(filename), original_file))
         filename.sort(reverse=True)
         filename = [filename[0]]
         log.debug("- %s" % filename)
      elif len(filename) > 2:
         log.error("Got %d images for \"%s\". Dont know which one to download! Return False." % \
                  ( len(filename), original_file ))
         for rec in filename:
            log.debug("- %s" % rec)
         return False

      # Else downloading the image via ftp
      filename = filename[0]

      # ---------------------------------
      # Try to get proper file name
      # ---------------------------------
      local_original = os.path.join(self.config.originals, "%s.png" % filename)
      lockbit        = os.path.join(self.config.lockbitdir, filename)

      # If the file exists on disc, then we know that we have already
      # processed this file. In this case: skip 
      if os.path.isfile( lockbit ) and not self.config.devel:

         log.info("  [!] Already processed, skip ...")
         return 

      # Development mode: load from disc and go ahead
      elif os.path.isfile( local_original ):

         log.info("  [!] Local file exists, development mode on, load from disc")
         img = Image.open( local_original )

         # Create the lockbit
         log.info("      Create lockbit")
         open( lockbit, "a").close()

      # Else load file from ftp and go ahead
      else:

         img = self.ftp.getImage( filename ) 
         log.info("  - Original file size [x/y]: %d %d" % img.size)

         # Create the lockbit
         log.info("      Create lockbit")
         open( lockbit, "a").close()

         # Save original file to disc if store_originals is
         # set to true in the config file
         if self.config.store_originals:
            log.info("  - Save original file into:")
            log.info("    %s" % local_original)
            img.save( local_original )


      # ---------------------------------
      # Check if subdirectory exists, if set
      # Note that this procedure is different for [products meteograms]
      # and all others specified in the config file.
      # ---------------------------------
      if product['type'] == 'meteograms':
         output_directory = os.path.join(self.config.meteogramsdir)
      else:
         if product['subdirectory']:
            output_directory = os.path.join(self.config.imagedir,product['subdirectory'])
            if not os.path.isdir( output_directory ): os.mkdir( output_directory ) 
         else:
            output_directory = self.config.imagedir


      # If a rotation is set: rotate
      img = self._rotate_image_( img, product['rotation'] )

      # Now slicing all the different images out of that thing
      checker = []
      for key,attr in products.items():

         # If the key contains YYYYmmdd and/or HHMM: replace
         key = key.replace('YYYYmmdd',self.YYYYmmdd).replace('HHMM',self.HHMM) \
                  .replace('HH',self.HHMM[0:2])

         # Define file name where to store the new image
         outfile = os.path.join(output_directory,"%s.gif" % key)
         log.info("  Processing: %s" % outfile)

         #try:

         # Copy image
         tmp = copy( img )

         # If one of the extents is set, all four are available (else the readconfig
         # routine does not what she should do): in this case Crop.
         # If we have to corp
         width, height, tmp = self._crop_image_( tmp, product['nrows'], product['ncols'], attr ) 

         # If we have to rescale the image
         if attr['resize_x'] is not None or attr['resize_y'] is not None:
            tmp = self._resize_image_( tmp, attr, width, height ) 


         # Save output file
         tmp.save( outfile ) 
         checker.append(True)

         # If product['type'] is equal to 'meteograms' and product['lastrunfile']
         # is set, we have to add the current date/time to the lastrun file.
         # Just overwrite it.
         if product['type'] == 'meteograms' and product['lastrunfile'] is not None:
            lastrunfile = os.path.join( self.config.meteogramsdir, product['lastrunfile'] )
            lastrun_str = self.date_time.strftime("%Y-%m-%d %H:%M")
            print(lastrunfile)
            log.info("  Write meteogram lastrun file containing %s into:" % lastrun_str)
            log.info("  - %s" % lastrunfile)

            # Write lastrun file here
            fid = open(lastrunfile,"w")
            fid.write(lastrun_str)
            fid.close()

         #except Exception as e:
         #   log.debug("[]-> Error occured for this section, return False")
         #   log.debug("     Original image size: %d x %d" % img.size)
         #   log.debug("Exception:")
         #   log.debug(e)
         #   checker.append(False)

         log.info("%sSuccessful  [%d of %d]" % (" "*50,sum(checker),len(checker)))


   # ----------------------------------------------------------------
   # Close necessary things
   # ----------------------------------------------------------------
   def close( self ):
      """!Closing the object. It is actually closing the ftp connection
      stored inside the object."""

      # Close ftp connection
      self.ftp.close()
