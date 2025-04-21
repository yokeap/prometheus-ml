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


echo "*** Preprocessing *** "
python3 ./dex_of.py $1 --infile $2 
rm -f stl_cfd/ship_gen.stl
cd ./hull_opt
pwd
echo "*** Cleaning and Running OF ***"
./Allclean; ./Allrun &> hull_opt.log

# tail -100 postProcessing/forces/0/forces.dat | awk -F "[( )]+" '{print $1, -2*$3, -2*$6, 2*(-$3-$6)}' > forces_hull.dat
# echo "*** PostProcessing ***"
# echo "*** Results ***" >> results.log
# tail -50 log.foamRun | grep "forces forces write:" -A 8  >> results.log

# # Filename for input
# FORCES_FILE="forces_hull.dat"

# # Check if forces.dat file exists
# if [ ! -f "$FORCES_FILE" ]; then
#     echo "Error: $FORCES_FILE not found!"
#     exit 1
# fi

# # Initialize variables
# total_resistance_sum=0
# total_pressure_sum=0
# total_viscous_sum=0
# num_steps=0

# # Read forces.dat line by line, skipping comment lines
# while read -r line; do
#     # Skip comments or header lines
#     if [[ $line == \#* ]]; then
#         continue
#     fi

#     # Read columns from forces.dat
#     # the file format: time  Fx_pressure Fx_viscous Resistance  (that's double times for full hull)
#     time=$(echo $line | awk '{print $1}')
#     Fx_pressure=$(echo $line | awk '{print $2}')
#     Fx_viscous=$(echo $line | awk '{print $3}')

#     # Calculate total resistance at this time step
#     total_resistance=$(echo "$Fx_pressure + $Fx_viscous" | bc -l)

#     # Accumulate total resistance for averaging
#     total_pressure_sum=$(echo "$total_pressure_sum + $Fx_pressure" | bc -l)
#     total_viscous_sum=$(echo "$total_viscous_sum  + $Fx_viscous" | bc -l)
#     total_resistance_sum=$(echo "$total_resistance_sum + $total_resistance" | bc -l)
#     num_steps=$((num_steps + 1))

# done < "$FORCES_FILE"

# # Compute average resistance
# if [ $num_steps -eq 0 ]; then
#     echo "Error: No data found in $FORCES_FILE"
#     exit 1
# fi

# average_total_pressure=$(echo "$total_pressure_sum / $num_steps" | bc -l)
# average_total_viscous=$(echo "$total_viscous_sum / $num_steps" | bc -l)
# average_total_resistance=$(echo "$total_resistance_sum / $num_steps" | bc -l)

# rm -f ./forces_hull.dat

# Extract time and total_x (i.e., total resistance in x-direction)
tail -100 postProcessing/forces/0/force.dat | awk '{if ($1 ~ /^#/) next; printf "%s %.10f\n", $1, $2}' > forces_hull.dat

echo "*** PostProcessing ***"
echo "*** Results ***" >> results.log
tail -50 log.interFoam | grep "forces forces write:" -A 8  >> results.log

FORCES_FILE="forces_hull.dat"

if [ ! -f "$FORCES_FILE" ]; then
    echo "Error: $FORCES_FILE not found!"
    exit 1
fi

total_resistance_sum=0
num_steps=0

while read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue

    time=$(echo $line | awk '{print $1}')
    total_resistance=$(echo $line | awk '{print $2}')

    total_resistance_sum=$(echo "$total_resistance_sum + $total_resistance" | bc -l)
    num_steps=$((num_steps + 1))
done < "$FORCES_FILE"

if [ $num_steps -eq 0 ]; then
    echo "Error: No valid data found in $FORCES_FILE"
    exit 1
fi

average_total_resistance=$(echo "$total_resistance_sum / $num_steps" | bc -l)

average_total_resistance=$(echo "$average_total_resistance*-2" | bc -l)

echo "Average Total Resistance: $average_total_resistance"

rm -f ./forces_hull.dat



# Output the average total resistance
echo "Average total: " >> results.log
echo "      pressure: $average_total_pressure" >> results.log
echo "      viscous: $average_total_viscous" >> results.log
echo "      resistance: $average_total_resistance" >> results.log
# echo "Average total resistance: $average_total_resistance N"
# echo "Average total resistance: $average_total_resistance N"

echo "*** ALL DONE ***"
