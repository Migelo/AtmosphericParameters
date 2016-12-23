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


args = parser.parse_args()
#set the necessary parameters for parsing

#file_list = []
#file_list = sorted(glob.glob(str(args.folder)+'/*.lopa'), reverse=True)
#numberOfItems = len(file_list)
#create a list off all the .lopa files

cpuNumber = args.cpuNumber
#number of cores to use

floatFormat = '%.7e'
#format for np.savetxt()

table = []
#temperatures=[1000,5000,10000]
#Nh=[5,12,34]
#temperatures = args.temperatures
#Nh = args.Nh

#i = 1
#for temp in temperatures:
#    for concentration in Nh:
#        table.append([len(temperatures)*len(Nh)*100-i*100, temp, 0, concentration])
#        i += 1 

#firstFile = np.loadtxt(file_list[0])
#depth=0
#for array in firstFile:
#    if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) and (int(array[1]) > 0): #check whether we are in the header line
#        depth += 1
#print("Number of depthpoints: " + str(depth))

#depthList = range(1, len(np.loadtxt("../../fioss/" + str(args.temperature) + "/FAL_VD"))+1)
depthList = range(1, len(glob.glob('*.segment'))+1)
#print depthList

#depthLength = len(str(len(np.loadtxt("../../fioss/" + str(args.temperature) + "/FAL_VD"))))
depthLength = len(str(len(depthList)))

binData = np.loadtxt(args.bins)

minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment') #get minimum and maximum wawelenghts from the first .segment file

error = 0

def sort_array(array, column, removeHeader):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    array = array[np.argsort(array[:,column])]
    return array


#==============================================================================
# 
#==============================================================================

def bining(depthList):
#    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment') #get minimum and maximum wawelenghts from the first .segment file
    wawelenghts = [array[0] for array in minMax]
    minimum = np.min(wawelenghts)
    maximum = np.max(wawelenghts)
    print('Minimum: ' + str(minimum))
    print('Maximum: ' + str(maximum))
    if (np.min(binData) < minimum) or (np.max(binData) > maximum):
        print('Bins intervals exceede the available wawelenghts. Please check your bins and make sure they are within the following limits')
        print('Minimum: ' + str(minimum) + '\n')
        print('Maximum: ' + str(maximum) + '\n')
        sys.exit('Check your bins')
        #check if the bins are within range of wawelenghts
    
    p = Pool(cpuNumber)    
    p.map(reducing, depthList)
#    for item in depthList: reducing(item)
#    reducing(1)
    
  
def reducing(currentFile):
    counter = currentFile
    currentFile = str(currentFile).zfill(depthLength) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile) #load the current file to memory
    start_at = 0
    global binData
    for singleBin in binData: #for each bin
        test=True
#        print('bin',singleBin)
        tempList = []
        encounteredBinYet = False
        if start_at < 0: start_at = 0
        i = int(start_at)
        while i < len(data): #for each data[i] in a segmentFile
            outsideOfTheBin = True
            if (data[i][0] + data[i][-1] >= singleBin[0]) and (data[i][0] <= singleBin[1]): #check if the wawelength of the current data[i] is within the bin, append it
                if test:
                    test=False
#                    print '1st print: ',data[i-1],i-1
#                    print '2st print: ',data[i], i
                if (data[i][0] + data[i][-1] >= singleBin[0]) and (data[i][0] < singleBin[0]):
#                    print "first bin item: ", data[i], i
#                    print data[i]
#                    data[i][-1] = data[i][0] + data[i][-1] - singleBin[0]
#                    data[i][0] = singleBin[0]
                    tempList.append(np.array([singleBin[0], data[i][1], data[i+1][0] - singleBin[0]]))
