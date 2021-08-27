import h5py, numpy as np
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
psr = argparse.ArgumentParser()
psr.add_argument('-i',dest='ipt')
psr.add_argument('-c', nargs='+', dest='ch')
psr.add_argument('-o',dest='opt')
args =psr.parse_args()
chs = [int(i) for i in args.ch]
params={
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'x-large',
     'axes.titlesize':'x-large',
    'xtick.labelsize':'x-large',
     'ytick.labelsize':'x-large'
}
plt.rcParams.update(params)

def compare(h5file,pngout,chs):
    with h5py.File(h5file,'r') as ipt:
        result = ipt['ana'][:]
    N=result.shape[0]
    baseDf134 = pd.DataFrame({
    'ADCmean':np.concatenate([result['ADC{}'.format(i)]*1000 for i in chs]),
                        'ADCstd':np.concatenate([result['std{}'.format(i)]*1000 for i in chs]),
                      'channel':np.concatenate([N*['{}'.format(i)] for i in chs])
                     })
    hi = sns.jointplot(data=baseDf134, x='ADCmean',y='ADCstd',hue='channel',height=10)
    hi.ax_joint.set_xlabel('mean/mV')
    hi.ax_joint.set_ylabel('std/mV')
    hi.ax_joint.set_title(['{}:mean{:.2f},std{:.2f} '.format(ch,1000*np.mean(result['ADC{}'.format(ch)]),1000*np.mean(result['std{}'.format(ch)])) for ch in chs])
    plt.tight_layout()
    plt.savefig(pngout)
compare(args.ipt,args.opt,chs)