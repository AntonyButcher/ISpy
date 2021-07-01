from obspy.core import read
from obspy import Stream
import matplotlib.pyplot as plt
import os

def data_in(filename,stations,channels,freqmin=3,freqmax=10, plot=False,imgdir='images/'):
    """
    Seismic data reader with preprocessing and plotting functions.
    
    Arguments:
    Required:
    filename - file name of seismic data
    Optional:
    freqmin - minimum frequency for bandpass filter 
    freqmax - maximum frequency for bandpass filter
    plot - dayplot of day
    imgdir - directory to save seismic plots
    """
    # Read in data
    st=read(filename)
    stime=st[0].stats.starttime
    
    # Select traces from stream and place in order
    st2=Stream()
    for station in stations:
        for channel in channels:
            st2+=st.select(station=station,channel=channel)

    st.clear()  
    # Preprocess stream
    st2.detrend(type='linear')
    st2.filter('bandpass',freqmin=freqmin,freqmax=freqmax)
    
    # Name file base on start time
    fileid=('%04d-%02d-%02d-%02d-%02d-%02d'%(stime.year,stime.month,stime.day,stime.hour,stime.minute,stime.second))
    
    # Plot seimic wave forms for inspection
    if plot==True:
        
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
                    
        fig, axs =plt.subplots(nrows=len(st2),sharex=True,sharey=False,figsize=(10, 50))
        plt.xlabel('Time (s)')
        
        for i in range(len(st2)):
            axs[i].set_title("%s - %s: %s - %s"%(st2[i].stats.station,st2[i].stats.channel,st2[i].stats.starttime,st2[i].stats.endtime))
            axs[i].plot(st2[i].times(),st2[i].data,'k')
            axs[i].set_ylabel('Amplitude (counts)')
            axs[i].grid()
       
        plt.savefig("%s%s.png"%(imgdir,fileid))
        plt.close(fig)    

    return st
    
def tr_write(tr,path,id,resp=False,freqmin=0.01,freqmax=50):
    """ Removes the instrument response, and exports data to a SAC format.
    
    Arguments:
    Required:
    tr - obspy trace
    path - file path e.g. 'data/%s/SAC/'%(id)
    id - unique event id
    
    returns:
    file - name of sac waveform file.
    """
    network=tr.stats.network
    if network=="":
        network="GB"    
    station=tr.stats.station
    channel=tr.stats.channel
    date=tr.stats.starttime
    
    # Add location in case not present. Needed for response removal.
    tr.stats.location='00'
    
    if resp==True:
        resp_file='data/RESP/RESP.%s.%s.00.%s'%(network,station,channel)
        if not os.path.exists(resp_file):
#             resp_file='RESP/RESP.%s.%s..%s'%(network,station,channel)
#             if not os.path.exists(resp_file):
            print('Response file could not be found')            
            pass
        else:
#                 tr.taper(max_percentage=0.01,type='cosine')
            tr=tr.detrend(type='linear')
            pre_filt = (freqmin,freqmin+0.5,freqmax-0.5,freqmax)
            seedresp = {'filename': resp_file, 'date':date, 'units': 'DISP'} 
            tr.simulate(paz_remove=None, pre_filt=pre_filt, seedresp=seedresp)
    else:
        pass
    
    # Create network name in none exists
    if network=="":
        network="xx"
        
    if not os.path.exists(path):
        os.makedirs(path)
        
    file="%s.%s.%s.%s.sac"%(network,station,id,channel)
    filename="%s%s"%(path,file)
    print(filename)
#     tr=tr.slice(tr.stats.starttime+30,tr.stats.starttime+90)
    tr.write(filename,format='SAC')
    
    return file