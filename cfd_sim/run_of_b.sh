#!/bin/bash

echo "USAGE: run_of.sh dexfile stlfile aoa "
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

if [ -z "$3" ]
  then
    echo " AOA is required "
    exit 2
fi

fname=`echo "$1" | cut -d'.' -f1`

echo $fname

echo "*** Preprocessing *** "
python /home/aimed_user/dex_of/dex_of.py  $1 --infile $2 --aoa $3 --casefoldername dir_${fname}_aoa_$3
cd dir_${fname}_aoa_$3
echo "*** Cleaning and Running OF ***"
./Allclean; ./Allrun &> dir_${fname}_aoa_$3.log
echo "*** PostProcessing ***"
echo "*** Results ***" >> results.log
echo " ----- LIFT AND DRAG FORCES ---- " >> results.log
tail -13 log.simpleFoam |head -8 >> results.log
echo " ----- LIFT AND DRAG COEFFICIENTS ---- " >> results.log
tail -50 log.simpleFoam | grep "Cd       :" |tail -1 >> results.log
tail -50 log.simpleFoam | grep "Cl       :" |head -1 >> results.log
tail -50 log.simpleFoam | grep "Cs       :" |head -1 >> results.log
echo "___ REFERENCE AREAS ----" >> results.log
echo "Arefs" >> results.log
find ./postProcessing -name "coefficient.dat" -exec grep -H Aref {} \; >> results.log
echo "lrefs:" >> results.log
find ./postProcessing -name "coefficient.dat" -exec grep -H lRef {} \; >> results.log
echo "----- MESH DENSITIES & CPU TIMES ----- "
grep -H ells  dir_${fname}_aoa_$3.log  >> results.log
grep -H "Finished meshing in"  log.snappyHexMesh >> results.log
echo " Converged In:"
grep "Time =" log.simpleFoam | tail -2 >> results.log
echo "Results stored in dir_${fname}_aoa_$3/results.log"
cat ./results.log
cd ..
echo "*** ALL DONE ***"
