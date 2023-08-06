__author__ = 'kaurov'
from numpy.fft import fftn, ifftn
import numpy as np
import scipy.stats


def a2z(a):
    '''
    Convert scale factor, a, to redshift, z.
    :param a: Scale factor.
    :return: Redshift.
    '''
    return 1.0/a-1.0

def binned_percentile(x, weights, p):
    '''
    Help function
    :param x:
    :param weights:
    :param p:
    :return:
    '''
    temp=np.cumsum(weights)/np.sum(weights)
    return np.interp(p, temp, x)

def perc2sigma(x):
    '''
    Converts percentiles to sigmas.
    :param x: Values in percentiles.
    :return: Values in sigmas.
    '''
    tempx = np.append(np.logspace(-10, 0, 300)*0.49, 1.0-0.49*np.logspace(-10, 0, 300)[::-1])
    tempy = scipy.stats.norm.ppf(tempx)
    return np.interp(x, tempx, tempy)


def any2perc(x):
    '''
    Converts any distribution to percentiles.
    :param x: Values with any distribution.
    :return: Values in percentiles.
    '''
    x[x.argsort()] = np.arange(len(x))
    return x/len(x)+0.5/len(x)


def any2sigma(x):
    '''
    Converts any distribution to sigmas.
    :param x: Values with any distribution.
    :return: Values in sigmas.
    '''
    return perc2sigma(any2perc(x))


def f_filter(N, r_space, rmax, rmin=0):
    '''
    Generates spherical filter in Fourier space. This method avoids ringing.
    :param N: Box dimension.
    :param r_space: Distances in real space.
    :param rmax: Outer shell of the filter.
    :param rmin: Inner shell of the filter.
    :return: Spherical filter in Fourier space.
    '''
    fshape = np.zeros([N, N, N/2+1])
    fshape[(r_space[:, :, :] >= rmin) & (r_space[:, :, :] < rmax)] = 1.0
    fshape = fshape/np.sum(fshape)
    f_fshape = np.fft.fftn(fshape)
    return f_fshape


def train_model(field, bins, r_list, reference, sigma_bins=np.linspace(-5, 5, 100)):
    '''
    Generates trajectory from 'reference' and matches it to 'field'.
    :param field: Field we are interested in.
    :param bins: Bins boundaries of values in 'field'.
    :param reference: Field, which is used as a reference.
    :param sigma_bins: Bins along sigma space.
    :return: Returns map...
    '''
    # The array for storing resulting map.
    res = np.zeros([len(r_list), len(bins)-1, len(sigma_bins)-1])

    # Reshaping 'field' for later use.
    field = field.reshape([-1])

    # The size of the box.
    N = reference.shape[0]

    # Generating array with distances in real space.
    rx, ry, rz = np.mgrid[:N, :N, :(N/2+1)]
    rx[rx > N/2] = rx[rx > N/2] - N
    ry[ry > N/2] = ry[ry > N/2] - N
    rz[rz > N/2] = rz[rz > N/2] - N
    r_space = np.sqrt(rx**2 + ry**2 + rz**2)

    # Removing all extra arrays to free memory.
    del rx
    del ry
    del rz

    # FFT of the reference field.
    data_fft = np.fft.rfftn(reference)

    # Now iterating through all scales of interest.
    for i in range(len(r_list)):
        print 1.0*i/len(r_list)
        # Creating smoothed array.
        if i>0:
            rmin = r_list[i-1]
        else:
            rmin = 0
        temp = np.fft.irfftn(data_fft*f_filter(N, r_space, r_list[i], rmin=rmin))
        # Transforming it into N(0,1) distributed array.
        temp = any2sigma(temp.reshape([-1]))
        res[i, :, :] = np.histogram2d(field, temp, bins=(bins, sigma_bins))[0]
    # Normilize res
    for i in range(res.shape[1]):
        for j in range(res.shape[0]):
            if np.sum(res[j, i, :]) > 0:
                res[j, i, :] /= np.sum(res[j, i, :])
    print 'Done'
    return res


