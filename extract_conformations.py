import numpy as np
import mdtraj as md
import os
from sys import argv

home = os.getcwd()

MOL = md.load_xtc("{}_md.xtc".format(argv[1]), \
        top="{}_md.gro".format(argv[1])).remove_solvent()

# each frame is 100 ps
configs = [c for c, t in zip(MOL, MOL.time) if t % 1000 == 0]

for i, c in enumerate(configs):
    name = "config_" + str(i)
    if not os.path.isdir(name):
        os.mkdir(name)
    file = name + "/geo.pdb"
    c.save_pdb(file)

os.chdir(home)
