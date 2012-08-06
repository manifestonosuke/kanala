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
#echo "trapped"
printf "%-10s %-10s %-22s %-30s \n" "Info :" "$PRGNAME : " "Program aborted"
end
exit
}

function usage {
cat << FIN
switch off extra video card
usage : $PRGNAME 
	-c : check battery state and exit (see -L)
	-C : Do check before and after changing acpi mode 
        -d : run in debug mode 	
	-L : Loop (only with -c only option)
	-p : change acpi module dir to this path 
	-v : full verbose mode
	-0 : try to turn OFF discrete card
	-1 : try to turn ON discrete card
        
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
#cat /proc/acpi/battery/BAT0/info 
#cat /proc/acpi/battery/BAT0/state
grep rate /proc/acpi/battery/BAT0/state 
}

DO=OFF
CHECK=0
PPCHECK=0
TEMPO=3 
LOOP=0

DIR=/root/acpi_call
MODULE=acpi_call.ko
MODULESHORT=$(echo $MODULE | cut -d '.' -f 1)

while getopts cCdhLp:v10 sarg
do
case $sarg in
        c)      CHECK=1 ;; 
	C)	PPCHECK=1 ;; 
        d)      set -x
        	DEBUG=1 ;;
        h)      usage
                end;;
	L)	LOOP=1 ;;
	p)	DIR=$OPTARG ;;
	1)	DO=ON ;;
	0)	DO=OFF ;;
        v)      LOWER=1 ;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done


cd $DIR
(lsmod | grep -q $MODULESHORT)
if [ $? -ne 0  ]; 
then
	insmod $MODULE
if [ $? -ne 0 ] ;
then
	echo "$PRGNAME : error : cant load module $MODULE" 
	exit 1
fi
fi
	
if [ ${CHECK:=0} -eq 1 ];
then
	rundiag
	if [ ${LOOP:=O} -eq 0 ] ;
	then
		exit
	else
		while [ true ] ; 
		do
			rundiag 
			sleep $TEMPO
		done
	fi
fi

if lsmod | grep -q $MODULESHORT; then
    method="
    \_SB.PCI0.PEG1.GFX0._$DO
    "

	if [ ${PPCHECK:=O} -eq 1 ] ;
	then
		rundiag
	fi
	#echo -n "Switching $method: "
        echo $method > /proc/acpi/call
        result=$(cat /proc/acpi/call)
        case "$result" in
        Error*)
            echo "$PRGNAME : error : turning $DO failed"
        ;;
        *)
            echo "$PRGNAME : info : turning $DO works"
        ;;
        esac
	if [ ${PPCHECK:=O} -eq 1 ] ;
	then
		echo "Sleep $TEMPO sec before check"
		sleep $TEMPO
		rundiag
		exit
	fi
else
	echo "$PRGNAME : error : module $MODULE not loaded" 
    exit 1
fi
