import wave, struct, math
from scipy.io.wavfile import write, read
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram as pdg
import os

'''load base image/timeseries and GM mask'''
img = nib.load('opti_combined_raw.nii_volreg.nii')
gm = nib.load('gm_mask.nii')
img = img.get_data()
gm = gm.get_data()

gms=[]
for i in range(len(img[0,0,0,:])):
    gms.append(gm)
    
gms=np.swapaxes(gms,0,1)
gms=np.swapaxes(gms,1,2)    
gms=np.swapaxes(gms,2,3)

'''masks out all non-cortex'''
img[ gm != 0] = np.nan

'''flattens cortex to the average overall timeseries (global signal?)'''
avg1 = np.nanmean(img, axis=0)
avg2 = np.nanmean(avg1, axis=0)
avg3 = np.nanmean(avg2, axis=0)

'''Generates array of PSDs to be converted to sound, corresponding to activation over time'''
'''Also generates parallel array of the global average PSD to be subtracted out'''
TR = 0.6
n = 100 #number of TRs in window
f = 1 / TR
i=0
psd_evolution , globalSignal = [] , []
while((i+n) < len(avg3)):
    ts = avg3[i:i+n]    
    freq , pxx = pdg(ts, fs=f )
    sampleFreq = (2*len(pxx))-1
    globalMeanFreq , globalPXX = pdg(avg3 , fs=f , nfft=(2*len(pxx))-1)   
    '''basline not removed''' 
    #psd_evolution.append( pxx )  
    '''basline removed'''
    psd_evolution.append(np.subtract(pxx , globalPXX))    
    i+=1



'''Generates a sinusoidal value of particular frequency'''
def gen_value(frequency , sampleRate ):
    value=[]
    domain = np.arange(0 , 2*np.pi , (2*np.pi/sampleRate))
    for i in range(len(domain)):
        value.append(int(32767*math.cos(frequency*domain[i])))   
    return(value)
    

'''Generates one TR's worth of sounds with certain weights per
   frequency, depending on the PSD of image'''    
def gen_master(duration, sampleRate, freqs , filename, weights):
    wavef = wave.open(filename,'w')
    wavef.setnchannels(1) # mono
    wavef.setsampwidth(2) 
    wavef.setframerate(sampleRate)    
    
    value = np.zeros(sampleRate)
    if(len(weights) != 0 and np.max(weights) != 0):
        #weights = weights / np.max(weights)
        print('')
    else:
        weights = np.zeros( 10000 )
    for j in range(len(freqs)):
        term = gen_value(freqs[j], sampleRate)
        term = np.multiply(weights[j] , term)
        value += term
        
    normalizer = np.max(value) / 32767.
    if(normalizer !=0):
        value = np.divide(value , normalizer)
    
    for i in value:
        i = i / len(freqs)
        data = struct.pack('<h', i)
        wavef.writeframesraw( data )
    wavef.writeframes('')
    wavef.close()    
    return(weights , value)

'''Joins file a and file b, deletes file b which should be a temp file'''    
def stitch(file_a , file_b , writeFreq):
    a=read(file_a)
    b=read(file_b)
    c=np.append(a[1] , b[1])
    d=write(file_a , 2000 , c)
    os.remove(file_b)
    return()

'''A loop which essentially runs the whole operation for a given fmri timeseries'''
for j in range(len(psd_evolution)):
    if(j==0):
        #weights , x =gen_master(1, 44100, np.arange(1,232,4), 'psd.wav' , psd_evolution[j])        
        weights , x =gen_master(0.6, 2000, np.arange(500,1000,10), 'psd.wav' , psd_evolution[j])
        print('start!')
    else:
        #weights , x =gen_master(1, 44100, np.arange(1,232,4), 'temp.wav' , psd_evolution[j])
        weights , x =gen_master(0.6, 2000, np.arange(500,1000,10), 'temp.wav' , psd_evolution[j])
        stitch('psd.wav','temp.wav', sampleFreq)
        print(j)