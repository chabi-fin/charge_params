#!/bin/bash

NAME=$1

# Perform Energy Minimization
gmxs grompp -f minim_steep.mdp -c initial.gro -p topol.top -o ${NAME}_em.tpr -maxwarn 1 -nobackup
gmxs mdrun -s ${NAME}_em.tpr -deffnm ${NAME}_em -nt 16 -pin on -nobackup

# Equilibrate Temp under Canonical Ensemble
gmxs grompp -f NVT.mdp -c ${NAME}_em.gro -r ${NAME}_em.gro -p topol.top -o ${NAME}_nvt.tpr -maxwarn 1 -nobackup
gmxs mdrun -s ${NAME}_nvt.tpr -deffnm ${NAME}_nvt -nt 16 -pin on -nobackup

# Equilibriate Temp under NPT Ensemble
gmxs grompp -f NPT.mdp -c ${NAME}_nvt.gro -r ${NAME}_nvt.gro -t ${NAME}_nvt.cpt -p topol.top -o ${NAME}_npt.tpr -maxwarn 1 -nobackup
gmxs mdrun -s ${NAME}_npt.tpr -deffnm ${NAME}_npt -nt 16 -pin on -nobackup

# Production Run
gmxs grompp -f Production.mdp -c ${NAME}_npt.gro -r ${NAME}_npt.gro -t ${NAME}_npt.cpt -p topol.top -o ${NAME}_md.tpr -maxwarn 1 -nobackup

exit 0
