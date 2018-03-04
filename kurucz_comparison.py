#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:29:17 2017

@author: cernetic
"""

import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from natsort import natsorted

c = 2.99792458e+10
folders = natsorted(glob('/scratch/cernetic/testRun/fioss/k2*'))
intensity_path = '/scratch/cernetic/testRun/intensity/'

for folder in folders:
    print folder
    nessy_lines = np.loadtxt(folder + '/nessy_lines')
    nessy_continuum_only = np.loadtxt(folder + '/nessy_continuum_only')
    kurucz = np.loadtxt(intensity_path + folder.split('/')[-1])
    
    f, ax = plt.subplots(1)
    ax.grid(1)
    ax.set_xlim((1000, 9000))
    ax.set_ylim( (0, 2*np.mean(kurucz[:, 1])))
    ax.plot(nessy_lines[:, 0], nessy_lines[:, 1], label='nessy_lines')
    ax.plot(nessy_continuum_only[:, 0], nessy_continuum_only[:, 1], label='nessy_continuum_only')
    ax.plot(kurucz[:, 0], kurucz[:, 1], label='kurucz')
    ax.legend(loc='best')
    plt.show()
