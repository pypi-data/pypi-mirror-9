'''
Basic tools for generating initial conditions.
'''

import cosmolopy as cp
import numpy as np

def get_IC(N=128, box_size=20, seed=0, h100=0.6814, cosmo={'tau': 0.087, 'omega_n_0': 0.0, 'sigma_8': 0.8285, 'h': 0.6814, 'N_nu': 0, 'omega_lambda_0': 0.6964, 'n': 0.96745, 'Y_He': 0.24, 'z_reion': 10.4, 'omega_b_0': 0.0456, 'omega_k_0': 0.0, 't_0': 13.75, 'omega_M_0': 0.2557}):
    '''
    Returns 3d array with IC.
    :param N: Box resolution (NxNxN).
    :param box_size: Box physical size in Mpc/h.
    :param h100: H/100.
    :param cosmo: cosmology in 'cosmolopy' format.
    :return:
    '''
    np.random.seed(seed)
    kx, ky, kz = np.mgrid[:N,:N,:N]
    kx[kx>N/2] = kx[kx>N/2]-N
    ky[ky>N/2] = ky[ky>N/2]-N
    kz[kz>N/2] = kz[kz>N/2]-N
    k = 2.0*np.pi*np.sqrt(kx**2+ky**2+kz**2)/N
    del kx
    del ky
    del kz
    k_phys = k*N/box_size*h100
    del k
    IC = np.random.normal(size=[N, N, N])
    # You can add constraints here
    # IC[(N/2-N/4):(N/2+N/4),(N/2-N/4):(N/2+N/4),:] -= .0005
    # IC[(N/2-2):(N/2+2),(N/2-2):(N/2+2),0] += 1.0
    # IC /= np.std(IC)
    # IC -= np.mean(IC)
    IC_fft = np.fft.fftn(IC)
    del IC
    Pk_amp = cp.perturbation.power_spectrum(k_phys, z=60.0, **cosmo)
    IC = np.real(np.fft.ifftn(IC_fft*np.sqrt(Pk_amp)))
    return IC
