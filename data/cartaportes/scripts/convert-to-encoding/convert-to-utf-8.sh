#!/bin/bash
#loop to convert multiple files 
mkdir "utf-8"
for  file  in  *.txt; do
	FROM_ENCODING=`file -i $file|cut -d"=" -f2`
    cmm="iconv -f $FROM_ENCODING -t utf-8  $file>utf-8/$file"
	echo $cmm
	eval $cmm
done
exit 0
