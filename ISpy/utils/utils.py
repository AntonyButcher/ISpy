from obspy.core import read
import os


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