import pandas as pd
import matplotlib.pyplot as plt
import os


from ISpy.utils import utils

from obspy.core import read
from obspy.signal.trigger import coincidence_trigger
from obspy.signal.trigger import z_detect
from obspy.signal.trigger import trigger_onset
from obspy.signal.trigger import plot_trigger

def trigger_check(st,station,channel,on=1,off=0.5,window=5):
    """Function to check the stalta trigger levels using zdetect.
    
    Arguments:
    Required:
    st - obspy stream
    station - station to check
    channel - channel to check
    windown - zdetect window"""
    
    st=st.select(station=station,channel=channel)
    df=st[0].stats.sampling_rate
    
    for tr in st:
        cft=z_detect(tr.data,int(window*df))
        plot_trigger(tr,cft,on,off)
        

def iscoincidence(st,stations,channel='HHE',on=1,off=0.5,minsta=3,window=5):
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
                file=utils.tr_write(st3[0],sacpath,id,resp=True,freqmin=0.01,freqmax=50)
#                 print(file)

                imgpath='data/%s/img/'%(id)
                if not os.path.exists(imgpath):
                    os.makedirs(imgpath)

                fig=plt.figure(figsize=[10,3])
                plt.title('%s - %s'%(st3[0].stats.starttime,st3[0].stats.endtime))
                plt.plot(st3[0].times(),st3[0].data,'k')
                plt.axvline(x=onset_time-(ttime-2),color='r')
                plt.xlim(0,5)
                plt.xlabel('Time (s)')
                plt.ylabel('Displacement (m)')
                plt.tight_layout()
                plt.savefig("%s%s.png"%(imgpath,file))
                plt.close(fig)
    #             plt.show()

                # Read in again to include pick times
                st4=read("%s%s"%(sacpath,file))
#                 print(onset_time-(ttime-2))

                if channel=='HHZ':
                    st4[0].stats.sac['ka']='IPU0'
                    st4[0].stats.sac['a']=onset_time-(ttime-2)

                else:
                    st4[0].stats.sac['kt0']='ISU0'
                    st4[0].stats.sac['t0']=onset_time-(ttime-2)

                file=utils.tr_write(st4[0],sacpath,id,resp=False,freqmin=0.01,freqmax=50)

    return id 
    
def sac_picker(id,stations):
    """
    SAC wrapper. Opens pick file created from iscoincidence in SAC.
    
    Arguments:
    Required:
    id - event id assigned by iscoincidence
    stations - station list
    
    Notes:
    Opens a xwindow and ppk plot which is used to pick P and S arrivals.
    In xwindow pick p-wave on z component using 'p' key and s-wave on e and n component 
    using 's' key. When finished press q.
    
    """
    
    for station in stations:
        sac="printf \"m pick.mac %s %s \"| sac"%(id,station)
        os.system(sac)  
    
def sac_to_nnloc(id,stations,channels,pick_err=0.02):
    """
    Exports sac header into an .obs file for NNLOC.
    
    Arguments:
    Required:
    id - event id assigned by iscoincidence
    optional:
    pick_err - pick error in seconds
    """
    
    # Read in sac files
    pickfiles="data/%s/SAC/*.sac"%(id)
    st_picks=read(pickfiles)
    
    # Define and open nnloc .obs file
    event_out_fname="%s.obs"%(id)
    f_out = open(event_out_fname, 'w')
    
    # Loop through each station and channel and write picks to .obs file
    for station in stations:
        for channel in channels:
            st_tmp=st_picks.select(station=station,channel=channel)
            stime=st_tmp[0].stats.starttime

            if channel == 'HHZ':
                phase='P'
                ptime=stime+st_tmp[0].stats.sac['a']
            else:
                phase='S'
                ptime=stime+st_tmp[0].stats.sac['t0']
            
            # In case no pick present
            if stime-ptime == 0:
                pass
            
            else:
                pick_date=str('%04d%02d%02d'%(ptime.year,ptime.month,ptime.day))
                pick_hrmin=str('%02d%02d'%(ptime.hour,ptime.minute))
                pick_secs=str('%02d.%03d'%(ptime.second,ptime.microsecond))
                pick_err=str(pick_err)

                f_out.write(" ".join((station, "? ? ?", phase, "?", pick_date, pick_hrmin, pick_secs,"GAU", pick_err, "0.0 0.0 0.0 1.0", "\n")))

    f_out.close()    
    print('%s file created'%(event_out_fname))
    