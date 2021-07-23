import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# from convertbng.util import convert_bng, convert_lonlat


def nnloc_read(locfile, maxerr=5):
    """
    NNLOC location reader. 
    
    Arguments:
    Required:
    locfile - NNLOC .hyp location file
    Optional:
    maxerr - Cut off limit of location std
    """  
    
    east=[]
    north=[]
    z=[]
    time=[]
    year=[]
    mth=[]
    dy=[]
    hr=[]
    mins=[]
    sec=[]
    success=[]
    stdxx=[]
    stdyy=[]
    stdzz=[]


    with open(locfile, 'r') as f:
        for line in f.readlines():

            if line.startswith("NLLOC"):
                time.append(line.split()[1])
                success.append(line.split()[2])
                #print line.split()[2]

            if line.startswith("HYPOCENTER"):
                east.append(float(line.split()[2]))
                north.append(float(line.split()[4]))
                z.append(float(line.split()[6]))
            if line.startswith("GEOGRAPHIC"):
                year.append(int(line.split()[2]))
                mth.append(int(line.split()[3]))
                dy.append(int(line.split()[4]))
                hr.append(int(line.split()[5]))
                mins.append(int(line.split()[6]))
                sec.append(float(line.split()[7]))

    #         print(east)
            if line.startswith("STATISTICS"):
                stdxx.append(np.sqrt(float(line.split()[8])))
                stdyy.append(np.sqrt(float(line.split()[14])))
                stdzz.append(np.sqrt(float(line.split()[18])))
                print(success[-1])
                if success[-1]=="\"REJECTED\"":
    #                 print("East", east)
                    east.pop()
                    north.pop()
                    z.pop()
                    time.pop()
                    year.pop()
                    mth.pop()
                    dy.pop()
                    hr.pop()
                    mins.pop()
                    sec.pop()
                    stdxx.pop()
                    stdyy.pop()
                    stdzz.pop()
                elif np.abs(stdxx[-1]) > maxerr or np.abs(stdyy[-1]) > maxerr or np.abs(stdzz[-1]) > maxerr:
                    east.pop()
                    north.pop()
                    z.pop()
                    time.pop()
                    year.pop()
                    mth.pop()
                    dy.pop()
                    hr.pop()
                    mins.pop()
                    sec.pop()
                    stdxx.pop()
                    stdyy.pop()
                    stdzz.pop()





    f.close()
    
    loc={'East':east,'North':north,'Depth':z,'Stdxx':stdxx,'Stdyy':stdyy,'Stdzz':stdzz}
    loc=pd.DataFrame(loc)
    
    return loc

def loc_plot(df,stations=[],extent=1,fname='Location.png'):
    
    """
    Plotting function to be used with nnloc_read.
    
    Arguments:
    Required:
    df - locations from the nnloc_read function
    Optional:
    stations - location of seismic stations 
    extent - extent around epicentre for figure limits
    fname - file name of the image     
    """
    
    fig=plt.figure(figsize=(12,12))
    ax1=plt.subplot(2,2,1)
    plt.grid(linestyle='--',)
    plt.gca().set_aspect('equal', adjustable='box')
    ax1.scatter(df.East,df.North,c='r',marker='*',s=100)
    ax1.scatter(stations.East,stations.North,c='g',marker='v',s=75)
    ax1.set_xlim([df.East[0]-extent,df.East[0]+extent])
    ax1.set_ylim([df.North[0]-extent,df.North[0]+extent])
    ax1.set_xlabel("Easting (m)", fontsize=12)
    ax1.set_ylabel("Northing (m)", fontsize=12)


    ax2=plt.subplot(2,2,2)
    plt.grid(linestyle='--',)
    plt.gca().set_aspect('equal', adjustable='box')
    ax2.scatter(df.Depth,df.North,c='r',marker='*',s=100)
    ax2.scatter(stations.Depth,stations.North,c='g',marker='>',s=75)
    ax2.set_ylim([df.North[0]-extent,df.North[0]+extent])
    ax2.set_xlim(2,-0.1)
    ax2.set_ylabel("Northing (m)", fontsize=12)
    ax2.set_xlabel("Depth (m)", fontsize=12)
    plt.gca().invert_xaxis()

    ax3=plt.subplot(2,2,3)
    plt.grid(linestyle='--',)
    plt.gca().set_aspect('equal', adjustable='box')
    evt=ax3.scatter(df.East,df.Depth,c='r',marker='*',s=100,label="Event")
    sts=ax3.scatter(stations.East,stations.Depth,c='g',marker='v',s=75,label='Stations')
    ax3.set_xlim([df.East[0]-extent,df.East[0]+extent])
    ax3.set_ylim(2,-0.1)
    ax3.set_xlabel("Easting (m)", fontsize=12)
    ax3.set_ylabel("Depth (m)", fontsize=12)

    ax3.legend(handles=[evt,sts],fontsize=12,loc=1,bbox_to_anchor=(1.6, 1))


#     plt.tight_layout()
    plt.savefig(fname,format='png')
    plt.show()

    
def pd_convert_latlon(df,x='East',y='North'):
    """
    Converts bng coordinates to lat and lon and adds column to panda dataframe.
    
    Arguments:
    Required:
    df - panda dataframe with grid coordinates
    Optional:
    x - name of eastings column
    y - name of northing column    
    """
    
    conv_results=convert_lonlat(df[x],df[y])
    df['lat']=conv_results[1]
    df['lon']=conv_results[0]

    return df

def latlong_distn(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points defined by latitude and longitude.
    
    Arguments:
    Required:
    lat1 - latitude of 1st location
    lon1 - longitude of 1st location
    lat2 - latitude of 2nd location
    lat2 - latitude of 2nd location
    """

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = np.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = lon1*degrees_to_radians
    theta2 = lon2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (np.sin(phi1)*np.sin(phi2)*np.cos(theta1 - theta2) +
           np.cos(phi1)*np.cos(phi2))
    arc = np.arccos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return (arc*6378.137)

def loc_log(id,rawfile,obsfile):
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