#!/bin/bash

#
#	manifestonosuke@gmail.com
# This script ease vbox command line for basic actions like stop/start/status ...
# Options are in usage() and can be check from cli with -h option 
#
#


# Determine program name
PRGDIR=`type $0 | awk '{print $3}'`
PRGNAME=`basename $0`
PRGNAME=`basename $0 |  awk -F '.' '{print $1}'`

# Get absolute path name of the script
PWD=`pwd`
DIRNAME=`dirname $0| sed 's/^\.//'`
LIB="$PWD/$DIRNAME"

# Debug variable
DEBUG=0

trap 'trapfunc' 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17

function trapfunc {
printf "%-10s %-10s %-22s %-30s \n" "Info :" "$PRGNAME : " "Program aborted"
end
exit
}

function usage {
cat << FIN
Handle command line for vbox easily
Run without arg will list vbox on the machine 
usage : $PRGNAME 
        -d : run in debug mode
	-l : List VM with power status only (State)
	-p : pause the vbox 
	-r : resume the vbox
	-R : Reset the vbox	
	-s : start the vbox
	-S : Give summary status of a named vm OR all vm is all is passed as parameter (bad if you have a vm called all)
	-O : Power OFF the vbox
	-v : full verbose mode (will list all vbox command runned)
FIN
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

function check_user() {
__USER=$1 
__VBOXGROUP=$2
if [ $__USER == "root" ];
then
	__print "VERBOSE" "$PRGNAME" "Perm check : Root user allowed by default for Vbox"
else
	__NEEDED_ID=$(getent group $__VBOXGROUP| cut -d ':' -f 3)
	__GROUP_USER=$(id -G $__USER)
	if [ $? -ne 0 ];
	then
		__print "ERROR" "$PRGNAME" "Cant get $__USER groups"
		end 3
	fi
	echo $__GROUP_USER  | egrep -w $__NEEDED_ID > /dev/null 
	if [ $? -ne 0 ];
	then
		__print "ERROR" "$PRGNAME" "$__USER dont belong to $__VBOXGROUP($__NEEDED_ID)"
		end 3
	fi
fi
return 0
}


function rundiag() {
echo > /dev/null
}


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

vbox_list_dry(){
local __LIST=$(VBoxManage list vms  | awk '{print $1}'  |sed s/\"//g)
__LIST=$(echo $__LIST)
if [ $? -ne 0 ];
then
	__print "ERROR" "$0" "Fail to return list of vm"
	return 1
else
	__print "INFO" "$PRGNAME" "$__LIST"	
fi
}

# 1 arg => silent response $?
# more than 1 arg => optionnal args
vbox_exist() {
local __VBOX=$1
local __VBOX_LIST=$(vbox_list_dry| cut -d ':' -f 3-)
echo $__VBOX_LIST | egrep -w $__VBOX  > /dev/null
local __REZ=$? 
if [ $# -eq  1 ] ;
then	
	return $__REZ
else
	case $2 in 
	V)	if [ $__REZ -eq 0 ] ;
		then
			__print "INFO" "$PRGNAME" "$__VBOX is existing"
		else
			__print "INFO" "$PRGNAME" "$__VBOX is NOT existing"
		fi
		;;
	esac
fi
}


vbox_status() {
local __PARAM=$1
if [ $(echo $__PARAM | tr '[:lower:]' '[:upper:]')  == "ALL" ] ; 
then
	local __LIST=$(vbox_list_dry| awk -F ":" '{print $3}')
else
	local __LIST=$__PARAM
fi

for i in $(echo $__LIST) ; 
do
if vbox_exist $i ;
then
	echo "** VM : $i"
	VBoxManage showvminfo --machinereadable $i | awk -F '=' '
$1 ~ /^ostype/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^VMState\y/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^memory/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^cpus/ {printf "%s:%s\n",$1,$2} 
' | sed s/\"//g | sed 's/:/		:	/' 

	local __IP=$(VBoxManage guestproperty get $i /VirtualBox/GuestInfo/Net/0/V4/IP | awk -F ':' '{print $2}')
	echo "IP Address	:	$__IP"
else
	__print "ERROR" "$PRGNAME" "$OPTARG VM is not existing"
fi
done 
}

vbox_run_status() {
local __LIST=$(vbox_list_dry| awk -F ":" '{print $3}')
for i in $(echo $__LIST) ; 
do
	__STATUS=$(VBoxManage showvminfo $i | grep State | cut -d ':' -f 2- | sed 's/  */ /g'| sed 's/  *$//')
	__print "INFO" "$PRGNAME" "$i : $__STATUS"
done
}


unset LC_CTYPE
unset LANG

DEBUG=0
TMPF1=/tmp/$PRGNAME.tmp
TYPE="NONE"
MOUNT=0
LABEL=ext4
MANAGE=NULL
TARGET=NULL
VERBOSE=0
VBOXGROUP=vboxusers

USER=$(getent passwd $(id -u) | cut -d ':' -f1)
check_user $USER $VBOXGROUP

if [ $# -eq 0 ] ;
then
	vbox_list_dry
	end 0
fi


while getopts dG:hO:lp:r:R:s:S:v sarg
do
case $sarg in
        d)      set -x
        	DEBUG=1 ;;
	G)	if vbox_exist $OPTARG ;
		then
			VBoxSDL --startvm  $OPTARG  > /dev/null 2>&1 &	
		else
			__print "ERROR" "$PRGNAME" "$OPTARG VM is not existing"
		fi
		end
		;;
        h)      usage
                end ;;
	l)	vbox_run_status 
		end ;;
	O|p|r|R|s) if vbox_exist $OPTARG ;
			then
				MANAGE=$sarg
				TARGET=$OPTARG
			else    
				__print "ERROR" "$PRGNAME" "$OPTARG VM is not existing"
		fi
		end
		;;
	S)	TARGET=$OPTARG
		vbox_status $TARGET
		end
		;;
	v)	VERBOSE=1	
		;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done

if [ ${MANAGE:=NULL} != "NULL" ];
then
	case $MANAGE in
	0)	VBoxManage controlvm $TARGET poweroff
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not powerd off" 
		end $?
	;;
	p)	VBoxManage controlvm $TARGET pause 
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not pause" 
		end $?
	;; 
	r)	VBoxManage controlvm $TARGET resume 
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not resumed" 
		end $?
	;; 
	R)	VBoxManage controlvm $TARGET reset 
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not reset" 
		end $?
	;; 
	s)	nohup VBoxHeadless --startvm $TARGET > $TMPF1 2>&1 &
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not started" 
		end $?
	;; 
	O)	VBoxManage controlvm $TARGET acpipowerbutton 
		REZ=$?
		[[ $REZ -ne 0 ]] &&  printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "$TARGE not powered down" 
		end $?
	;; 
	*)	__print "ERROR" "PRGNAME" "Oh you shouldnt have come to this, probably a bug"
		end 3 ;;
	esac
else
	__print "ERROR" "$PRGNAME" "Error in retrieving task to do"
	end 2
fi


exit

