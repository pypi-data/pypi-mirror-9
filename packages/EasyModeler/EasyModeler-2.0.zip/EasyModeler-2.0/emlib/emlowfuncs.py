
import logging
import datetime
import numpy as np
import math

FORMAT = '%(levelname)s -%(lineno)s- %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
emlog = logging.getLogger('EASYMODEL')


def NuN(value, Type=None):
    '''
    Tries to convert a string into a float, numpy.nan, or specified type.  Returns the conversion or the original string if failed.

    :param value: The string to convert.
    :param Type:  Optinal type to convert value to.
    :type value: str
    :type Type: float,int,str,...
    :returns: value
    :rtype: float,numpy.nan,str,...
    
    
    **Advantages**:
     - This function is useful in sanitizing text input files.

    **Drawbacks**:
     - Does not alert calling function if conversion failed.
    
    :Example:
    
    If value(str) is "NaN"  or "None", **NuN** will return *numpy.nan*
    
     >>> toTest = "NaN"
     >>> sanitized = NuN(toTest)
     >>> numpy.isnan(sanitized)
     True

    **NuN** will try to convert value (str) into a float.  If this is unsuccessful **NuN** will return the string.
     
     >>> a = "3.4"
     >>> b = "three point four"
     >>> a = NuN(a)
     >>> b = NuN(b)
     >>> type(a)
     <type 'float'>
     >>> type(b)
     <type 'str'>


    Empty strings will be returned as *numpy.nan*.  This is useful for importing data tables with missing values for cells.

     >>> empty = ''
     >>> sanitized = NuN(empty)
     >>> print sanitized
     nan
     >>> numpy.isnan(sanitized)
     True

    Occasionally we may want to import a series of text values as int instead of float.

     >>> string = "5"
     >>> integer = NuN(string, Type=int)
     >>> type(integer)
     <type 'int'>
     
    '''
    if not value:
        return np.nan
    if (value.lower() == 'nan') or (value.lower() == '') or (value.lower() == 'none'):
        return np.nan
    else:
        if Type:
            try:
                Type(value)
                return Type(value)
            except:
                return value
        else:
            try:
                float(value)
                return float(value)
            except ValueError:
                return value



def mmddyyyy2date(datestr):
    '''
    mmddyyyy2date

    INPUT:
    datestr     string

    OUTPUT:
    date        datetime object

    Method converts a date string in the form mm/dd/yyyy into a datetime object.
    Text deliminators are expected in the input string.

    '''
    debug = 0 #local debug instance
    date = datetime.date(int(datestr[6:]),int(datestr[:2]),int(datestr[3:5]))

    if debug:
        print (datestr, "converted to", date)
    return date


def GFSingle(obs,obsE,model):
    '''
    GFSingle

    INPUT:
    obs     float scalar
    obsE    float scalar
    model   float scalar

    OUTPUT:
    MSE     float scalar
    WMSE    float scalar
    RANGE   float scalar
    MSER    float scalar


    This is a pattern match program which tests goodness of fit
    for asingle point for models against observation results.

    '''
    diff = (abs(obs) - abs(model))
    diff2 = diff * diff

    #set the stdev to 1 if less for this test
    if obsE < 1:
        WobsE = 1
    else:
        WobsE = obsE

    WMSE = diff2 / (math.pow(WobsE,2))
    MSE = math.pow(((obs - model)),2)
    if (model < (obs + obsE)) and (model > (obs - obsE)):
        RANGE = 1
        MSER = 0
    else:
        RANGE = 0
        if (model < (obs - obsE)):
            MSER = math.pow(((obs - obsE) - model),2)
        else:
            MSER = math.pow(((obs + obsE) - model),2)

    emlog.debug(str((obs - obsE)) + "\t"+str(model)+"\t"+str((obs + obsE))+"\t"+str(RANGE))

    return MSE,WMSE,RANGE,MSER
               
def GFModel(model, Observations):
    """Fits Model results to observations

    :param model: Model to test
    :param Observations:  Historical Observations
    :type model: emlib.Model
    :type Observations: emlib.Observations
    :returns: GF strings
    :rtype: tuple

    """
    obsT = Observations.T 
    obsXM = Observations.XM
    obsXE = Observations.XE 


    WMSE = 0
    MSE = 0
    matches = 0
    indexobs = 0
    RANGE = 0
    MSER = 0
    O = []
    E = []
    emlog.debug("-STDEV\tEXP\t+STDEV\tISRANGE?")
    for i in obsT:
        indexsim = 0
        for k in model.computedT:
            indexsim+=1 #we are one index ahead
            #obs happend at the same exact deltaT of model response
            if k == i :
                matches+=1
                O.append(obsXM[indexobs])
                E.append(model.computed[indexsim-1])
                a,b,c,d = GFSingle(obsXM[indexobs],obsXE[indexobs],model.computed[indexsim-1][0])
                MSE+=a
                WMSE+=b
                RANGE+=c
                MSER+=d
                break
        indexobs +=1
            
    WMSE = round(math.sqrt(WMSE),1)
    MSE = round(math.sqrt(MSE),1)
    RANGE = round((100 * float(RANGE)/matches),1)
    MSER = round(math.sqrt(MSER),1)
    emlog.debug("GFMODEL #"+str(matches)+" MSE:"+str(MSE)+" RANGE%"+str(RANGE)+" MSER:"+str(MSER)+" WMSE:"+str(WMSE))
    return [matches,MSE,WMSE,RANGE,MSER,O,E]

