#!/bin/bash

# Default arguements
NAME="MOL"
DIR=$(pwd)

# Parse the command line
while getopts n:c:d:r: flag
do
    case "${flag}" in
    	n) NAME=${OPTARG};;
      c) CHARGE=${OPTARG};;
    	d) DIR=${OPTARG};;
      r) RESIDUE_ID=${OPTARG};;
    esac
done

# If name.mol2 not in directrory, exit
usage() { echo "Usage: ./stage2_charges.sh -n NAME -c CHARGE -d WORKING_DIR \
            -r RESIDUE_ID"; exit 1;}

# Set up directrories
HOME=$(pwd)
cd $DIR
DIR=$(pwd)
if [ -z $RESIDUE_ID ]; then
  RESIDUE_ID=$NAME
fi

# Get all the stage 2 folders in an array
stage2_dirs=`ls -d ./stage2*`
stage2_dirs=( $stage2_dirs )
if [ -z ${stage2_dirs[0]}/${NAME}.pdb ]; then
    usage
fi

# Extract the configurations from each conformation
for conform in ${stage2_dirs[@]}; do

  cd $DIR
  cp run_job.sh resp1.in resp2.in resp.qin $conform
  cd $conform
  conform=$(pwd)
  #python ${HOME}/extract_conformations.py $NAME

  # make a list of the configuration subdirectories
  configs=($(find . -type d -name "config_*"))

  # run single point calculation for every configuration
  for config in ${configs[@]}; do

    cd $conform
    cp run_job.sh resp1.in resp2.in resp.qin $config
    cd $config

    # remove all lines containing the string 'CONECT' from geo.pdb
    grep -F -v CONECT geo.pdb > geo.pdb.tmp && mv geo.pdb.tmp geo.pdb
    sed -i -e 's/\FA/F /' geo.pdb
    sed -i -e 's/\FB/F /' geo.pdb
    sed -i -e 's/\FC/F /' geo.pdb
    sed -i -e 's/\FD/F /' geo.pdb
    sed -i -e 's/\FE/F /' geo.pdb
    sed -i -e 's/\FF/F /' geo.pdb
    sed -i -e 's/\FG/F /' geo.pdb
    sed -i -e 's/  CL/  C /' geo.pdb
    sed -i -e 's/  CL/  C /' geo.pdb

    # make gaussian input
    #antechamber -i geo.pdb -fi pdb -o geo.dat -fo gcrt -gv 1 -ge geo.gesp

    # edit calculation options
    sed -i -e "s/\opt//" geo.dat
    sed -i -e "s/\0   1/$CHARGE  1/" geo.dat
    sed -i -e "s/\ 1   1/$CHARGE  1/" geo.dat

    # run job to get ESP
    #./run_job.sh rung16 geo.dat
    if [ ! -f resp1.chg ]; then
      espgen -i geo.gesp -o geo.esp

      # RESP procedure in 2 iterations
      resp -O -i resp1.in -o resp1.out -p resp1.pch -t resp1.chg -q resp.qin -e geo.esp
      resp -O -i resp2.in -o resp2.out -p resp2.pch -t resp2.chg -q resp1.chg -e geo.esp

    fi

  done

done

cd $HOME

python ave_charges.py $NAME $DIR $RESIDUE_ID 2