#                    print np.array([singleBin[0], data[i][1], data[i+1][0] - singleBin[0]])
                else: tempList.append(np.array(data[i]))
                outsideOfTheBin = False
                encounteredBinYet = True
                if (np.array_equal(data[i], data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted
                    tempList[-1][-1] = singleBin[1] - tempList[-1][0]
#                    print 'first: ',tempList[0],' last: ',tempList[0][0]
#                    print 'last element: ',tempList[-1]
                    sub_bins(args.subBins, singleBin, tempList, counter)
                    #tempList = sort_array(tempList, 1, 2) #sort by opacities
                #    f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                 #   np.savetxt(f, tempList, fmt = floatFormat)
                  #  f.close()
            elif (outsideOfTheBin and encounteredBinYet):
                tempList[-1][-1] = np.float(singleBin[1] - tempList[-1][0])
                start_at = int(i)-3
#                print data[i-1],i-1
#                print data[i],i
#                print data[i+1],i+1
#                print 'last element: ',tempList[-1]
#                print 'first: ',tempList[0], ' last: ',tempList[-1],'sum ',tempList[-1][0]+tempList[-1][-1],singleBin[-1]
                sub_bins(args.subBins, singleBin, tempList, counter)                
                #tempList = sort_array(tempList, 1, 2) #sort by opacities
                #f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                #np.savetxt(f, tempList, fmt = floatFormat)
                #f.close()
                break #once we leave the part of the file containing current bin, break and go to the next segment file
            i += 1
    

def sub_bins(subBinFile, singleBin, tempListList, counter):
#    print('0th ',tempListList[0],tempListList[0][0]+tempListList[0][-1],tempListList[1][0]) 
#    print('last: ',tempListList[-1], tempListList[-1][0]+tempListList[-1][-1])
#    print
#    global error
    subBinsBorders = []
    subBins = np.loadtxt(subBinFile)
    subBinsLength = []
    for line in subBins: subBinsLength.append((singleBin[1]-singleBin[0]) * (line[1] - line[0]))    
#    sys.exit()
#    if (singleBin[1] - singleBin[0]) - np.sum([line[-1] for line in tempListList]) < 0:
#        sys.exit("This shouldn've happened! Somehow the sum of deltaLambdas exceeded bin size, exiting...")
#    print 'integral before corrections: ', sum(np.array(tempListList)[:,1]*np.array(tempListList)[:,-1])

    """Create list of wavelengths which split the bin into subBins"""
    i=0
    while i < len(subBinsLength):
        if i==0:
            subBinsBorders.append([singleBin[0], singleBin[0] + subBinsLength[0]])
        else:
            subBinsBorders.append([subBinsBorders[i-1][-1], subBinsBorders[i-1][-1] + subBinsLength[i]])
        i += 1
#    print 'segment ', counter
#    print subBinsBorders
    
    tempListList.sort(key=lambda x: x[1]) #sort by opacities

    deltaLambda = subBinsBorders[0][0]
    i, j, border_indexes, sub_bin_values = 0, 0, [0], []
    while i < len(tempListList)-1:
        if deltaLambda + tempListList[i][2] > subBinsBorders[j][-1] and  j+1 < len(subBinsBorders):
            new_deltaLambda = deltaLambda + tempListList[i][2] - subBinsBorders[j][-1]
            tempListList[i][2] = ((subBinsBorders[j][-1] - deltaLambda))
            tempListList.insert(i+1,[tempListList[i][2]+tempListList[i][0], tempListList[i][1], new_deltaLambda])
            border_indexes.append(i+1)
            j += 1
            deltaLambda = subBinsBorders[j][0]
        else:
            deltaLambda += tempListList[i][2]            
        i += 1
    border_indexes.append(len(tempListList))
    deltaLambda, beginning = 0, singleBin[0]
    i = 0
    j = 0
    abc=list(tempListList)
    abc.sort(key=lambda x: x[0])
#    print border_indexes
#    print len(tempListList)
#    np.savetxt(str(singleBin[0]) + 'segment' + str(counter), tempListList)
    tempListList = np.array(tempListList)
#    print 'whole: ',np.sum(np.multiply(tempListList[:,1],tempListList[:,2]))
#    f = open(str(counter) + '.segmentt', 'a')
#    for i in range(len(border_indexes)-1):
#        np.savetxt(f, )
#    print 'integral after corrections: ', np.sum(tempListList[:,-1]*tempListList[:,1])
    for i in range(len(border_indexes)-1):
        tempp = np.sum(np.multiply(tempListList[border_indexes[i]:border_indexes[i+1],1],tempListList[border_indexes[i]:border_indexes[i+1],2]))/subBinsLength[i]
#        temp += np.sum(np.multiply(tempListList[border_indexes[i]:border_indexes[i+1],1],tempListList[border_indexes[i]:border_indexes[i+1],2]))
#        print 'start, end ',beginning,beginning + np.sum(tempListList[border_indexes[i]:border_indexes[i+1],-1])
#        sub_bin_values.append([beginning,beginning + np.sum(tempListList[border_indexes[i]:border_indexes[i+1],-1]), np.sum(tempListList[border_indexes[i]:border_indexes[i+1],1]*tempListList[border_indexes[i]:border_indexes[i+1],2])])
        sub_bin_values.append([beginning,beginning + np.sum(tempListList[border_indexes[i]:border_indexes[i+1],-1]),np.float(tempp)])
        beginning += np.sum(tempListList[border_indexes[i]:border_indexes[i+1],-1])
#        print 'comparison: ',tempp/tempp, np.sum(tempListList[border_indexes[i]:border_indexes[i+1],1]*tempListList[border_indexes[i]:border_indexes[i+1],2])/tempp, sub_bin_values[-1][-1]/tempp
        
#    print (np.sum([item[-1] for item in sub_bin_values])-np.sum(np.multiply(tempListList[:,1],tempListList[:,2])))/np.sum(np.multiply(tempListList[:,1],tempListList[:,2]))
    abc=np.array(sub_bin_values)
#    print abc
#    print 'integral of sub_bins: ', np.sum(abc[:,-1]*(abc[:,1]-abc[:,0])), temp
#    print 'delta lambda sum: ', sum(tempListList[:,-1])
#    sys.exit()
    if np.array_equal(singleBin, binData[0]): 
        np.savetxt(str(counter) + '.r' + args.subBins.split('s')[-1], sub_bin_values, fmt = floatFormat)
    else:
        f = open(str(counter) + '.r' + args.subBins.split('s')[-1], 'a')
#         np.savetxt(f, [0,0,0], fmt = floatFormat)
        np.savetxt(f, sub_bin_values, fmt = floatFormat)
        f.close()

bining(depthList)
#print error