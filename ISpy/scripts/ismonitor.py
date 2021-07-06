"""
ISmonitor.py
created 06/07/21, A Butcher

Trigger script which continuously scans a waveform directory and processes new files using the workflow:

1. New waveform files imported into an obspy stream, detrended and bandpass filtered.
2. A plot of the data is created and displayed.
3. A coincidence function is applied to the stream (iscoincidence).
4. If events are identified, data are sliced into 5 second parts with P- and S-wave picks added.
5. These are saved as .sac files and .png images.
6. The .sac files are opened in SAC to allow the waveforms to be more accurately picked.
7. User asked if they want a .obs exported. If yes, dir moved to 'Local' dir, if no, dir moved to 'Noise' dir.
8. If .obs file requested, file exported.

Requires SAC to be install. (https://members.elsi.jp/~george/sac-download.html)
"""

import time as time
import os

from ISpy.detect import trigger
from ISpy.utils import utils

# Define stations, channels and waveform path directory
stations=['PNR01','PNR02','PNR3A','PNR3B','PNR04','PNR05','PNR06','PNR07']
channels=['HHE','HHN','HHZ']
path="data/2019-08*"

# Check directories are present and create them if not.
try: os.mkdir('data/Local')
except: pass
try: os.mkdir('data/Noise')
except: pass

print('Welcome to ISmonitor.py')
print('Waiting')

# Create a continuous loop
while True:
    
    # Check for files which are not in the log file
    new_files=utils.file_scanner(path,logname='file.log')
    
    # If no new files, wait 10 seconds and repeat
    if len(new_files) == 0:
        time.sleep(10)
        
    # When new file detected, apply processing workflow.  
    else:
        print('New file identified at %s'%(time.asctime()))

        for file in new_files:
            print(file)
            
            # Read in data and create .png image of data for manual inspection
            st=utils.data_in(file,stations,channels,plot=True)
            
            # Apply coincidence filter, which creates .sac files when triggered
            ids=trigger.iscoincidence(st,stations,channel='HHE',on=1,off=0.5,minsta=3,window=5)
            
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
        
        


