#!/bin/bash

####
# This script is a wrapper for fsarchiver
# Basically check local device for ext4 FS and dump to file if not mounted
###


PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`


__print() {
# If 1st Param (level) is set to verbose it means that msg will display only in verbose mode 
# The displayed level will be info. Verbose mode is set by program VERBOSE var
if [ $# -lt 3 ];
then
        printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "Error Calling function __print"
fi
local __LEVEL=$1
shift
local __INFO=$1
shift
local __MSG="$*"
if [ $__LEVEL == "VERBOSE" ] ;
then
        [[ $VERBOSE -eq 1 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "INFO :" "$__INFO : " "$__MSG"
        return 0
else
        if [ ${SILENT:=0} -ne 1 ];
        then
                printf "%-10s %-10s %-22s %-30s \n" "$__LEVEL :" "$__INFO : " "$__MSG"
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


usage() {
cat << fin
<<<<<<< HEAD
$PRGNAME [-o] [-s] [ -D devide] [ -F <FSTYPE> ] -o -q [ -s /dev/devicename OR LABEL ] 
Backup file sytem using fsarchiver for default device $TARGETDISK
	-d	debug mode
	-D	Change target disk  to archive to
	-F	Filesytem type for the source device (by default just work for ext4)
	-h	This page 
	-o	Force overwrite when file exist
	-q	Silent mode (to be done)
	-s	source parition or label (only one and must be /dev/sd... or parition name as seen with blkid) to be backedup
	-t 	Target dir to write output file (if not specified $(pwd))
=======
$PRGNAME [-o] [-s] [ -D devide]
Backup file sytem using fsarchiver for default device $TARGETDISK
	-d	debug mode
	-D	Change target disk 
	-h	This page 
	-o	Force overwrite when file exist
	-s	Silent mode (to be done)
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
	-z	Compression level (as for fsarchiver)
fin
}

	
<<<<<<< HEAD
TARGETDIR=$(pwd)                                              |
TARGETDISK=/dev/sda
TARGETFSTYPE="ext4|ext3"
FORCEMOUNT=0
CREATEDESTDIR=0
#   obsolete FSTYPE="ext4|ext3" 
=======

TARGETDISK=/dev/sda
TARGETFSTYPE=ext4
FORCEMOUNT=0
CREATEDESTDIR=0
FSTYPE="ext4" 
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
SILENT=0
OVERWRITE=0
PROPFILE=ossync.prop
ZIPLEVEL=1
<<<<<<< HEAD
SOURCE=ALL
=======
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9

# time fsarchiver savefs  -o /media/pierre/SaveLinux/OS/Sidux-sda7.fsa -v -j2 -z 1 /dev/sda7


if [ ! -f  ./$PROPFILE ] ;
then
	__print "ERROR" "$PRGNAME" "file ./$PROPFILE not found, continue ?"
	read dummy	
fi

<<<<<<< HEAD
while getopts dDF:hoSs:t:z sarg
=======
while getopts dDhos sarg
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
do
case $sarg in
        d)      set -x
                DEBUG=1 ;;
	D)	TARGETDISK=$OPTARG;; 
<<<<<<< HEAD
	F)	TARGETFSTYPE="$OPTARG" ;; 
        h)      usage
                end;;
	o)	OVERWRITE=1 ;;
	q)	SILENT=1 ;;
	s)	SOURCE=$OPTARG ;;
	t)	TARGETDIR=$OPTARG ;;
=======
        h)      usage
                end;;
	o)	OVERWRITE=1 ;;
	s)	SILENT=1 ;;
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
	z)	ZIPLEVEL=$OPTARG;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done

# Building target list 
BASEARGS="-v -j2 -z $ZIPLEVEL"
<<<<<<< HEAD
if [ ${SOURCE:=NULL} == "ALL" ] ; 
then
	#LIST=$(blkid -o device | grep ${TARGETDISK:=NONE})
	LIST=$(blkid -o device) 
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

#blkid -s TYPE  /dev/sda1  | cut -d = -f 2 | sed s/\"//g | grep -w ext4

# Checking if device is mounted
for i in $(echo $LIST) ; 
do
	__DUMMY=$(blkid -s TYPE  $i  | cut -d = -f 2 | sed s/\"//g)
	echo $__DUMMY | egrep -e $TARGETFSTYPE 
	if [ $? -eq 0 ]; 
=======
LIST=$(blkid -o device | grep ${TARGETDISK:=NONE})
LIST=$(echo $LIST)
FINALLIST=""

__print "INFO" "$PRGNAME" "Disk list is $LIST"
#blkid -s TYPE  /dev/sda1  | cut -d = -f 2 | sed s/\"//g | grep -w ext4
for i in $(echo $LIST) ; 
do
	__DUMMY=$(blkid -s TYPE  $i  | cut -d = -f 2 | sed s/\"//g)
	if [ ${__DUMMY:=NULL} == "$TARGETFSTYPE" ]; 
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
	then
		cat /proc/mounts | grep -w $i > /dev/null 2>&1  
		if [ $? -eq 0 ] ; 
		then 
<<<<<<< HEAD
			__print "ERROR" "$PRGNAME" "Disk $i is $TARGETFSTYPE BUT mounted" 
=======
			__print "WARNING" "$PRGNAME" "Disk $i is $TARGETFSTYPE BUT mounted" 
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
		else
			__print "INFO" "$PRGNAME" "Disk $i is $TARGETFSTYPE" 	
			FINALLIST=$(echo $FINALLIST $i)
		fi
<<<<<<< HEAD
	else
		__print "ERROR" "$PRGNAME" "Disk is not proper FStype $TARGETFSTYPE"
		end 2
	fi
done

# do the job
=======
		
	fi
done

>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
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
<<<<<<< HEAD
	__TARGETFILE=$TARGETDIR/$__LABEL-$__DEVICE.fsa
=======
	__TARGETFILE=$(pwd)/$__LABEL-$__DEVICE.fsa
>>>>>>> 1d86e530b7a56c0f8b9560190c588e037ed101d9
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
