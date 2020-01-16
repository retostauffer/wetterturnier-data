# -------------------------------------------------------------------
# - NAME:        utils.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2015-02-21
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2015-02-21, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-08-08 06:11 on prognose2.met.fu-berlin.de
# -------------------------------------------------------------------


def movefile(config,stint,file,typ,ok):

   import sys, os

   if not typ == 'bufr' and not typ == 'synop':
      sys.exit('Problems calling utils.movefile. Input typ %s not allowed (use bufr/synop).' % typ)
   if not type(ok) == type(True):
      sys.exit('Problems calling utils.movefile. Input ok has to be logical.')

   # - Source file:
   print '    Source file: %s' % file

   # - Destination directory
   #   not ok means ok == False .. however :D 
   if not ok:
      dstdir = '%s/%s/error' % (config['%s_outdir' % stint],typ)
   else:
      dstdir = '%s/%s/processed' % (config['%s_outdir' % stint],typ)

   # - Create dir if not existing
   if not os.path.isdir( dstdir ):
      os.system('mkdir -p %s' % dstdir)

   # - Destination file:
   dstfile = '%s/%s' % (dstdir,file.split('/')[-1])
   print '    Destination is: %s' % dstfile

   os.rename(file,dstfile)

   return
