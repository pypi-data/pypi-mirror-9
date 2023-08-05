#!/bin/bash

# filter taxons or accessions from MALT'ed SAM file
# expects tab-delimited CSV file with NCBI taxonomy IDs or accession in first
# column
# author: Florian Aldehoff <f.aldehoff@student.uni-tuebingen.de>

if [ $# -lt 3 ]; then
    echo 'usage: filter_by_list.sh keep|discard read|taxon|accession input.sam list.csv'
    exit 1
fi

if [ "$1" != "keep" ] && [ "$1" != "discard" ]; then
	echo 'missing required command: keep | discard'
    exit 1
fi

if [ "$2" != "read" ] && [ "$2" != "taxon" ] && [ "$2" != "accession" ]; then
	echo 'missing required command: read | taxon | accession'
    exit 1
fi

if [[ $3 != *.sam ]]; then
    echo 'wrong file type given, expecting sam extension'
    exit 1
fi

if [[ $4 != *.csv ]]; then
    echo 'wrong file type given, expecting csv extension'
    exit 1
fi

# prepare pattern list from CSV
cut -f 1 $4 | while read -r LINE; do
	if [ "$2" == "read" ]; then
		PATTERN="${LINE}"
	elif [ "$2" == "taxon" ]; then
		PATTERN="tax|${LINE}|"
	elif [ "$2" == "accession" ]; then
		PATTERN="|${LINE}|"
	fi
	echo ${PATTERN} >> pattern.tmp
done

# filter SAM file
FILENAME=$(basename "$3" .sam)
if [ "$1" == "keep" ]; then
	GREP_OPTION=''
elif [ "$1" == "discard" ]; then
	GREP_OPTION='-v'
fi
grep ${GREP_OPTION} -f pattern.tmp $3 > ${FILENAME}.filtered.sam

# clean up
rm pattern.tmp

exit 0