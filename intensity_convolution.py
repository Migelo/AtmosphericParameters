#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

kurucz_intensity = 'ip00k2.pck19'
nessy = np.loadtxt('/scratch/cernetic/testRun/fioss/intensities/spectra')
c = 2.99792458e+10


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def read_line(line):
    i, array = 0, []
    while i<111:
        if i == 0:
            array.append(line[:9])
            i=9
        elif i==9:
            array.append(line[9:19])
            i=19
        else:
            array.append(line[i:i+6])
            i+=6
    return array


def convolve(spectra):
    dx = .005
    sigma = 4.1
    gauss = np.array([1/(np.sqrt(2*sigma**2*np.pi))*np.exp(-(x/sigma)**2/2) for x in np.arange(-3*sigma, 3*sigma, dx)])
    return np.convolve(spectra*dx, gauss, mode='same')

header_list, line_number = [], file_len(kurucz_intensity)
#intensitites = [[] for x in range(485)]
intensities = [[] for i in range(line_number/1224)]
with open(kurucz_intensity, 'r') as f:
    for i in range(line_number/1224):
        header = f.readline().rstrip().split()
        header = "k" + header[8][:1] + header[0] + header[1].replace(".", "") + header[2] + header[3].replace(".", "")
        header_list.append(header)
        f.readline()
        f.readline()
        intensities[i] = np.array([read_line(f.readline().rstrip()) for x in range(1221)]).astype(np.float)


#for i, item in enumerate(intensities):
#    np.savetxt(header_list[i], np.c_[item[:, 0]*10, item[:, 1]])
        
fig, ax = plt.subplots(1)
ax.grid(1)
ax.set_xlim((1000, 9000))
#ax.plot(nessy[:, 0], nessy[:, -1], label='nessy')
#ax.plot(nessy[:, 0], 1e-8*nessy[:, -1]*c/(nessy[:, 0]*1e-8)**2, label='nessy non convolved')
ax.plot(nessy[:, 0], convolve(1e-8*nessy[:, -1]*c/(nessy[:, 0]*1e-8)**2), label='nessy convolved gauss')
ax.plot(intensities[108][:, 0]*10, 1e-8*intensities[108][:, 1]*c/(intensities[108][:, 0]*10*1e-8)**2, label='kurucz')
ax.legend(loc='best')
plt.show()
#plt.savefig('intensity_comparison.pdf')
