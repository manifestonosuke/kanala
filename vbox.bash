#!/bin/bash
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
	-S : Give summary status of all VM's
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

function rundiag() {
echo > /dev/null
}

####printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "mount_device : " "Arg not OK  $#"
__print() {
if [ $# -lt 3 ];
then
	printf "%-10s %-10s %-22s %-30s \n" "ERROR :" "$PRGNAME : " "Error Calling function __print"	
fi
local __LEVEL=$1 
shift
local __INFO=$1
shift
local __MSG="$*"
if [ ${SILENT:=0} -ne 1 ];
then
	printf "%-10s %-10s %-22s %-30s \n" "$__LEVEL :" "$__INFO : " "$__MSG"
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

vbox_status() {
local __LIST=$(vbox_list_dry| awk -F ":" '{print $3}')
for i in $(echo $__LIST) ; 
do
echo "VM : $i"
VBoxManage showvminfo $i | awk -F ':' '
$1 ~ /^OS type/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^State/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^Memory size/ {printf "%s:%s\n",$1,$2} 
$1 ~ /^Number of CPUs/ {printf "%s:%s\n",$1,$2} 
' 
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
TYPE="NONE"
MOUNT=0
LABEL=ext4
MANAGE=NULL
TARGET=NULL

if [ $# -eq 0 ] ;
then
	vbox_list_dry
	end 0
fi


while getopts dhO:lp:r:R:s:S sarg
do
case $sarg in
        d)      set -x
        	DEBUG=1 ;;
        h)      usage
                end ;;
	l)	vbox_run_status 
		end ;;
	O|p|r|R|s)	MANAGE=$sarg
		TARGET=$OPTARG
		;;
	S)	vbox_status
		end
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
	end $?
	;;
	p)	VBoxManage controlvm $TARGET pause 
	end $?
	;; 
	r)	VBoxManage controlvm $TARGET resume 
	end $?
	;; 
	R)	VBoxManage controlvm $TARGET reset 
	end $?
	;; 
	O)	VBoxManage controlvm $TARGET reset 
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

