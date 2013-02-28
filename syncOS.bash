#!/bin/bash

####
# This script is a wrapper for fsarchiver
# Basically check local device for ext4 FS and dump to file if not mounted
###


PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`


__print() {
# If 1st Param (__MODE__) is set to verbose it means that msg will display only in verbose mode 
# The displayed level will be info. Verbose mode is set by program VERBOSE var
# SILENT mode says that this can be ignored if silent, defined by global var silent 
local __MODE=$1 

case ${__MODE:=NULL}  in 
	VERBOSE) shift ;;
	SILENT)  shift ;;
	*)	__MODE=NORMAL ;;
esac

#echo "mode is $__MODE"

if [ $# -lt 3 ];
then
        printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "Error Calling function __print"
fi
#if [ "$__MODE" == "SILENT" ] ; 
#then
#	return 0
#fi
local __LEVEL=$1
shift
local __INFO=$1
shift
local __MSG="$*"
if [ $__MODE == "NORMAL" ]; 
then
	printf "%-10s %-10s %-22s %-30s \n" "$__LEVEL :" "$__INFO : " "$__MSG"
	return 0
fi
if [ $__MODE == "VERBOSE" ] ;
then
        [[ $VERBOSE -eq 1 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "INFO :" "$__INFO : " "$__MSG"
        return 0
fi
if [ $__MODE == "SILENT" ] ;
then
	if [ ${SILENT:=0} -ne 1 ];
        then
                printf "%-10s %-10s %-22s %-30s \n" "$__LEVEL :" "$__INFO : " "$__MSG"
        fi
fi
}

amiroot() {
CMD=/usr/bin/whoami
if [ ! -x $CMD ];
then
        __print "ERROR"  "$PRGNAME"  "cant get root status"
        exit 1
else
        __DUM=$(/usr/bin/whoami)
        if [ ${__DUM:=NULL} == "root" ];
        then
                __print "INFO" "$PRGNAME"    "You are root, continue"
        else
                __print "ERROR"   "$PRGNAME"  "Need to be root to run this"
                exit 1
        fi
fi
}


function end {
if [ $# -ne 0 ];
then
        RET=$1
else
        RET=0
fi
if [ -f {$TMPF1:=DUMMY.$$} ] ;
then
      rm $TMPF1
fi
exit $RET
}

# Save mbr /part to tune
partsave() {
__TARGET=$1  
if [ ! -b $__TARGET ] ; 
then
	__print "ERROR" "$PRGNAME" "$__TARGET disk not found"
	end 10
fi

__DATE=$(date '+%Y%m%d') 
OUT1=$__TARGET.mbr.dd-backup.$__DATE
OUT2=$__TARGET.sfdisk.backup.$__DATE
local i=0 ; 
for i in [ $OUT1 $OUT2 ]; 
do
	if [ -f $i ];
	then
		__print "WARNING" "$PRGNAME" "$i file exist, continue"
		read __DUMMY
	fi
done
__print "INFO" "$PRGNAME" "Creating $OUT1"
dd if=$__TARGET of=$OUT1 bs=512 count=1
__print "INFO" "$PRGNAME" "Creating $OUT2"
sfdisk -d $__TARGET > $OUT2
}


usage() {
cat << fin
$PRGNAME [-o] [-q] [ -F <FSTYPE> ] [ -t target dump dir ]  [ /dev/devicename OR LABEL ] || [-A] 
Backup file sytem using fsarchiver, default is to backup all partition of $TARGETFSTYPE which are not mounted 
	-A	Do all parition but mounted one backup
	-d	debug mode
	-D	Default targeti disk ($TARGETDISK) to backup 
	-F	Filesytem type for the source device (by default just work for ext4)
	-h	This page 
	-o	Force overwrite when file exist
	-P	Save the MBR and partition table
	-q	Silent mode (to be done)
	-t 	Target dir to write output file (if not specified $(pwd))
	-z	Compression level (as for fsarchiver)
fin
}

	
TARGETDIR=$(pwd)
TARGETDISK=/dev/sda
TARGETFSTYPE="ext4|ext3"
FORCEMOUNT=0
CREATEDESTDIR=0
#   obsolete FSTYPE="ext4|ext3" 
TARGETFSTYPE=ext4
FORCEMOUNT=0
CREATEDESTDIR=0
FSTYPE="ext4" 
SILENT=0
OVERWRITE=0
PROPFILE=ossync.prop
ZIPLEVEL=1
SOURCE=__NONE__
PARTSAVE=0
ALL=0 

while getopts AdDF:hoqPt:z sarg
do
case $sarg in
	A)	ALL=1 ;;
        d)      set -x
                DEBUG=1 ;;
	D)	TARGETDISK=$OPTARG;; 
	F)	TARGETFSTYPE="$OPTARG" ;; 
        h)      usage
                end;;
	o)	OVERWRITE=1 ;;
	q)	SILENT=1 ;;
	P)	PARTSAVE=1 ;; 
	t)	TARGETDIR=$OPTARG ;;
	z)	ZIPLEVEL=$OPTARG;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done

shift $(( $OPTIND - 1))
#echo "index $INDEX:$OPTIND"
#echo "::$#:$*:$ALL:$SOURCE:"
# We are set now to have in $* remaining params 
if [ $# -gt 0 ]; 
then
	SOURCE="$*" 
fi

if [ $ALL -eq 1 -a "$SOURCE" != "__NONE__" ] ;
then
	__print "ERROR" "$PRGNAME" "Parameter error please use -A OR specify devices"
	end 0
fi
if [ $ALL -eq 0 -a "$SOURCE" == "__NONE__" ] ;
then
	__print "ERROR" "$PRGNAME" "No target defined (-A or device list)"
	end 0
fi

if [ $ALL -ne 1 ];
then
	__print "INFO" "$PRGNAME" "Preparing  to dump $SOURCE "	
else
	__print "INFO" "$PRGNAME" "Preparing  to dump all appropriate device on $TARGETDISK "	
	SOURCE=ALL
fi
#### MAIN ##### 
#amiroot 


if [ ${PARTSAVE:=0} -eq 1 ] ;
then
	partsave $TARGETDISK 
fi
	
#SOURCE=$OPTARG ;;

if [ ! -d ${TARGETDIR:=EMPTY} ] ;
then
	__print "ERROR" "$PRGNAME" "$TARGETDIR target directory not found"
	end 9
fi

#if [ ! -f  ./$PROPFILE ] ;
#then
#	__print "ERROR" "$PRGNAME" "file ./$PROPFILE not found, continue ?"
#	read dummy	
#fi

# Building target list 
BASEARGS="-v -j2 -z $ZIPLEVEL"
if [ ${SOURCE:=NULL} == "ALL" ] ; 
then
	#LIST=$(blkid -o device) 
	#blkid -s TYPE  /dev/sda1  | cut -d = -f 2 | sed s/\"//g | grep -w ext4
	LIST=$(blkid -o device | grep ${TARGETDISK:=NONE})
	LIST=$(echo $LIST)
	FINALLIST=""

	__print "INFO" "$PRGNAME" "Disk list is $LIST"
else
	# Param is a device
	echo $SOURCE | grep '^\/dev\/' > /dev/null 2>&1 
	if [ $? -eq 0 ]
	then
		if [ -b $SOURCE ] ;
		then 
			__print "INFO" "$PRGNAME" "$SOURCE is a proper block device"	
			LIST=$SOURCE
		else
			__print "ERROR" "$PRGNAME" "Device $SOURCE is not found or existing"
			end 2 
		fi
	else
		#if not a device then a label ?
		LIST=$(blkid -L $SOURCE)
		if [ $? -eq 0 ]; 
		then 
			__print "INFO" "$PRGNAME" "$SOURCE is a proper device LABEL for $LIST"	
		else
			__print "ERROR" "$PRGNAME" "Label $SOURCE is not found or existing"
			end 2 
		fi
	fi
fi

# Checking if device is mounted
for i in $(echo $LIST) ; 
do
	__DUMMY=$(blkid -s TYPE  $i  | cut -d = -f 2 | sed s/\"//g)
	echo $__DUMMY | egrep -e $TARGETFSTYPE  > /dev/null 2>&1
	if [ $? -eq 0 ]; 
        then
                cat /proc/mounts | grep -w $i > /dev/null 2>&1
                if [ $? -eq 0 ] ;
                then
                        __print "WARNING" "$PRGNAME" "SKIPPING mounted partition $i"
                else
                        __print "INFO" "$PRGNAME" "ADDED $__DUMMY Partition $i "
                        FINALLIST=$(echo $FINALLIST $i)
                fi
        else
                __print "WARNING" "$PRGNAME" "SKIPPING $__DUMMY Partition $i is not proper FStype"
        fi
done
	
if [ "A$FINALLIST" == "A" ] ; 
then
                __print "INFO" "$PRGNAME" "No partition found in $LIST"
		exit 0
fi

__print "INFO" "$PRGNAME" "Disk list is $FINALLIST"
#blkid -s TYPE  /dev/sda1  | cut -d = -f 2 | sed s/\"//g | grep -w ext4


for i in $(echo $FINALLIST) ; 
do	
	__LABEL=$(blkid -s LABEL $i  |  cut -d = -f 2 | sed s/\"//g)
	if [ ${__LABEL:=NULL} == "NULL" ]; 
	then
		__print "ERROR" "$PRGNAME" "Disk $i has no label or NULL, skipping"
		continue
	fi
	__LABEL=$(echo $__LABEL) 
	__DEVICE=$(basename $i)
	__TARGETFILE=$TARGETDIR/$__LABEL-$__DEVICE.fsa
	if [ -f $__TARGETFILE ] ;
	then
		if [ $OVERWRITE -ne 1 ]; 
		then
			__print "ERROR" "$PRGNAME" "File $__TARGETFILE exist and overwrite is off, skipping"	
			continue
		else
			__print "WARNING" "$PRGNAME" "File $__TARGETFILE exist and overwrite is ON"
		fi
	fi
	__print "INFO" "$PRGNAME" "Starting Backup of $i on $__TARGETFILE"
	time fsarchiver savefs  -o $__TARGETFILE $BASEARGS $i
done
