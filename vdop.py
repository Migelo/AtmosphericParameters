#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

c = 2.99792458e+10
averaging_points = 500

vdop15 = np.loadtxt('/scratch/cernetic/testRun/fioss/vdop_comparison/vdop1.5')
vdop2 = np.loadtxt('/scratch/cernetic/testRun/fioss/vdop_comparison/vdop2')
vdop3 = np.loadtxt('/scratch/cernetic/testRun/fioss/vdop_comparison/vdop3')
vdop4 = np.loadtxt('/scratch/cernetic/testRun/fioss/vdop_comparison/vdop4')


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N


def convolve(spectra, sigma):
    dx = np.float(.005)
    sigma = np.float(30)
    gauss = [np.exp(-((x)/sigma)**2/2) for x in np.arange(-3*sigma, 3*sigma, dx)]
    return np.convolve(spectra, gauss, mode='same')



# gaussian convolution
fig, ax1 = plt.subplots(1)
ax1.plot(vdop15[:, 0], convolve(vdop15[:, 1], 15), label='1.5 km/s', linewidth=1)
ax1.plot(vdop2[:, 0], convolve(vdop2[:, 1], 15), label='2 km/s', linewidth=1)
ax1.plot(vdop3[:, 0], convolve(vdop3[:, 1], 15), label='3 km/s', linewidth=1)
ax1.plot(vdop4[:, 0], convolve(vdop4[:, 1], 15), label='4 km/s', linewidth=1)
ax1.set_xlim((1000, 9000))
ax1.legend(loc='best')

#ax2.plot(vdop15[:, 0], convolve(vdop15[:, 1], 30), label='1.5 km/s', linewidth=.3)
#ax2.plot(vdop2[:, 0], convolve(vdop2[:, 1], 30), label='2 km/s', linewidth=.3)
#ax2.plot(vdop3[:, 0], convolve(vdop3[:, 1], 30), label='3 km/s', linewidth=.3)
#ax2.plot(vdop4[:, 0], convolve(vdop4[:, 1], 30), label='4 km/s', linewidth=.3)
#ax2.grid(1)
#ax2.set_xlim((1000, 9000))
#ax2.legend(loc='best')

# nomal
#ax3.plot(vdop15[:, 0], vdop15[:, 1], label='1.5 km/s', linewidth=.3)
#ax3.plot(vdop2[:, 0], vdop2[:, 1], label='2 km/s', linewidth=.3)
#ax3.plot(vdop3[:, 0], vdop3[:, 1], label='3 km/s', linewidth=.3)
#ax3.plot(vdop4[:, 0], vdop4[:, 1], label='4 km/s', linewidth=.3)
#ax3.grid(1)
#ax3.set_xlim((1000, 9000))
#ax3.legend(loc='best')
