# -*- coding: utf-8 -*-
import numpy as np
import argparse
from multiprocessing import Pool
import sys
import glob

parser = argparse.ArgumentParser(description='Sort the spectra.')
parser.add_argument('bins', type=str, help='File defining the wawelenght bins')
parser.add_argument('subBins', help='File defining the subBins distribution.')
parser.add_argument('cpuNumber', type=int, help='Number of CPUs to be used.')
parser.add_argument('--stromgen', type=bool, default=False, help='Whether to use stromgen segments.')
args = parser.parse_args()

cpuNumber = args.cpuNumber

# format for np.savetxt()
floatFormat = '%.7e'

table = []
depthList = range(1, len(glob.glob('*.segment')) + 1)
if args.stromgen:
    depthList = range(1, len(glob.glob('*.segment_stromgen')) + 1)

depthLength = len(str(len(depthList)))

binData = np.loadtxt(args.bins)

# get minimum and maximum wawelenghts from the first .segment file
minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment')
if args.stromgen:
    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment_stromgen')


def sort_array(array, column, removeHeader):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    array = array[np.argsort(array[:, column])]
    return array


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
    p = Pool(cpuNumber)
    p.map(reducing, depthList)


def reducing(currentFile):
    counter = currentFile
    if args.stromgen:
        currentFile = str(currentFile).zfill(depthLength) + '.segment_stromgen'
    else:
        currentFile = str(currentFile).zfill(depthLength) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile)  # load the current file to memory
    start_at = 0
    global binData
    first_exception = False
    for singleBin in binData:  # for each bin
        if first_exception:
            continue
        if len(binData.shape) == 1:
            singleBin = np.array([binData[0], binData[1]])
            first_exception = True
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
    subBins = np.loadtxt(subBinFile)
    subBinsLength = []
    for line in subBins:
        subBinsLength.append((singleBin[1] - singleBin[0]) * (line[1] - line[0]))
    # Create list of wavelengths which split the bin into subBins
    i = 0
    while i < len(subBinsLength):
        if i == 0:
            subBinsBorders.append([singleBin[0], singleBin[0] + subBinsLength[0]])
        else:
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
    if np.array_equal(singleBin, binData[0]):
        if args.stromgen:
            np.savetxt(str(counter) + '.r' + args.subBins.split('s')[-1] + '_s' , sub_bin_values, fmt=floatFormat)
        else:
            np.savetxt(str(counter) + '.r' + args.subBins.split('s')[-1], sub_bin_values, fmt=floatFormat)
    else:
        if args.stromgen:
            f = open(str(counter) + '.r' + args.subBins.split('s')[-1] + '_s', 'a')
        else:
            f = open(str(counter) + '.r' + args.subBins.split('s')[-1], 'a')
        np.savetxt(f, sub_bin_values, fmt=floatFormat)
        f.close()

bining(depthList)
