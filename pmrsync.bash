#!/bin/bash

#HDSOURCE=/dev/sda2
#DIRSOURCE=/w7
#HDDEST=/dev/sdb1
#DIRDEST=/mnt/SAVEFAT
#SYNCDIR=data/

PROPFILE=rsync.prop

prtmsg() {
	printf "%-20s %-20s \n" "$1" "$2"
}

usage() {
cat << fin
sync according $PROPFILE file entry
	-c Create dest dir when non existing
	-f entry force mount of input and ouput FS	
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

FORCEMOUNT=0
CREATEDESTDIR=0
EXSTAT=0 

BASEARGS="avxtz --progress"

EXARGS="--exclude .cache "

while getopts cdfhS sarg
do
case $sarg in
        c)      CREATEDESTDIR=1 ;;
        d)      set -x
                DEBUG=1 ;;
        f)      FORCEMOUNT=1
                ;;
        h)      usage
                end;;
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
	SYNCDIR=$(echo $line | cut -d '|' -f 1)
	HDSOURCE=$(echo $line | cut -d '|' -f 2|cut -d ':' -f 1) 
	DIRSOURCE=$(echo $line | cut -d '|' -f 2|cut -d ':' -f 2)

	if [ ! -d $DIRSOURCE/$SYNCDIR ] ;
	then
		prtmsg "ERROR" "Source dir  $DIRSOURCE/$SYNCDIR not found"	
		continue
	fi	 
	HDDEST=$(echo $line | cut -d '|' -f 3|cut -d ':' -f 1) 
	DIRDEST=$(echo $line | cut -d '|' -f 3|cut -d ':' -f 2) 
	if [ ! -d $DIRDEST/$SYNCDIR ] ;         
        then     
                prtmsg "ERROR" "Dest dir  $DIRDEST/$SYNCDIR  not found" 
		if [ $CREATEDESTDIR -eq 1 ] ;
		then  
			mkdir -p $DIRDEST/$SYNCDIR > /dev/null 2>&1                  
			if [ ! $? ] 
			then
				prtmsg "ERROR" "Cant create $DIRDEST/$SYNCDIR" 
                		continue 
			else
				prtmsg "INFO" "$DIRDEST/$SYNCDIR created"
			fi
		else
			continue
		fi
        fi         
	ARGS=$BASEARGS
	ARGS="${BASEARGS} ${EXARGS}"
	prtmsg "INFO"  "rsync -$ARGS $DIRSOURCE$SYNCDIR/ $DIRDEST$SYNCDIR/"
	echo -n "Continue : "
	read dummy   </dev/tty
	#[[ $EXSTAT -eq 1 ]] && ARGS="$ARGS --stats" 
	rsync -$ARGS $DIRSOURCE$SYNCDIR/ $DIRDEST$SYNCDIR/
done < ./$PROPFILE


