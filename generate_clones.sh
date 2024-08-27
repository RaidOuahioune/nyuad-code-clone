#!/bin/bash

# Check if the --level argument is provided
if [ -z "$1" ] || [ "$1" != "--level" ] || [ -z "$2" ]; then
  echo "Usage: $0 --level <level>"
  exit 1
fi

LEVEL=$2
FILENAME="level${LEVEL}.txt"

# Run the Python scripts
rm  *.txt
rm *.csv

python tinypy_generator.py --level $LEVEL --filename $FILENAME
python main.py --input $FILENAME

rm data/$FILENAME/*.txt
python preparation.py --source "clones_${FILENAME}"
 
mv clone_count.txt data/"clones_${FILENAME}"/clone_count.txt
rm *.txt
mv meta_clone.csv data/"clones_${FILENAME}"/meta_clone.csv
mv meta_non_clones.csv data/"clones_${FILENAME}"/meta_non_clones.csv
