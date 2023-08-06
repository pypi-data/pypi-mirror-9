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

def adjust_barrier(reference, field, r_list, sigma_bins=np.linspace(-5, 5, 100), phasespace):
    '''
    For a given reference field and a phase space (single redshift) it guesses the best barrier to match total fraction
    of crossections.
    :param reference: Binary field, which is used as a reference.
    :param field: Binary field, which is used as a reference.
    :param r_list: Bins along scale space.
    :param sigma_bins: Bins along sigma space.
    :param phasespace: Phasespace.
    :return: retruns barrier
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