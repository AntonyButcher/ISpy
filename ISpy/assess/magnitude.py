import numpy as np

def ml_cal(a,r):
    """Equation to calculate local magnitude california scale
       
    Arguments:
    Required:
    a - displacement amplitude in m
    r - hypocentral distance in km
    
    returns:
    mag  - Local magnitude
    """
    
    # Convert to nanometers
    a=a*1e9
    mag=(np.log10(a))+(1.11*np.log10(r))+(0.00189*r)-2.09

    return mag

def ml_nol(a,r):
    """
    Local magnitude using the NOL scale (Butcher et al. 2017).
    
    Arguments:
    Required:
    a - displacement amplitude in m
    r - hypocentral distance in km
    
    returns:
    mag  - Local magnitude
    """
    
    # Convert to nanometers
    a=a*1e9
    if r<=17:
        mag=(np.log10(a))+(1.17*np.log10(r))+(0.0514*r)-3
    elif r>17:
        mag=(np.log10(a))+(1.11*np.log10(r))+(0.00189*r)-2.09


    return mag

def ml_luc(a,r):
    """
    Equation to calculate local magnitude from Luckett et al 2019
    
    Arguments:
    Required:
    a - displacement amplitude in m
    r - hypocentral distance in km
    
    returns:
    mag  - Local magnitude
    """
    # Convert to nanometers
    a=a*1e9
    mag=(np.log10(a))+(1.11*np.log10(r))+(0.00189*r)-1.16*np.exp(-0.2*r)-2.09

    return mag

def ml_luc_amp(mag,r):
    """
    Inverse ML function which calulates amplitude for a give ML and distance.
    Uses the Luckett et al. 2019 scale.
    
    Arguments:
    Required:
    mag  - Local magnitude
    r - hypocentral distance in km
    
    returns:
    amp - displacement amplitude in m
    """
    logamp=(mag-((1.11*np.log10(r))+(0.00189*r)-1.16*np.exp(-0.2*r)-2.09))

    # Convert to meters
    amp=(10**logamp)/1e9
    
    return amp

def detect_limits(mag,depth,noise=1e-7,boxsize=25,sampling=0.1):
    """
    Creates an array of detectability limits. Uses an inverse of the Luckett scale.
    Epicentre is in the centre of the box.
    
    Arguments:
    Required:
    mag - ML magnitude
    depth - depth of event
    Optional:
    noise - noise threshold. Displacement (m)
    boxsize - size of search area in km
    sampling - spacing between cells
    """
    
    # Define parameters
    array_size=int(boxsize/sampling)
    x=y=np.arange(-boxsize/2,boxsize/2,sampling)

    array=np.empty((array_size,array_size),dtype=float)
    
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            hypo=np.sqrt((x[i])**2+(y[j])**2+depth**2)
            amp=ml_luc_amp(mag,hypo)
            array[i,j]=amp
            
    detectable=np.where(array>=noise,1,0)
    
    return x,y,detectable