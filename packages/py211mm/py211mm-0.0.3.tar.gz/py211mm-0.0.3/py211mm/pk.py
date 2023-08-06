import cosmolopy as cp
import numpy as np

def kfilter(k, R, t="sharp"):
    temp=k*R
    if (t == 'sharp') | (t == 0):
        return 1.0*((1.0-temp) >= 0)
    elif (t == 'top-hat') | (t == 1):
        temp = 3.0*(np.sin(temp)-temp*np.cos(temp))/temp**3
        temp[np.isnan(temp)]=1
        return temp
    elif (t == 'gaussian') | (t == 2):
        return np.exp(-temp**2/2.0)


def pk(data, box_size, k_list_phys, mode=0, usefftw=False):
    '''

    :param data:
    :param box_size:
    :param k_list_phys:
    :param mode:
    :param usefftw:
    :return:
    '''
    N = data.shape[0]
    k_list = k_list_phys*box_size/N
    if usefftw: # Runs, but does not work !!!!!!!!!!!!!
        import pyfftw
        input_size = (N, N, N)
        padded_size = (input_size[0],input_size[1], 2*(input_size[2]//2 + 1))
        full_array = pyfftw.n_byte_align_empty(padded_size, pyfftw.simd_alignment, 
                    'float32')
        real_input = full_array[:, :, :input_size[2]]
        complex_output = full_array.view('complex64')
        fftw_obj = pyfftw.FFTW(real_input, complex_output, axes=(0, 1, 2)) # Plus whatever other args you want
        real_input[:] = data.copy() # with junk
        fftw_obj() # returns complex_output and overwrites the input
    else:
        data=np.fft.rfftn(data)
    kx, ky, kz = np.mgrid[:N, :N, :(N/2+1)]
    kx[kx > N/2-1] = kx[kx > N/2-1]-N
    ky[ky > N/2-1] = ky[ky > N/2-1]-N
    kz[kz > N/2-1] = kz[kz > N/2-1]-N
    k=2.0*np.pi*np.sqrt(kx**2+ky**2+kz**2)/N
    if mode == 1:
        kf = 2.0*np.pi/N
        res = np.zeros(len(k_list)-1)
        for i in range(len(k_list)-1):
            if np.sum((k >= k_list[i]) & (k < k_list[i+1]))>0:
                res[i] = np.mean(np.abs(data[(k >= k_list[i]) & (k < k_list[i+1])])**2)
        return res*box_size**3 / N**6
    if mode==0:
        kf=2.0*np.pi/N
        h1, dump = np.histogram(k.flat,weights=np.abs(data.flat)**2,bins=k_list)
        h2, dump = np.histogram(k.flat,bins=k_list)
        h2[h2==0] = 1.0
        res = h1/h2
        return res*box_size**3/N**6
    if mode==2:
        kf=2.0*np.pi/N
        res=np.zeros(len(k_list))
        for i in range(len(k_list)):
            res[i]=np.mean(np.abs(data[(k>=k_list[i]-kf) & (k<k_list[i]+kf)])**2)
        return res*box_size**3/N**6
    if mode==2:
        return k,data


def pk2d(data,box_size,k_list_r,k_list_theta,ax=0):
    N=data.shape[0]
    data=np.fft.rfftn(data)
    kx,ky,kz=np.mgrid[:N,:N,:(N/2+1)]
    kx[kx>N/2-1]=kx[kx>N/2-1]-N
    ky[ky>N/2-1]=ky[ky>N/2-1]-N
    kz[kz>N/2-1]=kz[kz>N/2-1]-N
    if ax==0:
        k_r=2.0*np.pi*np.abs(kx)/N
        k_theta=2.0*np.pi*np.sqrt(ky**2+kz**2)/N
    elif ax==1:
        k_r=2.0*np.pi*np.abs(ky)/N
        k_theta=2.0*np.pi*np.sqrt(kx**2+kz**2)/N
    elif ax==2:
        k_r=2.0*np.pi*np.abs(kz)/N
        k_theta=2.0*np.pi*np.sqrt(ky**2+kx**2)/N
    else:
        print 'ERROR, wrong ax'
    kf=2.0*np.pi/N
    res=np.zeros([len(k_list_r)-1,len(k_list_theta)-1])
    H, xedges, yedges = np.histogram2d(k_r.flat[:],k_theta.flat[:],bins=[k_list_r,k_list_theta],weights=np.abs(data.flat[:])**2)
    Hn,xedges, yedges = np.histogram2d(k_r.flat[:],k_theta.flat[:],bins=[k_list_r,k_list_theta])
    return H/Hn*box_size**3/N**6
