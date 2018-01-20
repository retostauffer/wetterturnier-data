# -------------------------------------------------------------------
# - NAME:        blitzortung.R
# - AUTHOR:      Reto Stauffer
# - DATE:        2014-12-30
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2014-12-30, RS: Created file on pc24-c707.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2015-01-11 17:22 on thinkreto
# -------------------------------------------------------------------

# - UTC
Sys.setenv('TZ'='UTC')

# - Config
config <- list()
config$bgdir   <- 'background'
config$bgname  <- 'background_%s.png'
config$imgdir  <- 'prepared'
config$imgname <- 'prepared_%s.png'
config$dstdir  <- 'blitzortung'
config$dstname <- 'blitzortung_%s.png'
config$range   <- 0.5 # degrees
config$gadmdir <- 'gadm'
config$imgdim  <- 300

config$sqlite  <- 'sqlite/strikes.sqlite'
config$maxage  <- 6 # hours

config$col_station <- 'black'

# - Create dir if necessary
if ( ! file.exists(config$bgdir) )  dir.create(config$bgdir)
if ( ! file.exists(config$imgdir) ) dir.create(config$imgdir)
if ( ! file.exists(config$dstdir) ) dir.create(config$dstdir)

# - Loading necessary packages
stopifnot( require('RSQLite') )
stopifnot( require('colorspace') )
stopifnot( require('sp') )

# - Loading station.txt file
if ( ! file.exists('stations.txt') ) stop('Cannot find stations.txt file')
cat(sprintf(' * Reading station list\n'))
stations <- try( read.table('stations.txt',header=TRUE,comment.char='#',sep=',',
         colClasses=c('character','numeric','character','numeric','numeric')) )
if ( class(stations) == 'try-error' ) stop('Error reading stations.txt file')

# - Show which cities and stations we found
cities <- unique(stations$city)
for ( c in cities ) {
   cat(sprintf('   Found city %s [stations: %s]\n',c,
      paste(subset(stations,city==c)$wmo,collapse=', ')))
}


# -------------------------------------------------------------------
# - Returns xlim and ylim values for the plots. We need the same
#   values for the background image and the current lightning.
#   Else we cannot overlay them.
get.xlim <- function(stations,c,config) {
   mean(subset(stations,city==c)$lon)+c(-1,1)*config$range
}
get.ylim <- function(stations,c,config) {
   mean(subset(stations,city==c)$lat)+c(-1,1)*config$range*0.5
}
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# - Checks the extent of the gadm shapefile
#   and the extent of the plot. Returns FALSE
#   if the gadm file is totally outside limits
#   and we do not have to plot it at all. Else 
#   returns TRUE.
check.extent <- function(gadm,xlim,ylim) {
   e <- matrix(c(apply(coordinates(gadm),2,FUN=min,na.rm=TRUE),
                 apply(coordinates(gadm),2,FUN=max,na.rm=TRUE)),
         nrow=2,dimnames=list(c('lon','lat'),c('min','max')))
   if ( max(xlim) < e['lon','min'] | min(xlim) > e['lon','max'] ) return(FALSE)
   if ( max(ylim) < e['lat','min'] | min(ylim) > e['lat','max'] ) return(FALSE)
   return(TRUE)
}
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# - Create background images if necessary
cat(sprintf(' * Checking/Creating background images\n'))
for ( c in cities ) {

   # - Check if background-file allready exists
   bgfile <- sprintf('%s/%s',config$bgdir,sprintf(config$bgname,c))
   if ( file.exists(bgfile) ) {
      cat(sprintf('   Background file for %s exists, skip\n',c))
      next
   }

   # - Create background image
   cat(sprintf('   Background file for %s does not exist, plot\n',c))

   # - Getting limits
   xlim <- get.xlim(stations,c,config)
   ylim <- get.ylim(stations,c,config)

   # - Create new image
   main <- sprintf('Blitzortung for %s',c)

   # - Plotting
   png(file=bgfile,width=config$imgdim,height=config$imgdim)
      layout(matrix(c(1,2),ncol=2),widths=c(0.8,0.2))
      par(mar=c(1,0.1,2,0.1),xaxt='n',yaxt='n')
      #par(mar=c(1,1,2,1),xaxt='n',yaxt='n')
      plot(0,0,type='n',main=main,xlab='longitude',ylab='latitude',
            xlim=xlim,ylim=ylim)
      gadmfiles <- list.files(config$gadmdir)
      for ( file in gadmfiles ) {
         var <- load(sprintf('%s/%s',config$gadmdir,file))
         gadm <- eval(parse(text=var))
         if ( ! check.extent(gadm,xlim,ylim) ) next
         plot(gadm,add=TRUE,border='slategray')
      }
      # - Adding stations
      tmp <- subset(stations,city==c)
      for ( i in 1:nrow(tmp) ) {
         points(tmp[i,]$lon,tmp[i,]$lat,pch=19,col=config$col_station)
         text(tmp[i,]$lon,tmp[i,]$lat,tmp[i,]$wmo,pos=1,col=config$col_station)
      }
   dev.off()
}
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# - Create lightning detection map.
#   First: loading data from the sqlite file.
cat(sprintf(' * Loading sqlite data\n'))
db <- dbConnect(dbDriver("SQLite"),config$sqlite)
sql <- sprintf('SELECT * FROM lightning WHERE timestamp >= %.0f ORDER BY timestamp ASC',
         as.numeric(Sys.time()) - config$maxage*3600)
cat(sprintf('   SQL statement: %s\n',sql))
data <- subset(dbGetQuery(db,sql),select=c(timestamp,longitude,latitude))
names(data) <- c('time','lon','lat')
data <- data[order(data$time),]

