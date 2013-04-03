#!/bin/bash

# This script must have propery file as defined below 
PROPFILE=pmrsync.prop
# Format is fields separated by | as 
# sourcedir|exclude pattern|dest dir|option
# option field is still ongoing 


prtmsg() {
	printf "%-20s %-20s \n" "$1" "$2"
}

usage() {
cat << fin
sync according $PROPFILE file entry
	-c Create dest dir when non existing
	-n Do not prompt before starting rsync 
	-S put extanded stat transfert report (rsync)
fin
}

end() {
	exit
}

check_dir() {

if [ ! -f  ./$PROPFILE ] ;
then
	prtmsg "ERROR" "file ./$PROPFILE not found"
	exit
fi
}
	
check_dir

CREATEDESTDIR=0
EXSTAT=0
PROMPT=1 

BASEARGS="avxtz --progress"

EXARGS="--exclude .cache "

while getopts cdhnS sarg
do
case $sarg in
        c)      CREATEDESTDIR=1 ;;
        d)      set -x
                DEBUG=1 ;;
        h)      usage
                end;;
        n)      PROMPT=0 ;;
	S)	EXSTAT=1 ;;
        *)      echo "ERROR : $PRGNAME : Bad option or misusage"
                usage
                end ;;
esac
done



while read line
do
	FIRST=$(echo $line | cut -c 1) 
	if [ A$FIRST == 'A#' ] ;
	then
		echo "commentaire" > /dev/null
		continue
	fi 
	#echo "$line"
	SOURCEDIR=$(echo $line | cut -d '|' -f 1)
	DESTDIR=$(echo $line | cut -d '|' -f 3)

	if [ ! -d $SOURCEDIR ] ;
	then
		prtmsg "ERROR" "Source dir  $SOURCEDIR not found"	
		continue
	fi

	FIRST=$(echo $DESTDIR | cut -c 1)
 	if [ ${FIRST:=NULL} != '/' ] ;
	then
		__DUMMY=$(pwd)
		DESTDIR=$__DUMMY/$DESTDIR
			
	fi
	if [ ! -d $DESTDIR ] ;         
        then     
                prtmsg "ERROR" "Dest dir  $DESTDIR  not found" 
		if [ $CREATEDESTDIR -eq 1 ] ;
		then  
			mkdir -p $DESTDIR > /dev/null 2>&1                  
			if [ ! $? ] 
			then
				prtmsg "ERROR" "Cant create $DESTDIR" 
                		continue 
			else
				prtmsg "INFO" "$DESTDIR created"
			fi
		else
			continue
		fi
        fi        
	
	EXARGS=""	
	EXCLUDELIST=$(echo $line | cut -d '|' -f 2)
	EXCLUDELIST=$(echo $EXCLUDELIST)
	if [ "${EXCLUDELIST:=EMPTY}" != "EMPTY" ];
	then
		for i in $(echo $EXCLUDELIST) ;
		do
			EXARGS="--exclude $i ${EXARGS}"
		done
	fi
 
	ARGS=$BASEARGS
	ARGS="${BASEARGS} ${EXARGS}"
	prtmsg "INFO"  "rsync -$ARGS $SOURCEDIR/ $DESTDIR/"
	if [ $PROMPT -ne 0 ];
	then
		echo -n "Continue : "
		read dummy   </dev/tty
	fi
	#[[ $EXSTAT -eq 1 ]] && ARGS="$ARGS --stats" 
	rsync -$ARGS $SOURCEDIR/ $DESTDIR/
	#echo "rsync -$ARGS $SOURCEDIR/ $DESTDIR/"
done < ./$PROPFILE


