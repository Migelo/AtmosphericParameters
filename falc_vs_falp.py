import numpy as np
import glob
import matplotlib.pyplot as plt
from natsort import natsorted
import copy

custom_bins = True

file_list = natsorted(glob.glob('odf_spectra*Comparison'))
#for item in file_list:
#    int(item.split('Comparison')[0].split('a')[-1])
sub_bins_path = '/home/cernetic/Documents/sorting/lopa-sorting/subBins'


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N


def sort_array(array, column):
    array = array[np.argsort(array[:, column])]
    return array

"""Every element of data consists of one Contrast file"""
raw_data = []
for item in file_list:
    print item
    raw_data.append(np.loadtxt(item))

if custom_bins:

    """Perform merging"""
    lower_bound, step = 1000, 10
    averaging_bins, data = range(lower_bound, 9000 + step, step), []
    for item in raw_data:
        data.append([])
    for j, item in enumerate(raw_data):
        averaged_item = []
        for i in range(len(averaging_bins)-1):
            interval = item[(item[:, 0] >= averaging_bins[i]) & (averaging_bins[i+1] > item[:, 0])][:, -1]
            interval = (np.ones(len(interval)) - interval)**2
            averaged_item.append(np.sum(interval))
        data[j] = np.c_[np.array(averaging_bins[:-1]), np.array(averaged_item)]

    """sub_bins contains all chi2 values of 1 sub bins across all Contrast files"""
    sub_bins = []
    for x in range(len(data[0])):
        sub_bins.append([])
    for i in range(len(data)):
        for j in range(len(data[i])):
            sub_bins[j].append(data[i][j])
    
    """sub_bins contains all values of 1 sub bins across all Contrast files"""
    raw_sub_bins = []
    for x in range(len(raw_data[0])):
        raw_sub_bins.append([])
    for i in range(len(raw_data)):
        for j in range(len(raw_data[i])):
            raw_sub_bins[j].append(raw_data[i][j])
    
    """min_indexes contains the index of the minimum value for each sub bin"""
    min_indexes = []
    for item in sub_bins:
        min_indexes.append([item[np.argmin([x[-1] for x in item])],np.argmin([x[-1] for x in item])])
    
    """Create best combination"""
    best_combination = []
    for i, item in enumerate([x[-1] for x in min_indexes]):
        print i, item
        best_combination.append(sub_bins[i][item])
    # np.savetxt("chi2_results", best_combination, fmt='%s')
    
    
    falc_ratio = []
    for i, item in enumerate(min_indexes):
        falc_ratio.append(raw_sub_bins[i][item[-1]])
    falc_ratio = np.array(falc_ratio)
    falc_indices = list(min_indexes)
    falc_raw_sub_bins = list(raw_sub_bins)
    
    
    ##############################################################
    
    
    file_list = natsorted(glob.glob('odf_fac_spect*Comparison'))
    for item in file_list:
        int(item.split('Comparison')[0].split('a')[-1])
    sub_bins_path = '/home/cernetic/Documents/sorting/lopa-sorting/subBins'
    
    
    """Every element of data consists of one Contrast file"""
    raw_data = []
    for item in file_list:
        print item
        raw_data.append(np.loadtxt(item))
    
    """Perform merging"""
    averaging_bins, data = range(lower_bound, 9000 + step, step), []
    for item in raw_data:
        data.append([])
    for j, item in enumerate(raw_data):
        averaged_item = []
        for i in range(len(averaging_bins)-1):
            interval = item[(item[:, 0] >= averaging_bins[i]) & (averaging_bins[i+1] > item[:, 0])][:, -1]
            interval = (np.ones(len(interval)) - interval)**2
            averaged_item.append(np.sum(interval))
        data[j] = np.c_[np.array(averaging_bins[:-1]), np.array(averaged_item)]
    
    """sub_bins contains all chi2 values of 1 sub bins across all Contrast files"""
    sub_bins = []
    for x in range(len(data[0])):
        sub_bins.append([])
    for i in range(len(data)):
        for j in range(len(data[i])):
            sub_bins[j].append(data[i][j])
    
    """sub_bins contains all values of 1 sub bins across all Contrast files"""
    raw_sub_bins = []
    for x in range(len(raw_data[0])):
        raw_sub_bins.append([])
    for i in range(len(raw_data)):
        for j in range(len(raw_data[i])):
            raw_sub_bins[j].append(raw_data[i][j])
    
    """min_indexes contains the index of the minimum value for each sub bin"""
    min_indexes = []
    for item in sub_bins:
        min_indexes.append([item[np.argmin([x[-1] for x in item])],np.argmin([x[-1] for x in item])])
    
    """Create best combination"""
    best_combination = []
    for i, item in enumerate([x[-1] for x in min_indexes]):
        print i, item
        best_combination.append(sub_bins[i][item])
    
