"""
ISmonitor.py
created 06/07/21, A Butcher

Trigger script which continuously scans a waveform directory and processes new files using the workflow:

1. New waveform files imported into an obspy stream, detrended and bandpass filtered (utils.data_in).
2. A plot of the data is created and displayed.
3. A coincidence function is applied to the stream (trigger.iscoincidence).
4. If events are identified, data are sliced into 5 second parts with P- and S-wave picks added.
5. These are saved as .sac files and .png images.
6. The .sac files are opened in SAC to allow the waveforms to be more accurately picked.
7. User asked if they want a .obs exported. If yes, dir moved to 'Local' dir, if no, dir moved to 'Noise' dir.
8. If .obs file requested, file exported.

Requires SAC to be install. (https://members.elsi.jp/~george/sac-download.html)
"""

import time as time
import glob
import os

from ISpy.detect import trigger
from ISpy.utils import utils

# Define stations, channels and waveform path directory
stations=['WRE1','WRE2','WRE3','WRE4','WRE5']
# stations=['WRE2','WRE3','WRE4','WRE5']
channels=['HHE','HHN','HHZ']
path='/Volumes/outerlimits2/*/*/*.msd'

# Check directories are present and create them if not.
try: os.mkdir('data/Local')
except: pass
try: os.mkdir('data/Noise')
except: pass

print('Welcome to ISmonitor.py version 2')



for x in range(5):
    mode = input("Interactive picking mode? (y/n)")
    
    if mode == 'y':
        openimg_val=True
        break
    elif mode == 'n':
        openimg_val=False
        break
    else:
        print('Try again! y/n?')
        continue

print('Waiting')

# Create a continuous loop
while True:
    
    
    tnow=time.gmtime()
            
    if tnow.tm_sec == 20:
        
        # Correction for midnight
        if tnow.tm_hour != 0:
            modhour=tnow.tm_hour-1
            modday=tnow.tm_yday
        elif tnow.tm_hour == 0:
            modhour=23
            modday=tnow.tm_yday-1
            
        # Correction to cope with hour change    
        if tnow.tm_min >= 3:
            oldpath='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(tnow.tm_yday,tnow.tm_hour,tnow.tm_min-3)
            path='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(tnow.tm_yday,tnow.tm_hour,tnow.tm_min-2)        
        elif tnow.tm_min == 2:
            oldpath='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(modday,modhour,59)
            path='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(tnow.tm_yday,tnow.tm_hour,tnow.tm_min-2)
        elif tnow.tm_min == 1:
            oldpath='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(modday,modhour,58)
            path='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(modday,modhour,59)
        elif tnow.tm_min == 0:
            oldpath='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(modday,modhour,57)
            path='/Volumes/outerlimits2/*/*/*.%02d.%02d.%02d.00.msd'%(modday,modhour,58)
                                                                      
            
        oldfiles=glob.glob(oldpath)
        files=glob.glob(path)

        new_files=oldfiles+files


        print('%s new files identified on %s'%(len(new_files),time.asctime()))
        
        ids=[]
        try:
            # Read in data and create .png image of data for manual inspection
            st=utils.data_in2(new_files,stations,channels,plot=True,openimg=openimg_val)
            # Apply coincidence trigger, which creates .sac files when triggered
            ids,iwrite=trigger.iscoincidence(st,stations,channel='HHZ',on=3,off=2.5,minsta=3,window=2)

        except:
            print("Files missing")
            time.sleep(30)
            continue


        if iwrite == 1:
            if mode == 'y':
                for id in ids:

                    # For each event detected, open .sac file in SAC for manual inspection. 
                    trigger.sac_picker(id,stations)
                    pick = input("Would you like to repick the traces? (y/n)")
                    if pick == 'y':
                        trigger.sac_picker(id,stations)   

                    # Export NNLOC .obs file if event identified.                
                    var = input("Would you like to output an .obs file? (y/n)")
                    if var =='y':
                        event_out_fname=trigger.sac_to_nnloc(id,stations,channels,pick_err=0.02)
                        print("%s file created"%(event_out_fname))
                        os.system("mv data/%s data/Local"%(id))

                    elif var=='n':
                        os.system("mv data/%s data/Noise"%(id))

                    else:
                        var = input("Would you like to output an .obs file? (y/n)")

            print('Waiting')
        
#     # If no new files, wait 10 seconds and repeat
#     elif len(new_files) == 0:
#         time.sleep(57)
#         continue
        
#     elif len(new_files) != 15 and len(new_files) != 0:
#         print(len(new_files))
#         time.sleep(10)
                    

        


        


