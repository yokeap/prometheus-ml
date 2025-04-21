#!/bin/bash

echo "USAGE: run_of.sh dexfile stlfile"
if [ -z "$1" ]
  then
    echo "No dex file is not supplied"
    exit 1
  fi

if [[ $1 != *.dex ]]
    then
        echo "First Argument must be a .dex file"
        exit 2
    fi
if [ -z "$2" ]
  then
    echo " STL file is required "
    exit 2
  fi

if [[ $2 != *.stl ]]
    then
        echo "Second argument must be a .stl file"
        exit 2
    fi

# if [ -z "$3" ]
#   then
#     echo " AOA is required "
#     exit 2
# fi


echo "*** Preprocessing *** "s
# python3 ./dex_of.py $1 --infile $2 
cd ./hull_opt
echo "*** Cleaning and Running OF ***"
# ./Allclean; ./Allrun &> hull_opt.log
echo "*** PostProcessing ***"
echo "*** Results ***" >> results.log
echo " ----- Pressure and Viscous ---- " >> results.log
tail -50 log.foamRun | grep "forces forces write:" -A 8  >> results.log
echo "*** ALL DONE ***"