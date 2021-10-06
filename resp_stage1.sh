#!/bin/bash

# Default arguements
NAME="MOL"
NETCHARGE=0
DIR=$(pwd)

# Parse the command line
while getopts n:c:d:o: flag
do
    case "${flag}" in
	n) NAME=${OPTARG};;
	c) NETCHARGE=${OPTARG};;
	d) DIR=${OPTARG};;
    esac
done 

# If name.mol2 not in directrory, exit
usage () { echo "Usage: ./resp_stage1.sh -n NAME -c CHARGE -d DIRECTORY"; exit 1;}

# General resp protocol
gen_resp () {

    if [ ! -f $1.pdb ]; then
	usage
    fi

    grep -F -v CONECT $1.pdb > geo.pdb
    sed -i -e 's/\FA/F /' geo.pdb
    sed -i -e 's/\FB/F /' geo.pdb
    sed -i -e 's/\FC/F /' geo.pdb
    sed -i -e 's/\FD/F /' geo.pdb
    sed -i -e 's/\FE/F /' geo.pdb
    sed -i -e 's/\FF/F /' geo.pdb
    sed -i -e 's/\FG/F /' geo.pdb
    sed -i -e 's/CL/C /' geo.pdb

    # Generate Gaussian input file, single point HF/6-31*
    antechamber -i geo.pdb -fi pdb -o geo.dat -fo gcrt -gv 1 -ge geo.gesp
    sed -i -e 's/\opt//' geo.dat
    sed -i -e "s/\0   1/${NETCHARGE}  1/" geo.dat
    sed -i -e "s/\ 1   1/${NETCHARGE}  1/" geo.dat
    
    ./run_job.sh rung16 geo.dat

    # Convert from Guassian electrostatic potential
    espgen -i geo.gesp -o geo.esp

    # 1st and 2nd iteration of the RESP procedure
    resp -O -i resp1.in -o resp1.out -p resp1.pch -t resp1.chg -q resp.qin -e geo.esp
    resp -O -i resp2.in -o resp2.out -p resp2.pch -t resp2.chg -q resp1.chg -e geo.esp

}

cp run_job.sh $DIR
cd $DIR

# Get all the stage 1 folders in an array
folders=`ls -d ./stage1*`
folders=( $folders )
if [ -z $folders ]; then
    usage
fi

# Multiple primary conformations
for conform in ${folders[@]}; do

    cp run_job.sh resp* $conform
    cd $conform

    gen_resp $NAME

    cd ..

done

echo ""
echo "Check the \"resp2.out\" file for each conformation to verify charges are reasonable."

exit 0
