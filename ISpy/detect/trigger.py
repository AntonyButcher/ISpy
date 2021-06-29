import pandas as pd
import matplotlib.pyplot as plt
import os

from obspy.core import read
from obspy.signal.trigger import coincidence_trigger
from obspy.signal.trigger import z_detect
from obspy.signal.trigger import trigger_onset

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

def iscoin(st,stations,channel='HHE',on=1,off=0.5,minsta=3,window=5):
    """Coincidence function based on obspy's zdetect function. 
    Identifies triggers and saves sac files with pick times.
    
    Arguments:
    Required:
    st - obspy stream
    stations - list of stations
    channel - channel to apply trigger
    """
    
    # Select channel to use
    st2=st.copy()
    st2=st2.select(channel=channel)
    
    # define sampling rate and start time 
    df=st[0].stats.sampling_rate
    stime=st[0].stats.starttime
    
    # Apply coindidence filter using z-detect method
    trig=coincidence_trigger('zdetect',1,0.5,st2,3,details=True,nsta=int(window*df))
    
    trig_pd=pd.DataFrame(trig)
    
    if len(trig_pd)>0:
        
        ttime=trig_pd.time[0]
        
        id=('%04d%02d%02d%02d%02d%02d'%(ttime.year,ttime.month,ttime.day,ttime.hour,ttime.minute,ttime.second))
        print(id)
        for station in stations:
            for channel in ('HHE','HHN','HHZ'):
                # Select the trace
                st2=st.copy()
                st2=st2.select(station=station)
                st2=st2.select(channel=channel)

                # Apply stalta to trace to identify pick times
                cft=z_detect(st2[0].data,int(window*df))
                list=trigger_onset(cft,0.3,0.2)
                onset_time=stime+list[0][0]/df

                # Slice the data in 5 second files
                st3=st2.copy()
                st3=st3.slice(ttime-2,ttime+3)

                # Save SAC file
                sacpath='data/%s/SAC/'%(id)
                file=tr_write(st3[0],sacpath,id,resp=True,freqmin=0.01,freqmax=50)
                print(file)

                imgpath='data/%s/img/'%(id)
                if not os.path.exists(imgpath):
                    os.makedirs(imgpath)

                fig=plt.figure(figsize=[10,3])
                plt.title('%s - %s'%(st3[0].stats.starttime,st3[0].stats.endtime))
                plt.plot(st3[0].times(),st3[0].data,'k')
                plt.axvline(x=onset_time-(ttime-2),color='r')
                plt.xlim(0,5)
                plt.xlabel('Time (s)')
                plt.savefig("%s%s.png"%(imgpath,file))
                plt.close(fig)
    #             plt.show()

                # Read in again to include pick times
                st4=read("%s%s"%(sacpath,file))
                print(onset_time-(ttime-2))

                if channel=='HHZ':
                    st4[0].stats.sac['ka']='IPU0'
                    st4[0].stats.sac['a']=onset_time-(ttime-2)

                else:
                    st4[0].stats.sac['kt0']='ISU0'
                    st4[0].stats.sac['t0']=onset_time-(ttime-2)

                file=tr_write(st4[0],sacpath,id,resp=False,freqmin=0.01,freqmax=50)

        
    
    

