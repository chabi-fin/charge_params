# -*- coding: utf-8 -*-

import os
from sys import argv, exit
from numpy import mean, std

def main(argv):
    """
    Finds the average charges from multiconformational RESP fits.
    
    Parameters
    ----------
    NAME : str
        Name of the compound, used to identify the .pdb file.

    DIRECTORY : str
        Main working directory for the parameterization.

    RESIDUE_ID : str
        3 letter code for the residue under parameterization.
    
    Returns
    -------
    rtp_output.txt : file
        File with the average RESP value from multiple conformations in .rtp format.
    
    """
    # Parse the command line
    if len(argv) != 4:
        print("Usage: python ave_charges.py NAME DIRECTORY RESIDUE_ID")
        exit(1)
    name = argv[1]
    os.chdir(argv[2])
    home = os.getcwd()
    res_id = argv[3]   
    
    # Get directories for stage1 conformations
    dirs = [os.path.join(home, o) for o in os.listdir(home) if os.path.isdir(os.path.join(home,o))
            and "stage1_" in o]  
    
    # Read in a pdb file from one conformation
    os.chdir(dirs[0])
    pdb_lines = read_file("{}.pdb".format(name))
    for line in pdb_lines:
        line = line.split()
        if "ATOM" in line:
            Residue.pdb.append(line)
    
    # Use the .pdb file to define atoms of the residue
    for line in Residue.pdb:
        Residue.atoms[int(line[1])] = Residue(line[1], line[2])
        Residue.atoms[int(line[1])].resid = line[3]
    os.chdir(home)
    
    # Collect all charges from conformations for each atom in a list
    for dir in dirs:
        os.chdir(dir)
        include_charges()
        os.chdir(home)
    
    print("\nSummary of partial atomic charges\n")
    print(*[str(item) for _, item in Residue.atoms.items()], sep="\n")

    print("\nSee the output file 'rtp_output.txt'. Use this to update the '[ atoms ]' field of the (noncanonical) amino acid in the 'aminoacids.rtp' file of the forcefield. Adjust the atomtypes for your forcefield. The default value is the atomic number which must be updated.\nComplete the '[ bonds ]' and '[ impropers ]' fields with help from previous acpype output and other files needed to simulate the dipeptide.")

    # Generate output
    with open("rtp_output.txt", "w") as f:
    	print("[ {} ]\n [ atoms ]".format(res_id), file=f)
    	print(*[Residue.rtp_line(item) for _, item in Residue.atoms.items() if item.resid == res_id], sep="\n", file=f)
    
class Residue():
    """
    The atoms belonging to the residue are stored within the dictionary 
    Residue.atoms, where individual atoms are accessed using their integer 
    values from the .pdb file as the key. 
    
    """
    pdb = []
    atoms = dict()
    
    def __init__(self, num, name):
        self.num = int(num)
        self.name = name
        self.charges = []
        self.element = "unknown"
        self.resid = ""

    def __str__(self):
        return "Number: {}, Name: {}, Element: {}, Configs: {}, Charge: {}00, STD: {}, Residue ID: {}"\
            .format(self.num, self.name, self.element, \
                len(self.charges), round(mean(self.charges), 4),\
                    round(std(self.charges), 4), self.resid)
    
    def rtp_line(self):
        return "{0:>6}    {1:<2}          {2:>8.4f}0    {3}".format(self.name, self.element, mean(self.charges), self.num)        
        
def read_file(file_name):
    """
    Return the lines of a file in a list.
    
    Parameters
    ----------
    file_name : file
        A text file, such as a .pdb or .mol2 file.
    
    Returns
    -------
    result : string list
        An ordered, line-separated list of strings from the file.
    
    """
    try:     
        with open(file_name, mode='r') as file: 
            lines = file.readlines()
    except OSError:
        print("file", file_name, "not found.")
    file_lines = []
    for line in lines:
        file_lines.append(line)
    return file_lines
            
def include_charges():
    """
    Include RESP fit charges for a configuration in Residue.atoms[x].charges
    
    For each atom 'x' in the residue, the RESP fitted charge for the 
    conformation in the current working directory is added to the charges list.
    The second RESP fit should be present in the folder as "resp2.out".
    
    """
    resp_out = read_file("resp2.out")
    
    # find the relevant lines from output for charges
    for i, line in enumerate(resp_out):
        if "Point Charges Before & After Optimization" in line:
            begin = i + 3
        if "Sum over the calculated charges:" in line:
            end = i - 1
    charges = resp_out[begin : end ]
    
    # Append the charges to the matching atom's charge list under: 
    # Residue.atoms[x].charges
    check = False
    for line in charges:
        number = int(line.split()[0])
        charge = float(line.split()[3])
        if -1.5 > charge or charge > 1.5: 
            check = True
        Residue.atoms[number].charges.append(charge) 
        Residue.atoms[number].element = line.split()[1]
    if check:
        print("Check RESP output: ", os.getcwd())

if __name__ ==  '__main__':
    main(argv)
    exit(0)
