import time as time
import os

from ISpy.detect import trigger
from ISpy.utils import utils


stations=['PNR01','PNR02','PNR3A','PNR3B','PNR04','PNR05','PNR06','PNR07']
channels=['HHE','HHN','HHZ']
path="data/2019-08*"

print('Waiting')

try: os.mkdir('data/Local')
except: pass
try: os.mkdir('data/Noise')
except: pass


while True:
    
    
    new_files=utils.file_scanner(path,logname='file.log')
    
    if len(new_files) == 0:
        
        time.sleep(10)
        
    else:
        print('New file processed')
        print(time.asctime())
        for file in new_files:
            print(file)
            st=utils.data_in(file,stations,channels,plot=True)
            
            ids=trigger.iscoincidence(st,stations,channel='HHE',on=1,off=0.5,minsta=3,window=5)
            
            for id in ids:
                
                trigger.sac_picker(id,stations)
                pick = input("Would you like to repick the traces? (y/n)")
                if pick == 'y':
                    trigger.sac_picker(id,stations)                    
                
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
        
        


