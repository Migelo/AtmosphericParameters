import numpy as np

atmosphere_files = ['ap00k2.dat13']

for atmosphere_file in atmosphere_files:
    with open(atmosphere_file, 'r') as f:
        for j in range(463):
            header = f.readline().rstrip().split()
            header.pop(-1)
            header = ''.join(header) + '.atm'
            header = atmosphere_file[4:6] + header
            print header
            for i in range(21):
                f.readline()
            atmosphere = []
            atmosphere.append(f.readline().rstrip())
            number_of_depth_points = int(atmosphere[0].split()[2])
            for k in range(number_of_depth_points):
                atmosphere.append(f.readline().rstrip())
            np.savetxt(header.replace('.', '', 2), atmosphere, fmt='%s')
            for i in range(2):
                f.readline()
