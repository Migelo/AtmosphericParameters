import numpy as np
import matplotlib.pyplot as plt

flux_file = 'fp00k0.pck'
falc = np.loadtxt('/scratch/cernetic/testRun/fioss/k2TEFF5750GRAVITY450000/nessy_lines')
old_kurucz = np.loadtxt('/scratch/cernetic/testRun/fioss/rinatTest/spectra')


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N


with open(flux_file, 'r') as f:
    wavelengths = []
    """Skip header"""
    for i in range(22):
        f.readline()
    """Read wawelengths"""
    for i in range(153):
        wavelengths.append(f.readline().rstrip().split())
    wavelengths = [np.float(item) for sublist in wavelengths for item
                   in sublist]
    wavelengths = np.array(wavelengths) * 10  # nm to A

    """Intensities"""
    """Skip header"""
    for i in range(33156):
        f.readline()
    header = f.readline().rstrip().split()
    for i in 4*[-1]:
        header.pop(i)
    header = ''.join(header).replace('.' ,'') + '.inte'
    print header
    intensity = []
    for i in range(153):
        if i == 152:
            line = f.readline().rstrip()
            for item, j in enumerate([x*10 for x in range(1, 6)]):
                intensity.append(np.float(line[item*10:j]))
        else:
            line = f.readline().rstrip()
            for item, j in enumerate([x*10 for x in range(1, 9)]):
                intensity.append(np.float(line[item*10:j]))

    intensity2 = []
    for i in range(153):
        if i == 152:
            line = f.readline().rstrip()
            for item, j in enumerate([x*10 for x in range(1, 6)]):
                intensity2.append(np.float(line[item*10:j]))
        else:
            line = f.readline().rstrip()
            for item, j in enumerate([x*10 for x in range(1, 9)]):
                intensity2.append(np.float(line[item*10:j]))

    ax = plt.subplot(111)
    """Smooth FALC plot"""
    c = 2.99792458e+10
    corrected_falc = falc[:, -1] * np.pi * c / (falc[:, 0]*1e-8)**2*1e-7*(6.9598e+10/1.495985e+13)**2*1e-3
    ax.plot(falc[:len(running_mean(corrected_falc, 1000)), 0], running_mean(corrected_falc, 1000), label='nessy: FALC')
#    ax.plot(falc[:, 0], ys/np.pi, label='nessy: FALC')
    """Smooth kurucz"""
    corrected_kurucz = old_kurucz[:, -1] * np.pi * c / (old_kurucz[:, 0]*1e-8)**2*1e-7*(6.9598e+10/1.495985e+13)**2*1e-3
    ax.plot(old_kurucz[:len(running_mean(corrected_kurucz, 1000)), 0], running_mean(corrected_kurucz, 1000), label='nessy: kurucz T5750 logG 4.5')
#    ax.plot(old_kurucz[:, 0], ys/np.pi, label='nessy: kurucz T5750 logG 4.5')
    
    ax.set_xlim((2500, 9000))
#    ax.set_ylim((1e-8, 1e-4))
    intensity = np.array(intensity)
    intensity2 = np.array(intensity2)
    wavelengths = np.array(wavelengths)
    corrected_intensity = intensity * np.pi  * c / (wavelengths*1e-8)**2*1e-7*(6.9598e+10/1.495985e+13)**2*1e-3
    corrected_intensity2 = intensity2 * np.pi  * c / (wavelengths*1e-8)**2*1e-7*(6.9598e+10/1.495985e+13)**2*1e-3
    ax.plot(wavelengths, corrected_intensity, label='kurucz website: everything')
    ax.plot(wavelengths, corrected_intensity2, label='kurucz website: continuum only')
    ax.legend(loc='best')
    ax.grid(True, which="both")
    
    plt.show()

