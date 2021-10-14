#!/bin/bash

NAME="MOL"
MDP=$(pwd)
DIR=$(pwd)

# Parse the command line
while getopts n:d:mdp: flag
do
    case "${flag}" in
	n) NAME=${OPTARG};;
	d) DIR=${OPTARG};;
  mdp) MDP=${OPTARG};;
    esac
done

# If name.mol2 not in directrory, exit
usage() { echo "Usage: ./simulate_stage2.sh -n NAME -d WORKING_DIR -mdp MDP_DIR"; exit 1;}

# Set up directrories
cd $DIR
stage2_dirs=`ls -d ./stage2*`
stage2_dirs=( $stage2_dirs )
if [ -z ${stage1_dirs[@]}/${NAME}.pdb ]; then
    usage
fi

for conform in "${stage2_dirs[@]}"; do

  cp run_job.sh ${conform}
  cd ${conform}

  # Check if files exist
  files=(${MDP}/minim_steep.mdp ${MDP}/NVT.mdp ${MDP}/NPT.mdp ${MDP}/Production.mdp ${NAME}_initial.gro)
  for file in "${files[@]}"; do
      if [ -z $file ]; then
          usage
      fi
  done

  #JOB INPUT GOES HERE
  # Perform Energy Minimization
  gmx194 grompp -f ${MDP}/minim_steep.mdp -c ${NAME}_initial.gro -p topol.top -o ${NAME}_em.tpr -nobackup
  ./run_job.sh gmx194 mdrun -s ${NAME}_em.tpr -deffnm ${NAME}_em -nt 16 -pin on -nobackup

  # Equilibrate Temp under Canonical Ensemble
  gmx194 grompp -f ${MDP}/NVT.mdp -c ${NAME}_em.gro -r ${NAME}_em.gro -p topol.top -o ${NAME}_nvt.tpr -nobackup
  ./run_job.sh gmx194 mdrun -s ${NAME}_nvt.tpr -deffnm ${NAME}_nvt -nt 16 -pin on -nobackup
  echo "Temperature" | gmx194 energy -f ${NAME}_nvt.edr -o temperature.xvg -nobackup

  # Restrain Backbone
  restraint=3000
  echo "Backbone" | gmx194 genrestr -f ${NAME}_em.gro -fc $restraint $restraint $restraint -nobackup

  # Equilibriate Temp under NPT Ensemble
  gmx194 grompp -f ${MDP}/NPT.mdp -c ${NAME}_nvt.gro -r ${NAME}_nvt.gro -t ${NAME}_nvt.cpt -p topol.top -o ${NAME}_npt.tpr -nobackup
  ./run_job.sh gmx194 mdrun -s ${NAME}_npt.tpr -deffnm ${NAME}_npt -nt 16 -pin on -nobackup
  echo "Pressure" | gmx194 energy -f ${NAME}_npt.edr -o pressure.xvg -nobackup

  python verify_equilibriation.py

  # Production Run
  gmx194 grompp -f ${MDP}/Production.mdp -c ${NAME}_npt.gro -r ${NAME}_npt.gro -t ${NAME}_npt.cpt -p topol.top -o ${NAME}_md.tpr -nobackup
  ./run_job.sh gmx194 mdrun -deffnm ${NAME}_md -nt 16 -pin on -nobackup

  cd $DIR

done

exit 0
