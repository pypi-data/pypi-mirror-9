'''
In this example a realization with some IC is generated.
'''

from py211mm.initialcond import *
import matplotlib.pyplot as plt

IC = get_IC(N=512, box_size=160)
IC /= 0.1
plt.imshow(IC[:,:,0], interpolation='nearest')
plt.show()

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