import numpy as np
from scipy import interpolate
import glob
from multiprocessing import Pool
import time
import argparse

parser = argparse.ArgumentParser(description='Interpolate the spectra')
parser.add_argument('subBins', type=str, help='File defining subBins.')
parser.add_argument('cpuNumber', type=int, help='Number of CPUs to be used.')
args = parser.parse_args()

atmosphere = np.loadtxt('/scratch/cernetic/testRun/fioss/temperature_gradients/odf/FAL_VD')  # load atmospheric file
# change the 4th column from Nh to p (Nh*T) which we interpolate
atmosphere[:, 3] = atmosphere[:, 3] * atmosphere[:, 1]
pressure = np.logspace(-4, 8, 25) / (1.38 * 10**-16)

# load some segment to see the available subBins
ending = args.subBins.split('s')[-1]
print(glob.glob(glob.glob('subBins/T*')[0] + '/*.r' + ending)[0])
example = np.loadtxt(glob.glob(glob.glob('subBins/T*')[0] + '/*.r' + ending)[0])
# load data
T_grid, Nh_grid, data = [], [], []
negative_T, negative_Nh, negative_lambda = [], [], []
i = 0
print('Loading files...')
for temp in glob.glob('subBins/T*'):
    for Nh in glob.glob(temp + '/*.r' + ending):
        T_grid.append(float(temp.split('T')[-1]))
        Nh_grid.append(pressure[int(Nh.split('/')[-1].split('.')[-2]) - 1])
        data.append(0)
        data[i] = np.loadtxt(Nh)
        j = 0
        for line in data[i]:
            if line[-1] < 0:
                negative_lambda.append([temp.split('T')[-1], Nh])
                for item in line:
                    negative_lambda[-1].append(float(item))
                data[i][j][-1] = 0
            j += 1
        i += 1
print('Files are loaded.')


def find_surrounding_square(grid, (T_point, Nh_point)):
    # grid's x-axis should be T, y-axis Nh
    T_grid = sorted(list(set(grid[:, 0])))
    Nh_grid = sorted(list(set(grid[:, 1])))
    idx1 = (np.abs(T_grid - T_point)).argmin()
    if T_grid[idx1] - T_point >= 0:
        idx2 = idx1 - 1
    elif T_grid[idx1] - T_point < 0:
        idx2 = idx1 + 1
    idy1 = (np.abs(Nh_grid - Nh_point)).argmin()
    if Nh_grid[idy1] - Nh_point >= 0:
        idy2 = idy1 - 1
    elif Nh_grid[idy1] - Nh_point < 0:
        idy2 = idy1 + 1

    return (T_grid[idx1], Nh_grid[idy1]), (T_grid[idx2], Nh_grid[idy1]), (T_grid[idx1], Nh_grid[idy2]), (T_grid[idx2], Nh_grid[idy2])


def interpolate_square(grid, T_point, Nh_point):
    indexes = []
    points = find_surrounding_square(grid, (np.log10(T_point), np.log10(Nh_point)))
    if points == -1:
        print ''
    for point in points:
        for i, _ in enumerate(grid):
            if grid[i][0] == point[0]:
                j = i
                while grid[j][1] != point[-1]:
                    j += 1
                break
        indexes.append(j)
    interpolation_points = []
    for index in indexes:
        if grid[index][-1] == 0:
            print('0 in interpolating points!', grid[index])
        interpolation_points.append(list(grid[index]))
    function1 = interpolate.interp1d([row[0] for row in interpolation_points[0:2]], [row[-1] for row in interpolation_points[0:2]])
    a = function1(np.log10(T_point))
    function2 = interpolate.interp1d([row[0] for row in interpolation_points[2:4]], [row[-1] for row in interpolation_points[2:4]])
    b = function2(np.log10(T_point))
    function3 = interpolate.interp1d([row[1] for row in interpolation_points[1:3]], [a, b])
    value = np.power(10, function3(np.log10(Nh_point)))
    return value


def interp(point):
    percent = .21
    print("Doing depthpoint: ", point)
    interpolated_ODF = []
    t0 = time.clock()
    for i in range(len(example)):
        # timer
        if (float(i) / len(example) > percent):
            print((((time.clock() - t0) / percent) / 60), (time.clock() - t0) / 60.)
            percent += .2
        # create grid of T/Nh/sub_bin_values
        sub_bin_values = []
        for part in data:  # a part contains sub_bin values for one (T,Nh) combination
            sub_bin_values.append(part[i][-1])
        interpolation_grid = np.c_[np.log10(T_grid), np.log10(Nh_grid), np.log10(sub_bin_values)]
        # interpolate
        T_to_interpolate, Nh_to_interpolate = atmosphere[point - 1][1], atmosphere[point - 1][3]
        my_value = interpolate_square(interpolation_grid, T_to_interpolate, Nh_to_interpolate)
        interpolated_ODF.append(my_value)
    np.savetxt('interpolation/' + str(point) + '.int' + str(args.subBins.split('s')[-1]), np.stack((example[:, 0], example[:, 1], interpolated_ODF), axis=-1), fmt='%.7e')

depth_points = range(1, len(atmosphere) + 1)
p = Pool(args.cpuNumber)
p.map(interp, depth_points)
