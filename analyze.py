import h5py, numpy as np
import argparse
from tqdm import tqdm
psr = argparse.ArgumentParser()
psr.add_argument('-i',dest='ipt')
psr.add_argument('-c', nargs='+', dest='ch')
psr.add_argument('-o',dest='opt')
args =psr.parse_args()
chs = [int(i) for i in args.ch]
with h5py.File(args.ipt,'r') as ipt:
    readout = ipt['Readout'][:]
wavelength = 10000
N=int(readout.shape[0]/wavelength)
result = np.zeros((N,),dtype=[('ADC{}'.format(i),'<f4') for i in chs]+[('std{}'.format(i),'<f4') for i in chs])
for j in chs:
    result['ADC{}'.format(j)] = np.mean(readout['ADC{}'.format(j)].reshape((-1,wavelength)),axis=1)
    result['std{}'.format(j)] = np.std(readout['ADC{}'.format(j)].reshape((-1,wavelength)),axis=1)
with h5py.File(args.opt, 'w') as opt:
    opt.create_dataset('ana', data=result, compression='gzip')