# -------------------------------------------------------------------
# - Generating colors for the lightnings
pal <- function (n, h = c(64, -105), c. = c(4, 100), l = c(90, 50), 
    power = c(2.56451612903226, 2.03225806451613), fixup = FALSE, 
    gamma = NULL, alpha = 1, ...) 
{
    if (!is.null(gamma)) 
        warning("'gamma' is deprecated and has no effect")
    if (n < 1L) 
        return(character(0L))
    h <- rep(h, length.out = 2L)
    c <- rep(c., length.out = 2L)
    l <- rep(l, length.out = 2L)
    power <- rep(power, length.out = 2L)
    rval <- seq(1, 0, length = n)
    rval <- hex(polarLUV(L = l[2L] - diff(l) * rval^power[2L], 
        C = c[2L] - diff(c) * rval^power[1L], H = h[2L] - diff(h) * 
            rval), fixup = fixup, ...)
    if (!missing(alpha)) {
        alpha <- pmax(pmin(alpha, 1), 0)
        alpha <- format(as.hexmode(round(alpha * 255 + 1e-04)), 
            width = 2L, upper.case = TRUE)
        rval <- paste(rval, alpha, sep = "")
    }
    return(rval)
}
# -------------------------------------------------------------------

####n <- 10000
####xx <- data.frame('time'=sample(seq(min(data$time),max(data$time),100),n,replace=TRUE),
####                 'lon'=sample(seq(from=7,to=17,by=0.1),n,replace=TRUE),
####                 'lat'=sample(seq(from=43,to=52,by=0.1),n,replace=TRUE))
####data <- rbind(data,xx)
####data <- data[order(data$time),]

# -------------------------------------------------------------------
cat(sprintf(' * Plotting data\n'))
for ( c in cities ) {

   cat(sprintf('  Create lightning activity for %s\n',c))

   # - Prepare map with lightning data 
   imgfile <- sprintf('%s/%s',config$imgdir,sprintf(config$imgname,c))
   if ( file.exists(imgfile) ) file.remove(imgfile)
   dstfile <- sprintf('%s/%s',config$dstdir,sprintf(config$dstname,c))
   if ( file.exists(dstfile) ) file.remove(dstfile)

   # - Getting limits
   xlim <- get.xlim(stations,c,config)
   ylim <- get.ylim(stations,c,config)

   sub <- subset(data,lon >= min(xlim) & lon <= max(xlim) &
                      lat >= min(ylim) & lat <= max(ylim) )

   if ( nrow(sub) == 0 ) {
      cat(sprintf('  [!] No lightning activity, skip\n'))
      next
   }

   # - Compute the AGE of the lightning strikes as integer
   #   intervals of length ntime representing the color it gets.
   ntime     <- 20 # defines number of colors and time interval
   sub$i     <- abs(sub$time - as.numeric(Sys.time()))
   sub$i     <- ntime - round( sub$i/(config$maxage*3600)*(ntime-1) )
   sub$i     <- ifelse( sub$i < 0, 0, sub$i ) 
   sub$color <- pal(ntime)[sub$i]
   sub$size  <- 0.3 + sub$i/ntime*1.5

   # - Plotting
   png(file=imgfile,width=config$imgdim,height=config$imgdim,bg='transparent')
      layout(matrix(c(1,2),ncol=2),widths=c(0.8,0.2))
      par(mar=c(1,0.1,2,0.1),xaxt='n',yaxt='n')
      ##par(mar=c(1,1,2,1),xaxt='n',yaxt='n')
      plot(0,0,type='n',main='',xlab='longitude',ylab='latitude',
            xlim=xlim,ylim=ylim)
      points(sub$lon,sub$lat,pch=19,cex=sub$size,col=sub$color)
      mtext(side=1,sprintf('Generated: %s [%dh max]',
         strftime(Sys.time(),'%Y-%m-%d %H:%M %Z'),config$maxage))

      par(mar=c(1,0.5,2,3))
      plot(0,0,type='n',xlim=c(0,1),ylim=c(.5,ntime+.5),xaxs='i',yaxs='i')
      for ( ix in 1:ntime ) {
         polygon(c(0,1,1,0),c(ix-.5,ix-.5,ix+.5,ix+.5),col=pal(ntime)[ix])
      }
      at <- seq(1,ntime,length.out=config$maxage+1)
      lab <- seq(config$maxage,0,length.out=config$maxage+1)
      par(yaxt='s',las=1)
      axis(side=4,at=at,label=sprintf('%dh',lab))

   dev.off()


}

# - Overlay images
cat(sprintf(' * Create combined files\n'))
for ( c in cities ) {
   
   cat(sprintf('  For city %s\n',c))
   # - Define file names first
   bgfile <- sprintf('%s/%s',config$bgdir,sprintf(config$bgname,c))
   imgfile <- sprintf('%s/%s',config$imgdir,sprintf(config$imgname,c))
   dstfile <- sprintf('%s/%s',config$dstdir,sprintf(config$dstname,c))

   # - If both file exists, compose.
   if ( file.exists(bgfile) & file.exists(imgfile) ) {
      cmd <- sprintf('composite -gravity center %s %s %s',
               imgfile,bgfile,dstfile)
      cat(sprintf('  Compose: %s\n',cmd))
      system(cmd)
   }

}


# - Create text file with current date/time to check when
#   the script was called last.
cat(sprintf(' * Crate lastrun logfile\n'))
write(strftime(Sys.time(),'%Y-%m-%d %H:%M'),file=sprintf('%s/lastrun',config$dstdir))



