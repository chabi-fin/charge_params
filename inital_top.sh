#!/bin/bash

cp -r /home/finnl92/thesis/ff/amber14sb_sp.ff/ .
cp amber14sb_sp.ff/residuetypes.dat .

gmxs pdb2gmx -ff amber14sb_sp -f PYF2.pdb -o PYF2.gro -water tip3p -nobackup

# Define box with ligand at center, > 1.2 nm to edge
gmxs editconf -f PYF2.gro -o PYF2_box.gro -c -d 1.2 -bt cubic -nobackup

# Solvate Ligand with TIP3P
gmxs solvate -cp PYF2_box.gro -cs spc216 -o PYF2_solv.gro -p topol.top -nobackup

# Add Ions
gmxs grompp -f minim_steep.mdp -c PYF2_solv.gro -p topol.top -o ions.tpr -maxwarn 1 -nobackup
echo "SOL" | gmxs genion -s ions.tpr -o initial.gro -p topol.top -np 2 -pname NA -pq 1 -nobackup
	
