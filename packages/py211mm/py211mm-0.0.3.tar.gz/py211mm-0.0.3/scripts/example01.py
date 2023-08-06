'''
In this example a realization with some IC is generated.
'''

from py211mm.initialcond import *
import matplotlib.pyplot as plt
from py211mm.models import *
import pkg_resources

IC = get_IC(N=256, box_size=80)
plt.imshow(IC[:,:,0], interpolation='nearest')
plt.show()

fit_dir = pkg_resources.resource_filename('py211mm','fit')
fit = np.load(fit_dir+'/Gnedin2014_fit_barriers.npz')

r_list = fit['r_list']
barriers = fit['barriers']
scale_f = fit['scale_f']

res = apply_barrier(IC, r_list, barriers, shells=False, rescale=1.0)
1.*res.sum(0).sum(0).sum(0)/256**3


plt.imshow(res.shape[3] - np.sum(res[:, :, 20, :],2).astype(np.float), interpolation='nearest', cmap='Spectral')

# res = apply_barrier(IC, r_list, barriers, shells=False, rescale=1.0)
# 1.*res.sum(0).sum(0).sum(0)/256**3
#
# plt.imshow(res.shape[3] - np.sum(res[:, :, 120, :],2).astype(np.float), interpolation='nearest', cmap='Spectral')
#
#
# plt.imshow(IC[:,:,0], interpolation='nearest')
# plt.show()
#
#
#
# plt.plot(r_list, barriers)
# plt.xscale('log')
