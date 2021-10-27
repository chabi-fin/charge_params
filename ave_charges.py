# -*- coding: utf-8 -*-

import os
from sys import argv, exit
from numpy import mean, std
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec

def main(argv):
    """
    Find the average charges from multiconformational RESP fits.

    Gives the "[ atoms ]" field of the rtp file for the structure, with the
    updated charges in "rtp_output.txt". For stage 2, a plot can be made to
    visualize the charge distribution and compare with the canonical analogue.

    Parameters
    ----------
    NAME : str
        Name of the compound, used to identify the .pdb file.

    DIRECTORY : str
        Main working directory for the parameterization.

    RESIDUE_ID : str
        3 letter code for the residue under parameterization.

    STAGE : int
        1 for stage1 and 2 for stage2

    Returns
    -------
    rtp_output.txt : file
        File with the average RESP value from multiple conformations in .rtp format.

    """
    # Parse the command line
    if len(argv) != 5:
        print("Usage: python ave_charges.py NAME DIRECTORY RESIDUE_ID STAGE")
        exit(1)
    name = argv[1]
    os.chdir(argv[2])
    home = os.getcwd()
    res_id = argv[3]
    stage = int(argv[4])

    # Get directories for stage1 conformations
    dirs = [os.path.join(home, o) for o in os.listdir(home) \
            if os.path.isdir(os.path.join(home,o)) and \
            "stage{}_".format(stage) in o]

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
        if len(line[3]) > 4:
            line[3] = line[3][:4]
        Residue.atoms[int(line[1])].resid = line[3]

    os.chdir(home)

    # Collect all charges for all configurations of all conformations
    if stage == 1:
        folders = dirs
    else:
        folders = []
        for dir in dirs:
            os.chdir(dir)
            sub_folders = ["{0}/{1}".format(dir, f) for f in os.listdir() \
                            if "config" in f]
            folders.extend(sub_folders)
    for folder in folders:
        os.chdir(folder)
        include_charges()
        os.chdir(home)

    print("\nSummary of partial atomic charges\n")
    print(*[str(item) for _, item in Residue.atoms.items()], sep="\n")

    print("\nSee the output file 'rtp_output.txt'. Use this to update the '[ atoms ]' field of the (noncanonical) amino acid in the 'aminoacids.rtp' file of the forcefield. Adjust the atomtypes for your forcefield. The default value is the atomic number which must be updated.\nComplete the '[ bonds ]' and '[ impropers ]' fields with help from previous acpype output and other files needed to simulate the dipeptide.")

    # Generate output
    with open("rtp_output.txt", "w") as f:
    	print("[ {} ]\n [ atoms ]".format(res_id), file=f)
    	print(*[Residue.rtp_line(item) for _, item in Residue.atoms.items() if item.resid == res_id], sep="\n", file=f)

    if stage == 2:
        # Include matching canonical charges
        con_res = "NTYR"
        canonical_charges(con_res)

        # Make a plot if stage 2
        make_plot(name, res_id, con_res)

    return None

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
        self.canonical = None

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

def canonical_charges(residue_code, ff="/home/finnl92/thesis/ff/amber14sb.ff"):
    """
    Include the canonical charge for atoms form the corresponding residue.

    Some of the atoms in the mimetic correspond to an atom on the canonical
    amino acid. For those atoms, include its canonical charge under the
    canonical attribute to the Residue class object.

    Parameters
    ----------
    residue_code : str
        3 or 4 letter residue_code for the canonical amino acid.

    Returns
    -------
    result : string list
        An ordered, line-separated list of strings from the file.

    """

    # Get the charge data for canonical Tyrosine
    rtp_file = "{}/aminoacids.rtp".format(ff)
    amino_acids = read_file(rtp_file)
    start = None
    for i, line in enumerate(amino_acids):
        if "[ {} ]".format(residue_code) in line:
            start = i + 2
        if start != None and "bonds" in line:
            end = i
            break
    residue = amino_acids[start:end]

    # Update the canonical attribute for matching atoms
    for line in residue:
        res_name, _, res_charge, res_num = line.split()
        for i, atom in Residue.atoms.items():
            if atom.name == res_name:
                atom.canonical = res_charge
                break

def make_plot(name, res_id, analogue_res):
    """
    Make a plot of charges, including std error bar and picture of structure.

    Make a plot of the charges and save to file. An image of the structure and
    the canonical analogue should be in the working directory as ">>name<<.png"
    and ">>analogue_res<<.png". The plot includes the two images to help readers
    understand the topology of the atom names.

    Parameters
    ----------
    name : str
        Name of the structure. e.g. "FY1", "PF7" etc.

    res_id : str
        3 or 4 letter residue code

    con_res : str
        3 or 4 letter code for the cononical analogue

    """
    font = {'color': 'black', 'weight': 'semibold', 'size': 20}

    # Data related to parameterized molecule
    atoms = [atom for _, atom in Residue.atoms.items() if atom.resid == res_id]
    names = [atom.name for atom in atoms]
    charges = [round(mean(atom.charges), 4) for atom in atoms]
    stdevs = [round(std(atom.charges), 4) for atom in atoms]

    # Data related to the canonical molecule
    analogue_names = [atom.name for atom in atoms if atom.canonical != None]
    analogue_charges = [float(atom.canonical) for atom in atoms \
                    if atom.canonical != None]

    # Images for plot
    png = name + ".png"
    im = mpimg.imread(png)
    analogue_png = analogue_res + ".png"
    analogue_im = mpimg.imread(analogue_png)

    # Add figure and subplots
    fig = plt.figure(constrained_layout=True, figsize=(15,10))
    gs = GridSpec(3, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1:, :])

    #ax2 = plt.axes()
    ax3.scatter(names, charges, label=name, marker='o', linewidth=3, \
                color="royalblue")
    ax3.scatter(analogue_names, analogue_charges, label=analogue_res, \
                marker='*', linewidth=3, color="firebrick")
    plt.errorbar(names, charges, yerr=stdevs, fmt="none")
    ax3.tick_params(axis='y', labelsize=16, direction='in', width=2, \
                    length=5)
    ax3.tick_params(axis='x', labelsize=16, direction='in', width=2, \
                    rotation=45, length=5)
    plt.xlabel("Atom Names", fontdict=font, labelpad=10)
    plt.ylabel("Atomic Partial Charge (e)", fontdict=font, labelpad=10)
    plt.legend(loc=2, fontsize=16)
    ax1.imshow(im)
    ax2.imshow(analogue_im)
    ax1.text(0,0,name, verticalalignment="bottom", fontdict=font, \
                color="royalblue")
    ax2.text(0,0,analogue_res, verticalalignment="bottom", fontdict=font, \
        color="firebrick")
    for ax in [ax1, ax2]:
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
    ax3.grid()
    for i in ["top","bottom","left","right"]:
        ax3.spines[i].set_linewidth(2)

    # Save to file
    plt.savefig(name + "_charges.png")
    plt.show()

    return None

if __name__ ==  '__main__':
    main(argv)
    exit(0)