def apply_model(map, bins, sigma_bins, r_list, reference):
    '''
    The function applies a given model (map) to a reference field.
    :param aim:
    :param reference:
    :return:
    '''
    # The array for storing resulting map.
    # res = np.zeros([len(r_list), len(bins)-1, len(sigma_bins)-1])
    # The size of the box.
    N = reference.shape[0]
    # Generating array with distances in real space.
    rx, ry, rz = np.mgrid[:N, :N, :(N/2+1)]
    rx[rx > N/2] = rx[rx > N/2] - N
    ry[ry > N/2] = ry[ry > N/2] - N
    rz[rz > N/2] = rz[rz > N/2] - N
    r_space = np.sqrt(rx**2 + ry**2 + rz**2)
    # Removing all extra arrays to free memory.
    del rx
    del ry
    del rz
    # FFT of the reference field.
    data_fft = np.fft.rfftn(reference)
    # Defining likelyhood array
    likelyhood = np.zeros([N, N, N, len(bins)-1])
    # Now iterating through all scales of interest.
    for i in range(len(r_list)):
        print 1.0*i/len(r_list)
        # Creating smoothed array.
        if i > 0:
            rmin = r_list[i-1]
        else:
            rmin = 0
        temp = np.fft.irfftn(data_fft*f_filter(N, r_space, r_list[i], rmin=rmin))
        # Transforming it into N(0,1) distributed array.
        temp2 = temp.copy()
        for j in range(len(sigma_bins)-1):
            for k in range(len(bins)-1):
                likelyhood[(temp >= sigma_bins[j]) & (temp < sigma_bins[j+1]), k] += map[i, k, j]
    print 'Done'
    # res = np.zeros([N, N, N], dtype=np.int8)
    res = np.argmax(likelyhood, axis=3)
    return res, likelyhood

def adjust_barrier(reference, phasespace, r_list, sigma_bins_centers, Q_aim):
    '''
    Adjust barrier according to phasespace for the best match in total neutral volume.
    :param reference: Reference field.
    :param phasespace: Phase space used to extract a barrier.
    :param r_list: List of scales.
    :param sigma_bins_centers: List of sigmas.
    :param Q_aim: Ionization fraction to fit into.
    :return:
    '''
    # Creating an array of test barriers,
    barriers = np.zeros([phasespace.shape[0], 64])
    # and test thresholds.
    tresh = np.linspace(0.3, 0.98, 64)
    for i in range(barriers.shape[0]):
        for j in range(barriers.shape[1]):
            if i == (barriers.shape[0]-1):
                barriers[i, j] = np.interp(tresh[j], phasespace[i, 51:], sigma_bins_centers[51:])
            else:
                barriers[i, j] = np.interp(tresh[j], phasespace[i, 30:], sigma_bins_centers[30:])
    res = apply_barrier(reference, r_list, barriers, shells=False, rescale=1.0)
    # Determine ionization fraction for those thresholds.
    ion_fractions = 1.0*res.sum(0).sum(0).sum(0)/128**3
    # Find the best threshold.
    tresh_best = np.interp(Q_aim, ion_fractions[::-1], tresh[::-1])
    print ion_fractions
    print tresh_best
    # Determine the best barrier.
    barrier_best = np.zeros([phasespace.shape[0]])
    for i in range(len(barriers)):
        barrier_best[i] = np.interp(tresh_best, phasespace[i, 30:], sigma_bins_centers[30:])
    return barrier_best


def apply_barrier(reference, r_list, barriers, shells=False, rescale=1.0):
    '''
    Applies a list of barriers on a given reference field.
    :param reference: Reference field.
    :param r_list: List of scales.
    :param barriers: 2d numpy array og barriers.
    :param rescale: rescaling factor.
    :return:
    '''
    # The size of the box.
    N = reference.shape[0]
    # The size of the box.
    N_b = barriers.shape[1]
    # The array for storing resulting map.
    res = np.zeros([N, N, N, N_b], dtype=np.bool)
    # Generating array with distances in real space.
    rx, ry, rz = np.mgrid[:N, :N, :(N/2+1)]
    rx[rx > N/2] = rx[rx > N/2] - N
    ry[ry > N/2] = ry[ry > N/2] - N
    rz[rz > N/2] = rz[rz > N/2] - N
    r_space = np.sqrt(rx**2 + ry**2 + rz**2)
    # Removing all extra arrays to free memory.
    del rx
    del ry
    del rz
    # FFT of the reference field.
    data_fft = np.fft.rfftn(reference)
    # Now iterating through all scales of interest.
    for i in range(len(r_list)):
        print 1.0*i/len(r_list)
        # Creating smoothed array.
        if shells:
            if i > 0:
                rmin = r_list[i-1] * rescale
            else:
                rmin = 0
        else:
            rmin = -1
        temp = np.fft.irfftn(data_fft*f_filter(N, r_space, r_list[i] * rescale, rmin=rmin))
        # Transforming it into N(0,1) distributed array.
        temp = any2sigma(temp.reshape([-1])).reshape([N, N, N])
        for j in range(N_b):
            res[temp > barriers[i, j], j] = True
    print 'Done'
    return res
