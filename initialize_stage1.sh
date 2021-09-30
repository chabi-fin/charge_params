#!/bin/bash

# parse the command line
NAME=$1
NETCHARGE=$2
DIR=$3
shift 3
CONFORMS=("$@")

cd $DIR

echo "Usage: ./initialize_stage1.sh NAME CHARGE PATH Conform1 Conform2 ..."

for CONFORM in "${CONFORMS[@]}"; do
        
    mkdir -p stage1_${CONFORM}

    cp ${NAME}_${CONFORM}.mol2 stage1_${CONFORM}/${NAME}.mol2
    cd stage1_${CONFORM}

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
