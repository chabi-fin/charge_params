# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 16:08:35 2021

@author: Lauren
"""

import numpy as np
import matplotlib.pyplot as plt

# time given in ps, temp in K
temp_data = np.loadtxt("temperature.xvg", comments=["#","@"])
pressure_data = np.loadtxt("pressure.xvg", comments=["#","@"])

# font dictionary for plots
font = {'color': 'black', 'weight': 'semibold', 'size': 18}

# make a figure with two subplots
fig, axes = plt.subplots(1,2, figsize=(12,6), constrained_layout=True)
for condition, ax in zip([temp_data, pressure_data], axes.flat):
    
    # Calculate and format statistics
    average = np.round(np.mean(condition[:,1]), decimals=1)
    std = np.round(np.std(condition[:,1]), decimals=1)
    stats = '\n'.join((
    r'$\mu=%.1f$' % (average, ),
    r'$\sigma=%.1f$' % (std, )))
    
    # Make individual plot
    ax.plot(condition[:,0],condition[:,1])
    ax.set_xlabel("Time (ps)", fontdict=font, labelpad=5)
    ax.tick_params(axis='y', labelsize=14, direction='in', width=2, \
                    length=5, pad=10)
    ax.tick_params(axis='x', labelsize=14, direction='in', width=2, \
                    length=5, pad=10)
    for i in ["top","bottom","left","right"]:
        ax.spines[i].set_linewidth(2)
    ax.grid(True)
    
    # Include stat summary in a text box
    ax.text(0.80, 0.15, stats, color='black', va='top', ha="left", transform=ax.transAxes,
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))
# add y-axis names and save figures
axes[0].set_ylabel("Temperature (K)", fontdict=font, labelpad=5)
axes[1].set_ylabel("Pressure (bar)", fontdict=font, labelpad=5)
plt.savefig("equilibriation.png")