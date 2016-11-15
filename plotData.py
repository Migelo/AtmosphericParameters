# -*- coding: utf-8 -*-
import numpy as np
import glob

binToPlot = 2
subBinsToPlot = [0, 8, 11] * (binToPlot+1)
Nh = 17


for subBins in subBinsToPlot:
    plotData = []
    for folder in sorted(glob.glob('subBins/T*')):
        for segment in sorted(glob.glob(folder + '/' + str(Nh) + '.rk')): # returns only 1 file
            print(segment)
            plotData.append([int(segment.split('/')[-2].split('T')[-1]), np.loadtxt(segment)[subBins][2]])
            plotData = sorted(plotData)   
            np.savetxt(str(binToPlot) + 'bin_' + str(subBins+1) + 'sub', plotData) 