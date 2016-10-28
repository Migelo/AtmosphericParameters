# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:31:44 2016

@author: cernetic
"""

#import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Generate atmospheres for a combination of given temperatures and Nh.')
parser.add_argument('temperatures', type=list, help='List of temperatures')
parser.add_argument('Nh', type=list, help='List of Nh')


table = []
temperatures=[1000,5000,10000]
Nh=[5,12,34]
i = 1
for temp in temperatures:
    for concentration in Nh:
        table.append([len(temperatures)*len(Nh)*100-i*100, temp, 0, concentration])
        i += 1 