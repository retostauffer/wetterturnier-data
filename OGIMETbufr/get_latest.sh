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
 
logfile="errorlog.txt"
if [ -n ${logfile} ]; then
   touch $logfile
fi

# From/to (N hours)
BEGIN=`date -u "+%Y%m%d%H%M" -d "${N} hours ago"`
END=`date -u "+%Y%m%d%H%M"`

printf "Trying to get BUFR for/between\n"
printf " - Begin:   %s\n" "${BEGIN}"
printf " - End:     %s\n" "${END}"

# Only extracting CENTER LSSW (and only ISMD/ISID/ISND, see regex
# expression in the egrep command below).
CENTER="LSSW"
LST="listing.html"
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
wget "${URL}?res=list&beg=${BEGIN}&end=${END}&ecenter=${CENTER}" -O $LST

# Extract the bufr files we would like to get from ogimet
printf "Extracting the files we would like to download\n"
nfiles=`cat ${LST} | egrep -oE ">\S+IS(MD|ID|ND)23\S+\\.bufr<" | wc -l`
files=`cat ${LST} | egrep -oE ">\S+IS(MD|ID|ND)23\S+\\.bufr<" | sed -e "s/<//g" -e "s/>//g"`
printf "Number of files to be considered: %d\n" $nfiles

if [ $nfiles -eq 0 ] ; then
    printf "No files, stop ...\n\n"
    exit 0
fi

# Loop over files and download if not yet available. If
# we download a new file: move the file to the incoming
# folder with additionals. These files will be considered.
# by the bufr decoder.
printf "Start downloading new bufr files (if there are any)\n"
for file in ${files[@]} ; do
    local=`printf "%s/%s" ${TMPDIR} ${file}`
    if [ ! -f ${local} ] ; then
        printf " - Downloading %s\n" ${file}
        wget --no-check-certificate "${URL}?file=${file}" -O ${local} || rm -f ${local}
        #delete file if size == 0byte
        if [ ! -s ${local} ]; then
           rm -f ${local}
        fi
        if [ -f ${local} ]; then
           cp ${local} ${OUTDIR}/
        else
           echo "- 0-BYTE FILE DOWNLOADED!, WILL SKIP AND TRY LATER!"
           echo "`date`: 0-BYTE ERROR" >> ${logfile}
           #TODO: try until suceeded?
        fi
    else
        printf " - Already processed: %s\n" ${file}
    fi
done

# At the end: remove all bufr files older than 24 hours.
# not needed. They are just kept inside the TMPDIR folder
# to track what we have already processed and what's new
# in the listing.
printf "Delete files in %s older than 48 hours\n" ${TMPDIR}
find ${TMPDIR} -type f -name "*.bufr" -mmin +2880 -exec rm {} \;

