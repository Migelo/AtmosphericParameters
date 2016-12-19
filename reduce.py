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
print depthList

#depthLength = len(str(len(np.loadtxt("../../fioss/" + str(args.temperature) + "/FAL_VD"))))
depthLength = len(str(len(depthList)))

binData = np.loadtxt(args.bins)


#np.set_printoptions(precision=17)

def sort_array(array, column, removeHeader):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    array = array[np.argsort(array[:,column])]
    return array
  
def write_array(array, fileName, removeHeader = 0, resetTo = 0):
    """Deletes the header of the array before writing it to the disk.

    Writes the array as fileName while removing removeHeader lines from array and returning resetTo.

    Parameters
    ----------
    array : np.array
        Array to be written.
    fileName : str
        File to write to.
    removeHeader : int
        Number of header lines to delete before writing.
    resetTo : int/float/np.array...
        Returns this object.

    Returns
    -------
    resetTo
        Returns the object specified in arguments, by default it is integer 0.

    """
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    f = open(fileName, "a")
    np.savetxt(f, array, fmt = floatFormat)
    f.close()
    if resetTo != 0:
        array = np.array(resetTo)
    return array

    

#==============================================================================
# 
#==============================================================================

def bining(depthList):
    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment') #get minimum and maximum wawelenghts from the first .segment file
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
    
  
def reducing(currentFile):
    counter = currentFile
    currentFile = str(currentFile).zfill(depthLength) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile) #load the current file to memory
    binData = np.loadtxt(args.bins)
    for singleBin in binData: #for each bin
        tempList = np.array([[0,0,0],[0,0,0]]) #list for storing the data which we then write to the file in the end
        encounteredBinYet = False
        for line in data: #for each line in a segmentFile
            outsideOfTheBin = True
            if (line[0] >= singleBin[0]) and ((line[0] + line[2]) <= singleBin[1]): #check if the wawelength of the current line is within the bin, append it
                tempList = np.vstack([tempList, line])
                outsideOfTheBin = False
                encounteredBinYet = True
                if (np.array_equal(line, data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted
                    sub_bins(args.subBins, singleBin, tempList, counter)
                    #tempList = sort_array(tempList, 1, 2) #sort by opacities
                    f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                    np.savetxt(f, tempList, fmt = floatFormat)
                    f.close()
            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
                sub_bins(args.subBins, singleBin, tempList, counter)                
                #tempList = sort_array(tempList, 1, 2) #sort by opacities
                f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                np.savetxt(f, tempList, fmt = floatFormat)
                f.close()
                break #once we leave the part of the file containing current bin, break and go to the next segment file
    

def sub_bins(subBinFile, singleBin, tempList, counter):
    for i in range(0, 2):
        tempList = np.delete(tempList, (0), axis=0)
#    print 'bin: ', singleBin
    subBinsBorders = []
    subBins = np.loadtxt(subBinFile)
    subBinsLength = np.array([0.])
    for line in subBins: subBinsLength = np.append(subBinsLength, (singleBin[1]-singleBin[0]) * (line[1] - line[0]))
    subBinsLength = np.delete(subBinsLength, (0), axis=0)
    #subBinsLength = np.around(subBinsLength, 7)
    
    """Create list of wavelengths which split the bin into subBins"""
    i=0
    while i < len(subBinsLength):
        if i==0:
            subBinsBorders.append([singleBin[0], singleBin[0] + subBinsLength[0]])
            i += 1
        subBinsBorders.append([subBinsBorders[i-1][-1], subBinsBorders[i-1][-1] + subBinsLength[i]])
        i += 1
    
        
    """Take care of the opacity values at the subBin and bin borders"""
#    print "Sum before corrections: ", np.sum(tempList[:,-1])
    tempListList = tempList.tolist()
    #tempListList.reverse()
#    print "First element: ", tempListList[0]
    if not np.equal(tempListList[0][0], singleBin[0]): 
        tempListList.insert(0, [singleBin[0], tempListList[0][1], tempListList[0][0]-singleBin[0]])
#        print "New first element: ", tempListList[0]
#        print "Sum after fixing the beginning: ", np.sum(np.array(tempListList)[:,-1])
#        print "Last element: ", tempListList[-1]
    tempListList = np.array(tempListList)
    if (singleBin[1] - singleBin[0]) - np.sum(tempListList[:,-1]) < 0:
        sys.exit("This shouldn've happened! Somehow the sum of deltaLambdas exceeded bin size, exiting...")
    else: tempListList[-1][-1] += (singleBin[1] - singleBin[0]) - np.sum(tempListList[:,-1])
#    print tempListList[-1]
#    print "Sum after fixing the beginning and end: ", np.sum(tempListList[:,-1])
#    np.savetxt(str(singleBin[0]), tempListList)
    tempListList = sort_array(tempListList, 1, 0) #sort by opacities
    tempListList = tempListList.tolist()
    deltaLambda = subBinsBorders[0][0]
    i, j, border_indexes, sub_bin_values = 0, 0, [0], []
    while i < len(tempListList)-1:
        if deltaLambda + tempListList[i][2] > subBinsBorders[j][-1] and  j+1 < len(subBinsBorders):
            new_deltaLambda = deltaLambda + tempListList[i][2] - subBinsBorders[j][-1]
            tempListList[i][2] = ((subBinsBorders[j][-1] - deltaLambda))
            tempListList.insert(i+1,[tempListList[i][2]+tempListList[i][0], tempListList[i][1], (new_deltaLambda)])
            border_indexes.append(i+1)
            j += 1
            deltaLambda = subBinsBorders[j][0]
        else:
            deltaLambda += tempListList[i][2]            
        i += 1
    border_indexes.append(len(tempListList)-1)
    deltaLambda, beginning = 0, singleBin[0]
    i = 0
    j = 0
    tempListList=np.array(tempListList)
#    print "Sum after spliting the bordering sub bins: ", np.sum(tempListList[:,-1])
    for i in range(len(border_indexes)-1):
        sub_bin_values.append([beginning, beginning + np.sum(tempListList[border_indexes[i]:border_indexes[i+1],-1]), np.sum(np.multiply(tempListList[border_indexes[i]:border_indexes[i+1],1],tempListList[border_indexes[i]:border_indexes[i+1],2]))])
        beginning = sub_bin_values[-1][1]
        if np.array_equal(singleBin, binData[0]): 
            np.savetxt(str(counter) + '.r' + args.subBins.split('s')[-1], sub_bin_values, fmt = floatFormat)
        else:
            f = open(str(counter) + '.r' + args.subBins.split('s')[-1], 'a')
            np.savetxt(f, sub_bin_values, fmt = floatFormat)
            f.close()


bining(depthList)
