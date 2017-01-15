# -*- coding: utf-8 -*-
import numpy as np
import glob
import time

binToPlot = [0,1,2]
subBinsToPlotDefault = [0,4,9]
Nh = 16
t0=time.clock()
floatFormat = '%.7e'

for binn in binToPlot:
    subBinsToPlot = []
    for item in subBinsToPlotDefault: subBinsToPlot.append(item + binn*10)
    print subBinsToPlot
    for subBins in subBinsToPlot:
        plotData = []
        for folder in sorted(glob.glob('subBins/T*')):
            for segment in sorted(glob.glob(folder + '/' + str(Nh) + '.r10plot')): # returns only 1 file
                print segment
                a=np.loadtxt(segment)[subBins]
                print a
                plotData.append([int(segment.split('/')[-2].split('T')[-1]), a[2]])
        plotData = sorted(plotData)
        np.savetxt(str(binn+1) + 'bin_' + str(subBins-(binn*10)+1) + 'sub', plotData, fmt=floatFormat) 
print('Finished in ', time.clock()-t0)