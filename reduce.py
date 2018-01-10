# -*- coding: utf-8 -*-
import numpy as np
import argparse
from multiprocessing import Pool
import sys
import glob
import copy

parser = argparse.ArgumentParser(description='Sort the spectra.')
parser.add_argument('bins', type=str, help='File defining the wawelenght bins')
parser.add_argument('subBins', help='File defining the subBins distribution.')
parser.add_argument('cpuNumber', type=int, help='Number of CPUs to be used.')
parser.add_argument('--stromgen', type=bool, default=False, help='Whether to use stromgen segments.')
parser.add_argument('--suffix', type=str, help='Suffix of the segment files.')
args = parser.parse_args()
if args.stromgen and not args.suffix:
    parser.error('--suffix can only be used with --stromgen')

table = []
depthList = range(1, len(glob.glob('*.segment')) + 1)
if args.stromgen:
    depthList = range(1, len(glob.glob('*.segment_{}'.format(args.suffix))) + 1)

depthLength = len(str(len(depthList)))

binData = np.loadtxt(args.bins, ndmin=2)

# get minimum and maximum wawelenghts from the first .segment file
if args.stromgen:
    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment_{}'.format(args.suffix))
else:
    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment')

print(depthList)


def bining(depthList):
    wawelenghts = [array[0] for array in minMax]
    minimum = np.min(wawelenghts)
    maximum = np.max(wawelenghts)
    print('Minimum: ' + str(minimum))
    print('Maximum: ' + str(maximum))
    if (np.min(binData) < minimum) or (np.max(binData) > maximum):
        print('Bins intervals exceede the available wawelenghts. '
              'Please check your bins and make sure they are within '
              'the following limits')
        print('Minimum: ' + str(minimum) + '\n')
        print('Maximum: ' + str(maximum) + '\n')
        sys.exit('Check your bins')
        # check if the bins are within range of wawelenghts
    p = Pool(args.cpuNumber)
    p.map(reducing, depthList)


def reducing(currentFile):
    counter = currentFile
    if args.stromgen:
        currentFile = str(currentFile).zfill(depthLength) + '.segment_{}'.format(args.suffix)
    else:
        currentFile = str(currentFile).zfill(depthLength) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile)  # load the current file to memory
    start_at = 0
    global binData
    for singleBin in binData:  # for each bin
        test = True
        tempList = []
        encounteredBinYet = False
        if start_at < 0:
            start_at = 0
        i = int(start_at)
        while i < len(data):  # for each data[i] in a segmentFile
            outsideOfTheBin = True
            if (data[i][0] + data[i][-1] >= singleBin[0]) and (data[i][0] <= singleBin[1]):  # check if the wawelength of the current data[i] is within the bin, append it
                if test:
                    test = False
                if (data[i][0] + data[i][-1] >= singleBin[0]) and (data[i][0] < singleBin[0]):
                    tempList.append(np.array([singleBin[0], data[i][1], data[i + 1][0] - singleBin[0]]))
                else:
                    tempList.append(np.array(data[i]))
                outsideOfTheBin = False
                encounteredBinYet = True
                if (np.array_equal(data[i], data[-1])):
                    # if we are on the last line, we must also sort the array
                    # otherwise it will go unsorted
                    tempList[-1][-1] = singleBin[1] - tempList[-1][0]
                    sub_bins(args.subBins, singleBin, tempList, counter)
            elif (outsideOfTheBin and encounteredBinYet):
                tempList[-1][-1] = np.float(singleBin[1] - tempList[-1][0])
                start_at = int(i) - 3
                sub_bins(args.subBins, singleBin, tempList, counter)
                break  # once we leave the part of the file containing current
                # bin, break and go to the next segment file
            i += 1


