#!/bin/bash
# -------------------------------------------------------------------
# - NAME:        get_latest.sh
# - AUTHOR:      Reto Stauffer
# - DATE:        2018-11-14
# -------------------------------------------------------------------
# - DESCRIPTION: Downloading some BUFR files from ogimet as MeteoSwiss
#                wont give them to us.
# -------------------------------------------------------------------
# - EDITORIAL:   2018-11-14, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-06-18 00:30 on prognose2
# -------------------------------------------------------------------

#1st command line argument: hours backwards in time to process
N=${1:-3}
#N=${1:-48}
echo "Looking for BUFR files not older than ${N} hour(s)..."

set -u
 
logfile="errorlog_unterlaa.txt"
if [ -n ${logfile} ]; then
   touch $logfile
fi

# From/to (N hours)
BEGIN=`date -u "+%Y%m%d%H%M" -d "${N} hours ago"`
END=`date -u "+%Y%m%d%H%M"`

printf "Trying to get BUFR for/between\n"
printf " - Begin:   %s\n" "${BEGIN}"
printf " - End:     %s\n" "${END}"

# Only extracting CENTER LOWM (and only specific files, see regex
# expression in the egrep command below).
CENTER="LOWM"
LST="listing_unterlaa.html"
URL="http://www.ogimet.com/getbufr.php"

# Where the files should be stored for further processing
OUTDIR="/home/imgi/GISCobservations/incoming-additional"
if [ ! -d ${OUTDIR} ] ; then
   printf "[ERROR] %s does not exist. Stop." ${OUTDIR}
fi

# Output directory
TMPDIR="ogimet_bufr_tmp"
if [ ! -d ${TMPDIR} ] ; then mkdir $TMPDIR ; fi

# Grep listing from ogimet (listing with files)
printf "Downloading file listing from ogimet\n"
if [ -f ${LST} ] ; then rm ${LST} ; fi
printf " - wget ${URL}?res=list&beg=${BEGIN}&end=${END}&ecenter=${CENTER}"
wget "${URL}?res=list&beg=${BEGIN}&end=${END}&ecenter=${CENTER}&type=IS" -O $LST

# Extract the bufr files we would like to get from ogimet
printf "Extracting the files we would like to download\n"

#regex=">\S+IS(MD|ID|ND)23\S+\\.bufr<"
#TODO: FIND A PROPER REGEX! WE ARE DOWNLOADING TOO MUCH WRONG/UNNECESSARY DATA!!!
regex='>\S+[0-9]{6}(_CC[A-Z]|)\.bufr<'
#regex='>\S+IS..13\S+\.bufr<'
#regex='>\S+*\.bufr<'

nfiles=`cat ${LST} | egrep -oE $regex | wc -l`
files=`cat ${LST} | egrep -oE $regex | sed -e "s/<//g" -e "s/>//g"`

#nfiles=`cat ${LST} | wc -l`
#files=`cat ${LST} | sed -e "s/<//g" -e "s/>//g"`
printf "Number of files to be considered: %d\n" $nfiles

if [ $nfiles -eq 0 ] ; then
    printf "No files, stop ...\n\n"
    exit 0
fi

# If a CCX exists we should remove all filess but the latest correction
# TODO

# Loop over files and download if not yet available. If
# we download a new file: move the file to the incoming
# folder with additionals. These files will be considered.
# by the bufr decoder.
printf "Start downloading new bufr files (if there are any)\n"
for file in ${files[@]} ; do
    local=`printf "%s/%s" ${TMPDIR} ${file}`
    if [ ! -f ${local} ] ; then
        success=0
        ii=0
        while [ $success -eq 0 ] && [ $ii -lt 3 ]; do
            printf " - Downloading %s\n" ${file}
            wget --no-check-certificate "${URL}?file=${file}" -O ${local} || rm -f ${local}
            #delete file if size == 0byte
            if [ ! -s ${local} ]; then
               rm -f ${local}
               success=0
               echo "0 BYTE FILE!"
            fi
            if [ -f ${local} ]; then
               cp ${local} ${OUTDIR}/
               succes=1
               echo "SUCCESS!"
            else
               echo "FILE NOT DOWNLOADED!"
            fi
            ii+=1
        done
    else
        printf " - Already processed: %s\n" ${file}
    fi
done

# At the end: remove all bufr files older than 48 hours.
# not needed. They are just kept inside the TMPDIR folder
# to track what we have already processed and what's new
# in the listing.
printf "Delete files in %s older than 48 hours\n" ${TMPDIR}
find ${TMPDIR} -type f -name "*.bufr" -mmin +2880 -exec rm {} \;

