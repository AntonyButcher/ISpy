from obspy.core import read
from obspy import read_inventory
from obspy import Stream
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import time as time

def file_scanner(path,logname='file.log'):
    """
    Checks and records which waveform files have been processed.
    
    Arguments:
    Required:
    path - file path of waveform files e.g. "data/2019-08*"
    Optional:
    logname - file name of log file, default is 'file.log'
    """
    # Check if log file exists, if not create one
    if not os.path.exists(logname):
        f_out=open(logname,'x')
        f_out.write("ISpy trigger log file \nCreated %s \n"%(time.asctime()))
        f_out.close()
        
        old_files=[]

    # Read in file names from log file
    else:
        f_in=open(logname,'r')
        old_files = f_in.read().splitlines()[2:]
        f_in.close()

    # Current list of files 
    files=glob.glob(path)
    
    # List of new files found in the directory
    new_files=list(set(files) - set(old_files))

    f_out2=open(logname,'a')
    
    # Add the new files to log file
    for file in new_files:
        f_out2.write('%s\n'%(file))
    f_out2.close()
    
    return new_files

def data_in2(files,stations,channels,freqmin=1.5,freqmax=20.5, plot=False,imgdir='images/',openimg=True,inv=True):
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
    st=Stream()
    for file in files:
        st+=read(file)
    st=st.merge()
    stime=st[0].stats.starttime
    
    # Select traces from stream and place in order
    st2=Stream()
    for station in stations:
        for channel in channels:
            st2+=st.select(station=station,channel=channel)

    st.clear()  
    # Preprocess stream
    
    st2=st2.detrend(type='linear')
    st2=st2.taper(max_percentage=0.02,type='cosine')
    st2=st2.filter('bandpass',freqmin=freqmin,freqmax=freqmax)
    
    # Instrument correct
    for tr in st2:
        station=tr.stats.station

#         # Add location in case not present. Needed for response removal.
#         tr.stats.location='00'

        if inv==True:
            inv_file='Dataless/%s.dataless'%(station)
#             print(inv_file)
            if not os.path.exists(inv_file):
                print('Response file could not be found')            
                pass
            else:
    #                 tr.taper(max_percentage=0.01,type='cosine')
                finv = read_inventory(inv_file)

                tr=tr.detrend(type='linear')
                pre_filt = (freqmin,freqmin+0.5,freqmax-0.5,freqmax)
                tr.remove_response(inventory=finv, pre_filt=pre_filt, output="DISP")
    
    # Name file base on start time
    fileid=('%04d-%02d-%02d-%02d-%02d-%02d'%(stime.year,stime.month,stime.day,stime.hour,stime.minute,stime.second))
    
    # Plot seismic wave forms for inspection
    if plot==True:
        
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
                    
        fig, axs =plt.subplots(nrows=len(st2),sharex=True,sharey=False,figsize=(30,20))
        plt.xlabel('Time (s)')
        
        for i in range(len(st2)):
            axs[i].set_title("%s - %s: %s - %s"%(st2[i].stats.station,st2[i].stats.channel,st2[i].stats.starttime,st2[i].stats.endtime))
            axs[i].plot(st2[i].times(),st2[i].data,'k')
            axs[i].set_ylabel('Amp (Dis)')
            axs[i].grid()
            
            max_val=np.max(abs(st2[i].data))
            dis_val=2.5e-7
            
            if max_val < dis_val:
                axs[i].plot(st2[i].times(),st2[i].data,'k')
                axs[i].set_ylim(-1*dis_val,dis_val)
                
            elif max_val >= dis_val:
                axs[i].plot(st2[i].times(),st2[i].data,'g')
                axs[i].set_ylim(-1*max_val,max_val)
                
        plt.savefig("%s%s.png"%(imgdir,fileid))
        plt.close(fig)  
        
        if openimg==True:
        
            os.system ("open %s%s.png"%(imgdir,fileid))

    return st2

def data_in(filename,stations,channels,freqmin=2,freqmax=20, plot=False,imgdir='images/',openimg=True,inv=True):
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
    st2=st2.detrend(type='linear')
    st2=st2.filter('bandpass',freqmin=freqmin,freqmax=freqmax)
    
    
#     for tr in st2:
#         station=tr.stats.station
#         channel=tr.stats.channel
#         date=tr.stats.starttime

#         # Add location in case not present. Needed for response removal.
#         tr.stats.location='00'

#         if inv==True:
#             inv_file='Dataless/%s.dataless'%(station)
#             print(inv_file)
#             if not os.path.exists(inv_file):
#                 print('Response file could not be found')            
#                 pass
#             else:
#     #                 tr.taper(max_percentage=0.01,type='cosine')
#                 finv = read_inventory(inv_file)

#                 tr=tr.detrend(type='linear')
#                 pre_filt = (freqmin,freqmin+0.5,freqmax-0.5,freqmax)
#                 tr.remove_response(inventory=finv, pre_filt=pre_filt, output="DISP")

    # Name file base on start time
    fileid=('%04d-%02d-%02d-%02d-%02d-%02d'%(stime.year,stime.month,stime.day,stime.hour,stime.minute,stime.second))
    
    # Plot seismic wave forms for inspection
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
        
        if openimg==True:
        
            os.system ("open %s%s.png"%(imgdir,fileid))

    return st2
    
def tr_write(tr,path,id,resp=False,inv=False,freqmin=0.01,freqmax=50):
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
            tr.remove_response(inventory=inv, pre_filt=pre_filt, output="DISP")
    else:
        pass
    
    if inv==True:
        inv_file='Dataless/%s.dataless'%(station)
        print(inv_file)
        if not os.path.exists(inv_file):
            print('Response file could not be found')            
            pass
        else:
#                 tr.taper(max_percentage=0.01,type='cosine')
            finv = read_inventory(inv_file)
    
            tr=tr.detrend(type='linear')
            pre_filt = (freqmin,freqmin+0.5,freqmax-0.5,freqmax)
            tr.remove_response(inventory=finv, pre_filt=pre_filt, output="DISP")
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

def event_log(id,rawfile,obsfile):
    """
    Event log file for ISpy.
    
    Arguments:
    Required:
    id - event id
    rawfile - original raw waveform file
    obsfile - NNLOC obs file name
    """
    
    fname='data/%s/%s.log'%(id,id)
    logfile=open(fname,'x')
    
    logfile.write("ISpy event file, created %s\n"%((time.asctime())))
    logfile.write("EVENT %s\n"%(id))
    logfile.write("RAW %s\n"%(rawfile))
    logfile.write("OBSFILE %s\n"%(obsfile))
    
    logfile.close()
    