def sub_bins(subBinFile, singleBin, tempListList, counter):
    subBinsBorders = []
    subBinsBorders_stromgen = []
    subBins = np.loadtxt(subBinFile)
    subBinsLength = []
    bin_length = np.array(tempListList)[:, 2].sum()
    stretch_factor = 1
    if args.stromgen:
        stretch_factor = (singleBin[1] - singleBin[0]) / bin_length
    for line in subBins:
        subBinsLength.append((bin_length) * (line[1] - line[0]))
    # Create list of wavelengths which split the bin into subBins
    i = 0
    while i < len(subBinsLength):
        if i == 0:
            subBinsBorders_stromgen.append([singleBin[0], singleBin[0] + subBinsLength[0] * stretch_factor])
            subBinsBorders.append([singleBin[0], singleBin[0] + subBinsLength[0]])
        else:
            subBinsBorders_stromgen.append([subBinsBorders_stromgen[i - 1][-1], subBinsBorders_stromgen[i - 1][-1] + subBinsLength[i] * stretch_factor])
            subBinsBorders.append([subBinsBorders[i - 1][-1], subBinsBorders[i - 1][-1] + subBinsLength[i]])
        i += 1

    tempListList.sort(key=lambda x: x[1])  # sort by opacities

    deltaLambda = subBinsBorders[0][0]
    i, j, border_indexes, sub_bin_values = 0, 0, [0], []
    while i < len(tempListList) - 1:
        if deltaLambda + tempListList[i][2] > subBinsBorders[j][-1] and j + 1 < len(subBinsBorders):
            new_deltaLambda = deltaLambda + tempListList[i][2] - subBinsBorders[j][-1]
            tempListList[i][2] = ((subBinsBorders[j][-1] - deltaLambda))
            tempListList.insert(i + 1, [tempListList[i][2] + tempListList[i][0], tempListList[i][1], new_deltaLambda])
            border_indexes.append(i + 1)
            j += 1
            deltaLambda = subBinsBorders[j][0]
        else:
            deltaLambda += tempListList[i][2]
        i += 1
    border_indexes.append(len(tempListList))
    deltaLambda, beginning = 0, singleBin[0]
    i = 0
    j = 0
    tempListList = np.array(tempListList)
    for i in range(len(border_indexes) - 1):
        tempp = np.sum(np.multiply(tempListList[border_indexes[i]:border_indexes[i + 1], 1], tempListList[border_indexes[i]:border_indexes[i + 1], 2])) / subBinsLength[i]
        sub_bin_values.append([beginning, beginning + np.sum(tempListList[border_indexes[i]:border_indexes[i + 1], -1]), np.float(tempp)])
        beginning += np.sum(tempListList[border_indexes[i]:border_indexes[i + 1], -1])
    if args.stromgen:
        for i, item in enumerate(subBinsBorders_stromgen):
            sub_bin_values[i][0] = item[0]
            sub_bin_values[i][1] = item[1]
        if binData.shape[0] > 1:
            if np.array_equal(singleBin, binData[0]):
                sub_bin_values.insert(0, copy.copy(sub_bin_values[0]))
                sub_bin_values[0][0] -= 20
                sub_bin_values[0][1] = sub_bin_values[1][0]
            if np.array_equal(singleBin, binData[-1]):
                sub_bin_values.append(copy.copy(sub_bin_values[-1]))
                sub_bin_values[-1][0] = copy.copy(sub_bin_values[-1][1])
                sub_bin_values[-1][1] = 20 + sub_bin_values[-1][1]
        else:
            sub_bin_values.insert(0, copy.copy(sub_bin_values[0]))
            sub_bin_values[0][0] -= 20
            sub_bin_values[0][1] = sub_bin_values[1][0]
            sub_bin_values.append(copy.copy(sub_bin_values[-1]))
            sub_bin_values[-1][0] = copy.copy(sub_bin_values[-1][1])
            sub_bin_values[-1][1] = 20 + sub_bin_values[-1][1]

    sub_bin_values = np.array(sub_bin_values)
    if np.array_equal(singleBin, binData[0]):
        if args.stromgen:
            np.savetxt('{}.{}'.format(str(counter), args.suffix), sub_bin_values)
        else:
            np.savetxt(str(counter) + '.' + args.bins.split('b')[-1] + '_' + args.subBins.split('s')[-1], sub_bin_values)
    else:
        if args.stromgen:
            f = open('{}.{}'.format(str(counter), args.suffix), 'ab')
        else:
            f = open(str(counter) + '.' + args.bins.split('b')[-1] + '_' + args.subBins.split('s')[-1], 'ab')
        np.savetxt(f, sub_bin_values)
        f.close()

bining(depthList)
