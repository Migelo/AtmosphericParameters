# -*- coding: utf-8 -*-
import numpy as np
import glob
import time

binToPlot = [0,1,2,299,599]
subBinsToPlotDefault = [0,8,11]
Nh = 8
t0=time.clock()
floatFormat = '%.7e'

for binn in binToPlot:
    subBinsToPlot = []
    for item in subBinsToPlotDefault: subBinsToPlot.append(item + binn*12)
    print subBinsToPlot
    for subBins in subBinsToPlot:
        plotData = []
        for folder in sorted(glob.glob('subBins/T*')):
            for segment in sorted(glob.glob(folder + '/' + str(Nh) + '.rk')): # returns only 1 file
                print segment
                a=np.loadtxt(segment)[subBins]
                print a
                plotData.append([int(segment.split('/')[-2].split('T')[-1]), a[2]])
        plotData = sorted(plotData)
        np.savetxt(str(binn+1) + 'bin_' + str(subBins-(binn*12)) + 'sub', plotData, fmt=floatFormat) 
print('Finished in ', time.clock()-t0)