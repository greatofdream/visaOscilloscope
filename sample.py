import pyvisa
import h5py, numpy as np
import time, argparse
from tqdm import tqdm
psr = argparse.ArgumentParser()
psr.add_argument('-i', nargs='+', dest='ipt')
psr.add_argument('-o',dest='opt')
psr.add_argument('-N',dest='N',type=int,default=50000)
args =psr.parse_args()
chs = [int(i) for i in args.ipt]
# N = 40000
N = args.N
waveSampleLength = 10000

rmNet = pyvisa.ResourceManager()
print('begin record')
with rmNet.open_resource("TCPIP::192.168.1.29::INSTR") as scopeNet:
    # 预采数，确定数据大小
    print(scopeNet.query("*IDN?"))
    ymults = np.zeros(len(chs))
    yzeros = np.zeros(len(chs))
    yoffs = np.zeros(len(chs))
    for i, c in enumerate(chs):
        print('set the source:{}'.format(c))
        scopeNet.write('DATA:SOU CH{}'.format(c))
        scopeNet.write('DATA:START 1')
        scopeNet.write('DATA:STOP {}'.format(waveSampleLength))
        scopeNet.write('DATA:WIDTH 1') 
        scopeNet.write('DATA:ENC RPB')
        #scopeNet.write('WFMInpre:BIT_Nr 16')
        print(scopeNet.query('WFMOutpre:NR_pt?'))
        print('get the tick')
        ymult = float(scopeNet.query('WFMPRE:YMULT?')) # y-axis least count
        yzero = float(scopeNet.query('WFMPRE:YZERO?')) # y-axis zero error
        yoff = float(scopeNet.query('WFMPRE:YOFF?')) # y-axis offset
        xincr = float(scopeNet.query('WFMPRE:XINCR?')) # x-axis least count
        print('x tick: {}n{}; y tick: {}{}'.format(xincr*1e9,scopeNet.query('WFMOutpre:XUNit?'), ymult,scopeNet.query('WFMOutpre:YUNit?')))
        print('yzero:{};yoff:{}'.format(yzero,yoff))
        yzeros[i] = yzero
        yoffs[i] = yoff
        ymults[i] = ymult
    waveLength = int(scopeNet.query('WFMOutpre:NR_pt?'))
    
    dtype = [('EventID','<i4')]+[('ADC{}'.format(i),'<f4') for i in chs]
    sampleData = np.zeros(N*waveLength, dtype=dtype)
    print('record')
    for i in tqdm(range(N)):
        for j,c in enumerate(chs):
            scopeNet.write('DATA:SOU CH{}'.format(c))
            time.sleep(0.08)
            '''
            ymult = float(scopeNet.query('WFMPRE:YMULT?')) # y-axis least count
            yzero = float(scopeNet.query('WFMPRE:YZERO?')) # y-axis zero error
            yoff = float(scopeNet.query('WFMPRE:YOFF?')) # y-axis offset
            print('yzero:{};yoff:{}'.format(yzero,yoff))
            '''
            ADC_wave = scopeNet.query_binary_values('CURVE?', datatype='B',container=np.array)
            sampleData[(i*waveLength):((i+1)*waveLength)]['ADC{}'.format(c)]=(ADC_wave - yoffs[j])# * ymults[j] + yzeros[j]
        sampleData[(i*waveLength):((i+1)*waveLength)]['EventID'] = i
print('write h5')
with h5py.File(args.opt,'w') as opt:
    opt.attrs['xicnr'] = xincr
    for j,c in enumerate(chs):
        opt.attrs['yoff{}'.format(c)] = yoffs[j]
        opt.attrs['yzero{}'.format(c)] = yzeros[j]
        opt.attrs['ymult{}'.format(c)] = ymults[j]

    opt.attrs['wavelength'] = waveLength
    opt.create_dataset('Readout',data=sampleData,compression='gzip')