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
usage() { echo "Usage: ./initialize_stage1.sh -n NAME -c CHARGE -d DIRECTORY"; exit 1;}

cd $DIR

# Get all the mol files in an array
molfiles=`ls ./$NAME_*.mol2`
molfiles=( $molfiles )
if [ -z molfiles ]; then
    usage
fi

# For just one conformation 
if [ ${#molfiles[@]} -eq 1 ]; then

    if [ ! -f ${NAME}.mol2 ]; then
	usage
    fi

    mkdir -p stage1
    cp ${NAME}.mol2 stage1
    cd stage1
    
    acpype -di ${NAME}.mol2 -n 

    cp ${NAME}.acpype/${NAME}_NEW.pdb ./${NAME}.pdb

fi

# Multiple primary conformations
for conform in ${molfiles[@]}; do
    
    conform=${conform/.\/${NAME}_/}
    conform=${conform/.mol2/}
    mkdir -p stage1_$conform

    cp ${NAME}_${conform}.mol2 stage1_${conform}/${NAME}.mol2
    cd stage1_${conform}

    acpype -di ${NAME}.mol2 -n $NETCHARGE

    cp ${NAME}.acpype/${NAME}_NEW.pdb ./${NAME}.pdb
    cd ..

done

echo ""
echo "Prepare the file ${NAME}.pdb
Reorder the atoms in $NAME.pdb so they appear in the desired order for your residue
For peptides, make sure individual residues are grouped together according to C-terminal --> N-terminal
Change the residue name from UNL accordingly

Yes, this step is a bit tedious, but crucial!"

exit 0
