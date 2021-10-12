#!/bin/bash

# Default arguements
NAME="MOL"
NETCHARGE=0
DIR=$(pwd)
FF="/home/finnl92/thesis/ff/amber14sb_sp.ff"

# Parse the command line
while getopts n:c:d:ff: flag
do
    case "${flag}" in
	n) NAME=${OPTARG};;
	c) NETCHARGE=${OPTARG};;
	d) DIR=${OPTARG};;
	ff) FF=${OPTARG};;
    esac
done

# If name.mol2 not in directrory, exit
usage() { echo "Usage: ./initialize_stage2.sh -n NAME -c CHARGE -d WORKING_DIR -ff PATH_TO_FORCE_FIELD"; exit 1;}

MDP=$(pwd)
cd $DIR
DIR=$(pwd)

# Get all the stage 1 folders in an array
stage1_dirs=`ls -d ./stage1*`
stage1_dirs=( $stage1_dirs )
if [ -z ${stage1_dirs[0]}/${NAME}.pdb ]; then
    usage
fi

mkdir -p stage2
cp "${stage1_dirs[0]}/${NAME}.pdb" stage2
cd stage2
cp -r $FF $FF/residuetypes.dat .

# Generate topology using .pdb of capped residue
gmx18 pdb2gmx -ff amber14sb_sp -f ${NAME}.pdb -o ${NAME}.gro -water tip3p -ignh -nobackup

# Define box with ligand at center, >1.2 nm to edge
gmx18 editconf -f ${NAME}.gro -o ${NAME}_box.gro -c -d 1.2 -bt cubic -nobackup

# Solvate Ligand with TIP3P
gmx18 solvate -cp ${NAME}_box.gro -cs spc216 -o ${NAME}_solv.gro -p topol.top -nobackup

# Add Ions
gmx18 grompp -f ${MDP}/minim_steep.mdp -c ${NAME}_solv.gro -p topol.top -o ions.tpr -maxwarn 1 -nobackup
gmx18 genion -s ions.tpr -o ${NAME}_solv_ions.gro -p topol.top -np $NETCHARGE -pname NA -pq 1 -nobackup

cd $DIR
