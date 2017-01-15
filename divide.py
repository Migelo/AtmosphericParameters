import numpy as np
import args
import os

parser = argparse.ArgumentParser(description='Calculate contrast. (spectra1 - spectra2) / (spectra3 - spectra4)')
parser.add_argument('spectra1', type=str, help='First spectra.')
parser.add_argument('spectra2', type=str, help='Second spectra.')
parser.add_argument('spectra3', type=str, help='Third spectra.')
parser.add_argument('spectra4', type=str, help='Fourth spectra.')

args = parser.parse_args()
#set the necessary parameters for parsing

spectra1 = np.loadtxt(spectra1)
spectra2 = np.loadtxt(spectra2)
spectra3 = np.loadtxt(spectra3)
spectra4 = np.loadtxt(spectra4)

result = (spectra1[:,-1] - spectra2[:,-1])/(spectra3[:,-1] - spectra4[:,-1])

np.savetxt(spectra1.split("/")[-1] + "Contrast",np.c_[spectra1[:,0],result])