#    falp_ratio = []
#    for i, item in enumerate(min_indexes):
#        falp_ratio.append(raw_sub_bins[i][item[-1]])
#    falp_ratio = np.array(falp_ratio)
#    falp_indices = list(min_indexes)
#    falp_raw_sub_bins = list(raw_sub_bins)
#    
#    falp_ratio_on_falc = []
#    for i, item in enumerate(falp_indices):
#        falp_ratio_on_falc.append(falc_raw_sub_bins[i][item[-1]])
#    falp_ratio_on_falc = np.array(falp_ratio_on_falc)
#    
#    falc_ratio_on_falp = []
#    for i, item in enumerate(falc_indices):
#        falc_ratio_on_falp.append(falp_raw_sub_bins[i][item[-1]])
#    falc_ratio_on_falp = np.array(falc_ratio_on_falp)
    
    fig, (ax1, ax2) = plt.subplots(2)
    ax1.set_xlim((1000, 9000))
    ax1.set_ylim((.5, 1.1))
    ax1.grid(True)
    ax2.set_xlim((1000, 9000))
    ax2.set_ylim((.5, 1.1))
    ax2.grid(True)
    ax1.plot(falc_ratio[:, 0], falc_ratio[:, -1], label='falc_best')
    ax1.plot(falp_ratio_on_falc[:, 0], falp_ratio_on_falc[:, -1], label='falc_on_falp')
    ax1.legend(loc='best')
    
    ax2.plot(falp_ratio[:, 0], falp_ratio[:, -1], label='falp_best')
    ax2.plot(falc_ratio_on_falp[:, 0], falc_ratio_on_falp[:, -1], label='falp_on_falc')
    #ax1.plot(falp_ratio[:, 0], falp_ratio[:, -1], label='falp_best')
    #ax1.plot(falp_ratio_on_falc[:, 0], falp_ratio_on_falc[:, -1], label='falp_on_falc')
    ax2.legend(loc='best')
    
    plt.savefig('best_comparison.pdf')
    plt.show()

else:
    """First for FALC"""
    for i, item in enumerate(raw_data):
        raw_data[i] = item.tolist()

    """Perform merging"""
    for j, item in enumerate(raw_data):
            for i, line in enumerate(item):
                raw_data[j][i].append((1. - float(line[-1]))**2)

    """best_combination contains the best sub bins and their indexes"""
    best_combination = []
    raw_data = np.array(raw_data)
    for i in range(len(raw_data[0])):
        best_combination.append([raw_data[:, i, 0][0], raw_data[:, i, 2][np.argmin(raw_data[:, i, -1])], raw_data[:, i, -1][np.argmin(raw_data[:, i, -1])], np.argmin(raw_data[:, i, -1])])

    """Store FALC results and do the same for FALP"""
    falc_raw_data = copy.copy(raw_data)
    falc_best_combination = copy.copy(best_combination)
    file_list = natsorted(glob.glob('odf_fac_spectra*Comparison'))

    """Every element of data consists of one Contrast file"""
    raw_data = []
    for item in file_list:
        print item
        raw_data.append(np.loadtxt(item))

    for i, item in enumerate(raw_data):
        raw_data[i] = item.tolist()

    """Perform merging"""
    for j, item in enumerate(raw_data):
            for i, line in enumerate(item):
                raw_data[j][i].append((1. - float(line[-1]))**2)

    """best_combination contains the best sub bins and their indexes"""
    best_combination = []
    raw_data = np.array(raw_data)
    for i in range(len(raw_data[0])):
        best_combination.append([raw_data[:, i, 0][0], raw_data[:, i, 2][np.argmin(raw_data[:, i, -1])], raw_data[:, i, -1][np.argmin(raw_data[:, i, -1])], np.argmin(raw_data[:, i, -1])])
    falp_raw_data = copy.copy(raw_data)
    falp_best_combination = copy.copy(best_combination)
    
    """Create best combination of FALC on FALP best indices and vice versa"""
    falp_indices_on_falc, falc_indices_on_falp = [], []
    for i, item in enumerate(falp_best_combination):
        falp_indices_on_falc.append([falc_raw_data[:, i][item[-1]][0], falc_raw_data[:, i][item[-1]][2]])
    falp_indices_on_falc = np.array(falp_indices_on_falc)
    for i, item in enumerate(falc_best_combination):
        falc_indices_on_falp.append([falp_raw_data[:, i][item[-1]][0], falp_raw_data[:, i][item[-1]][2]])
    falc_indices_on_falp = np.array(falc_indices_on_falp)
    
    falc_best_combination, falp_best_combination = np.array(falc_best_combination), np.array(falp_best_combination)
    
    fig, (ax1, ax2) = plt.subplots(2)
    ax1.set_xlim((1000, 9000))
    ax1.set_ylim((.8, 1.1))
    ax1.grid(True)
    ax2.set_xlim((1000, 9000))
    ax2.set_ylim((.8, 1.1))
    ax2.grid(True)
    ax1.plot(falc_best_combination[:, 0], falc_best_combination[:, 1], label='falc_best', linewidth=.2)
    ax1.plot(falp_indices_on_falc[:, 0], falp_indices_on_falc[:, -1], label='falc_on_falp', linewidth=.2)
    ax1.legend(loc='best')
    
    ax2.plot(falp_best_combination[:, 0], falp_best_combination[:, 1], label='falp_best', linewidth=.2)
    ax2.plot(falc_indices_on_falp[:, 0], falc_indices_on_falp[:, -1], label='falc_on_falp', linewidth=.2)
    #ax1.plot(falp_ratio[:, 0], falp_ratio[:, -1], label='falp_best')
    #ax1.plot(falp_ratio_on_falc[:, 0], falp_ratio_on_falc[:, -1], label='falp_on_falc')
    ax2.legend(loc='best')
    
    plt.savefig('best_comparison.pdf')
    plt.show()

