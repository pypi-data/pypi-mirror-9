__author__ = 'kaurov'

import os.path
import glob
import numpy as np

def readifrit(path, nvar=[0], moden=2, skipmoden=2):
    '''
    Code for reading IFRIT files used by Nickolay Gnedin's code IFRIT.
    '''
    import struct
    import numpy as np
    openfile=open(path, "rb")
    dump = np.fromfile(openfile, dtype='i', count=moden)
    N1,N2,N3 = np.fromfile(openfile, dtype='i', count=3)
    dump = np.fromfile(openfile, dtype='i', count=moden)
    data=np.zeros([N1,N2,N3,np.size(nvar)])
    j=0
    for i in range(np.max(nvar)+1):
        dump = np.fromfile(openfile, dtype='i', count=moden)
        if i==nvar[j]:
            data[:,:,:,j]=np.reshape(np.fromfile(openfile, dtype='f4', count=N1*N2*N3), [N1, N2, N3])
            j=j+1
        else:
            dump=np.fromfile(openfile, dtype='f4', count=N1*N2*N3)
        dump = np.fromfile(openfile, dtype='i', count=moden)
    openfile.close()
    return N1,N2,N3,data


def readgic(path='/lustre/gnedin/REI/IC/P/rei20A_lr_M.den',moden=1):
    '''
    Reads only lr .den files.
    '''
    print 'test'
    openfile=open(path, "rb")
    ## Manifest
    dump = np.fromfile(openfile, dtype='i', count=moden)
    Manifest = np.fromfile(openfile, dtype=[('name','a256'),('iver','i4')],count=1)
    print Manifest[0]
    dump = np.fromfile(openfile, dtype='i', count=moden)
    ## Header
    dump = np.fromfile(openfile, dtype='i', count=moden)
    Header = np.fromfile(openfile, dtype=[('OmB','f4'),('OmDM','f4'),('OmL','f4'),('OmN','f4'),('h100','f4'),('enn','f4'),('sigma8','f4'),('akpivot','f4'),('aBegin','f4'),('cell','f4'),('delDC','f4'),('rmsDC','i4'),('Nx','i4'),('Ny','i4'),('Nz','i4'),('is','i4'),('is2','i4'),('Nrec','i4'),('Np','i4'),('idx','i4'),('iflag','i4'),('extra','i4')],count=1)
    print Header[0]
    dump = np.fromfile(openfile, dtype='i', count=moden)
    ## Body
    dump = np.fromfile(openfile, dtype='i', count=moden)
    if Header['idx']==0:
        dump = np.fromfile(openfile, dtype='i', count=100)
        data = np.fromfile(openfile, dtype='f4')
        data = data[np.arange(len(data))%1026<1024]
        data = data.reshape(Header['Nx'],Header['Ny'],Header['Nz'],order='A')
    dump = np.fromfile(openfile, dtype='i', count=moden)
    openfile.close()
    return Manifest, Header, data

def gic2ifrit(pathin,pathout):
    Manifest, Header, data = readgic(pathin)
    np.savez(pathout,Manifest=Manifest, Header=Header, data=data)
    return 0

def downsample2(data):
    N = data.shape[0]
    res = np.zeros([N/2, N/2, N/2])
    res[:, :, :] = data[::2,::2,::2] \
                   + data[1::2,::2,::2]\
                   + data[::2,1::2,::2] \
                   + data[::2,::2,1::2]\
                   + data[1::2,1::2,::2]\
                   + data[1::2,::2,1::2]\
                   + data[::2,1::2,1::2]\
                   + data[1::2,1::2,1::2]
    return res / 8.0