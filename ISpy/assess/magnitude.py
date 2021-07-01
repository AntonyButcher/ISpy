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