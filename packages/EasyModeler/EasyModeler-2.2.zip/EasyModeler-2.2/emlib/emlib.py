
import sys
import os
import copy
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
from scipy.integrate import odeint
import scipy
import logging
import datetime


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
    Converts mm/dd/yyyy str into a :class:`datetime.date` object
    
    :param datestr: The mm/dd/yyyy string to convert.
    :type datestr: str
    :returns: date
    :rtype: datetime.date
    
    Method converts a date string in the form mm/dd/yyyy into a :class:`datetime.date` object.
    Text deliminators are expected in the input string.
    
    :Example:
    
    Converting a datestring to :class:`datetime.date` object:
    
     >>> toTest = "05/20/2013"
     >>> date = mmddyy2date(toTest)
     >>> print date
     2013-05-20
     >>> type(date)
     <type 'datetime.date'>
     
    '''
    date = datetime.date(int(datestr[6:]),int(datestr[:2]),int(datestr[3:5]))

    return date


def GFSingle(mean,stdev,model):
    '''
    Test fitness of single model dT

    
    :param mean: Observation Mean
    :type mean: float
    :param stdev: Observation STDEV
    :type stdev: float
    :param model: Simulated value **expected**
    :type model: float
    
    :returns: MSE,WMSE,RANGE,MSER
    :rtype: float,float,float,float
  

    This is a pattern match program which tests goodness of fit
    for asingle point for models against Observation results.
    
    .. note::  This function typically only called by :func:`emlib.GFModel` 
    

    '''
    obs = mean
    obsE = stdev
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
               
def GFModel(model, Observation):
    """Fits Model results to Observation

    :param model: Model to test
    :param Observation:  Historical Observation
    :type model: emlib.Model
    :type Observation: emlib.Observation
    :returns: Fitness object
    :rtype: emlib.Fitness

    """
    obsT = Observation.T 
    obsXM = Observation.XM
    obsXE = Observation.XE 


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
    return Fitness([matches,MSE,WMSE,RANGE,MSER,O,E])


class Calibration:
    """
    A collection of :class:`emlib.Coefficient` for a model.
    
    :param coeffs=: list of :class:`emlib.Coefficient`
    :param directory=:  directory
    :param filename=: filename
    :type coeffs=: list,emlib.Coefficient
    :type directory=: str
    :type filename=: str
    
    """
    _count = 0
    def __init__(self, coeffs=None, directory=None ,filename=None):
        self.__class__._count +=1
        
        self.initial = []
        self.ID = self.__class__._count
        emlog.info('New Calibration instance: '+str(self.ID))
        self.dir = directory
        self.filename = filename
        self.C = []
        if not directory:
            self.dir = ""
        if filename:
            self.Read(filename)
        if coeffs:
            self.C = coeffs[:]
            
    def Read(self, filename,directory=None):
        """
        Read Coefficients from CSV file
        
        :param directory=:  directory
        :param filename: filename
        :type directory=: str
        :type filename: str
    
        :Example:
        
        We have a CSV file called bcfile.csv in the working directory. 
        
        
        +----------+---------+--------+--------+---------+------------+
        |Label     | Value   | min    | Max    | ISConst | Desc       |
        +==========+=========+========+========+=========+============+
        |kbg       |    1    | 0.5    | 1      | 0       |  growth    |
        +----------+---------+--------+--------+---------+------------+    
        |kbm       | 0.001   | 0.0001 | .2     | 0       |   mortality| 
        +----------+---------+--------+--------+---------+------------+
        |kdd       |  1      |    0.05| 3      | 0       | depth mort |
        +----------+---------+--------+--------+---------+------------+   
        |Bcc       |   20    |        |        | 1       |carrying cap|
        +----------+---------+--------+--------+---------+------------+    
        |Ktg       | 0.9     | 0.5    | 15     | 0       |            | 
        +----------+---------+--------+--------+---------+------------+
        |Sopt      |  15     |        |        | 1       |opt salinity|
        +----------+---------+--------+--------+---------+------------+  
        |Ksg       |    8    | 6      | 15     | 0       |            |
        +----------+---------+--------+--------+---------+------------+    
        |Ksd       | 2.2     | 0.9    | 7      | 0       |            | 
        +----------+---------+--------+--------+---------+------------+
       
        
            >>> benthosCal = emlib.Calibration()
            >>> benthosCal.Read(bcfile.csv)
            INFO -243- New Calibration instance: 1
            DEBUG -351- C:1 Kbg 1.0
            DEBUG -351- C:2 Kbm 0.001
            DEBUG -351- C:3 Kdd 1.0
            DEBUG -351- C:4 Bcc 20.0
            DEBUG -351- C:5 Ktg 0.9
            DEBUG -351- C:6 Sopt 15.0
            DEBUG -351- C:7 Ksg 8.0
            DEBUG -351- C:8 Ksd 2.2
            INFO -272- imported C file
            
            
        """
        self.C = []
        if directory:
            self.dir = directory
        if filename:
            self.filename = filename
                
        myspamReader = csv.reader(open(os.path.join(self.dir, self.filename),'rb'), delimiter=',')
        firstline = next(myspamReader)

        for row in myspamReader:
            self.C.append(Coefficient(row[0],val=NuN(row[1]),min=NuN(row[2]),max=NuN(row[3]),isconst=NuN(row[4], Type=int),desc=row[5]))
        emlog.info('imported C file')
    def Add(self,label,val=None,min=None,max=None,isconst=None,desc=None):
        """
        Add a single coefficient to the calibration set
        """
        self.C.append(Coefficient(label,val,min,max,isconst,desc))

    def UpdateC(self,tag,val=None,min=None,max=None,isconst=None,desc=None):
        """
        Update an existing Coefficient in the calibration set
        """
        for i in self.C:
            if i.label == tag:
                if val:
                    i.var = val
                if min:
                    i.min = min
                if desc:
                    i.desc = desc
                if max:
                    i.max = max
                if isconst:
                    i.isconst = bool(isconst)
                break
                
        
            
    def SetCoeffs(self,Coeffs):
        """
        Copy coefficients from array
        """
        self.C = coeffs[:]

    def Write(self,directory=None,filename=None):
        """
        Write coefficients to CSV file.  Will overwrite contents if file exists.
        """
        if directory:
            self.dir = directory
        if filename:
            self.filename = filename
    
        f = open(self.dir+self.filename, 'wb')
        spamWriter = csv.writer(f, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        index = 0
        series = ["Label","Value","Min","Max","ISConst","Desc"]
        spamWriter.writerow(series)
    
        for i in self.C:
            spamWriter.writerow(i.Get())

        f.close()
        emlog.info('Saved C file')
    def Print(self):
        """
        Prints :class:`emlib.Calibration` structure to STDOUT
       
            >>> benthosCal.Print()
            Label	Value	Min	Max	ISConst	Desc
            Kbg 	1.0 	0.5 	1.0 	False   growth
            Kbm 	0.001 	0.0001 	0.2 	False   mortality 	
            Kdd 	1.0 	0.05 	3.0 	False 	depth mort
            Bcc 	20.0 	nan 	nan 	True 	carrying cap
            Ktg 	0.9 	0.5 	15.0 	False 	
            Sopt 	15.0 	nan 	nan 	True 	opt salinity
            Ksg 	8.0 	6.0 	15.0 	False 	
            Ksd 	2.2 	0.9 	7.0 	False 	

        """
        print "Label\tValue\tMin\tMax\tISConst\tDesc"
        for i in self.C:
            i.Print()
        

    def GetC(self,tag):
        """
        Return a single :class:`emlib.Coefficient` structure by label
        
        :param tag: Coefficient label
        :type tag: str
        
        :returns: Coefficient
        :rtype: emlib.Coefficient
        """
        for i in self.C:
            if i.label == tag:
                return i
    def Randomize(self):
        """
        Randomizes all coefficients that have **emlib.Coefficient.isconst** set to *False*
        
        .. seealso:: :class:`emlib.Coefficient.Randomize`
        """
        for i in self.C:
            i.Randomize()
        self.GF = []
    def Get(self):
        """
        Return a list of all :class:`emlib.Coefficient` objects.
        
        :returns: list of :class:`emlib.Coefficient`
        :rtype: list
        
        
        """
        tmp = []
        for i in self.C:
            tmp.append(i.var)
        return tmp
    def GetLabels(self):
        """
        Return list of all :class:`emlib.Coefficient` labels
        
        :returns: : list of labels 
        :rtype: list
        """
        tmp = []
        for i in self.C:
            tmp.append(i.label)
        return tmp
            
class Coefficient:
    """
    A single parameter coefficient.  
    
    :param label:     short description
    :param val=:     coefficient value
    :param min=:     minimum value
    :param max=:     maximum value
    :param isconst=:     is mutable coefficient?
    :param desc=:     Long description
    :type label:      str
    :type val=:      float
    :type min=:      float
    :type max=:      float
    :type isconst=:      bool
    :type desc=:      str
    
    """
    _count = 0
    def __init__(self,label,val=None,min=None,max=None,isconst=None,desc=None):
        self.__class__._count +=1
        self.label = label
        self.desc = desc
        self.var = val
        self.min = min
        self.max = max
        if isconst:
            self.isconst = bool(True)
        else:
             self.isconst = bool(False)
        self.input = 0
        self.index = 0
        self.ID = self.__class__._count
        emlog.debug("C:"+str(self.ID)+" " +self.label+" "+str(self.var))
    def Randomize(self):
        """
        Randomizes coefficient between :class:`emlib.Coefficient.min` and :class:`emlib.Coefficient.max` 
        using :func:`numpy.random.uniform`
        
        If **Coefficient.isconst** is *True* function returns without randomizing.
        
        .. note::  Why do we need a :mod:`boolean` value :class:`emlib.Coefficient.isconst`?  Even though :class:`emlib.Coefficient.min` and :class:`emlib.Coefficient.max`  could exist we may want to set this Coefficient to constant dynamically during a calibration algorithm.
        """
        if not self.isconst and (self.min and self.max) and (self.min <= self.max):
            self.var = np.random.uniform(self.min,self.max)
    def SetRange(self,min,max):
        """
        Reset our min and max allowable values for Coefficient.  This is useful for Monte Carlo algorithms that will tune each coefficient during the calibration process.
        
        :param min=:     minimum value
        :param max=:     maximum value
        :type min=:      float
        :type max=:      float
        
        """
        self.min=min
        self.max=max
    def Print(self):
        """
        Prints Coefficient structure to STDOUT.
        """
        print self.label,'\t',self.var,'\t',self.min,'\t',self.max,'\t',self.isconst,'\t',self.desc
    def Get(self):
        """
        Returns entire Coefficient structure as an array list.
        
        
        :returns: label,var,min,max,isconst,desc
        :rtype: list
        """
        return [self.label,self.var,self.min,self.max,self.isconst,self.desc]
    
            
  
class Observation:
    """
    A list of Observations to validate a model response
    
    """
    _count = 0
    def __init__(self,dirname,filename,value=None):
        self.__class__._count += 1
        self.label = value
        self.T = []
        self.X = []
        self.XM = []
        self.XE = []
        self.ID = self.__class__._count
        self.dir = dirname
        self.filename = filename
        if not dirname:
            self.dir = "" 
        myspamReader = csv.reader(open(os.path.join(self.dir, self.filename),'rb'), delimiter=',')
        firstline = next(myspamReader)

    
        if value:
            col = firstline.index(self.label)  #setup the value of interest
        else:
            col = 1
            self.value = firstline[1]
            logging.warn("Observation: No row specified assuming row[1]: "+firstline[1])

        emlog.debug("New OBS for value:"+str(self.label)+" COLMS:"+str(col)+" "+str(self.dir)+str(self.filename))
        emlog.debug(firstline)
        for row in myspamReader:
            date = mmddyyyy2date(row[0])
            if date in self.T:  # if we already have the same date then insert new obs
                if row[col] != '': #only insert if there is a value
                    self.X[len(self.T)-1].append(NuN(row[col]))
            else: #else we make a new obsT
                newlist = []
                if row[col] != '':
                    newlist.append(NuN(row[col]))
                    self.T.append(date)
                    self.X.append(newlist)
        for i in self.X:
            self.XM.append(np.mean(i))  #mean value table
            self.XE.append(np.std(i))   #stdev values
    

        emlog.info( "Read file "+dirname+filename+" "+str(len(self.X))+" Observations for value "+self.label)
    def Draw(self, block=True):
        """
        Plot Observations

        :param block: Blocking or non-blocking
        :type bool: bool

        Simple matplotlib plotting wrapper
        
        """
        plt.figure()
        plt.suptitle(self.filename)
        plt.plot(self.T,self.XM, 'ro', color='grey')
        plt.errorbar(self.T,self.XM, yerr=self.XE, color='grey',fmt='o', linewidth=1.4)
        plt.legend([self.label])
        plt.show(block=block)
    def Print(self, means=None):
        index = 0
        if means:
            for i in self.T:
                print i, self.XM[index], self.XE[index]
                index+=1
        else:
            for i in self.T:
                print i, self.X[index]
                index+=1

class TimeSeries:
    """
    A large series of data in time in a table.
    
    :param dirname: The ODE code function to be integrated.
    :param filename: Optional jacobian matrix
    :type dirname: str
    :type filename: str
 
    :returns: TimeSeries Object
    :rtype: emlib.TimeSeries
    
    
    This class object is the generic table structure EasyModeler uses
    to handle dtInput data and historical Observations via tables.
    
    EasyModeler 2 only supports comma separated value files *CSV*
    where the first row includes the header labels and first column is datetime 
    in the form mm/dd/yyyy.  Future planned expansions will increase this functionality.
    
    :Example:
    
    - You have a table of data in the form of a .CSV file stored as **/mydata/monthlyphysical.csv**. 
      Some of the cells may contain empty *Null* strings:
    
     +----------+---------+--------+
     |DATE      | SALINITY| TEMP   |
     +==========+=========+========+ 
     |01/20/2013| 30.2    | 22.5   |
     +----------+---------+--------+    
     |02/19/2013| 20.2    | 15.3   |
     +----------+---------+--------+   
     |03/20/2013|         |    24.2|
     +----------+---------+--------+   
    
    - Creating the TimeSeries object::
     
        >>> myData = TimeSeries(dirname="mydata",filename="monthlyphysical.csv")
        DEBUG -202- New INPUT table mydata\monthlyphysical.csv['DATE', 'SALINITY', 'TEMP']
        DEBUG -212- Saved 3 rows and 2 columns
        DEBUG -214- Converted dates to contiguous np.array
        DEBUG -216- Converted input data to contiguous np.array
        WARNING -218- Input data contains NaN values
     
    - EasyModeler separates time and data arrays as a design decision.  EasyModeler converts time to :mod:datetime objects.  To access the date array use the member **.T** ::
    
        >>> print myData.T
        [2013-01-20 2013-02-19 2013-3-20]
     
    :Missing Values:
    
    EasyModeler coverts blank *missing* values in data streams as :class:`numpy.nan` objects.  This is advantageous for plotting and numerical operations.
    Each non-date cell is passed to :func:`emlib.NuN` for conversion to :func:`float` values.
    
    .. seealso::  For more information about how :func:`emlib.NuN` handles empty strings and numerical conversions see it's documentation.
    
    
    """
    _count = 0
    def __init__(self,dirname=None,filename=None):
        self.__class__._count += 1
        self.ID = self.__class__._count
        emlog.info('New TimeSeries instance: '+str(self.ID))
        self.dir = dirname
        self.filename = filename
        self.labels = []
        if not dirname:
            self.dir = ""
        if filename:
            self._Read()
            
    def _Read(self, filename=None,directory=None):
        self.Rows = []
        self.labels = []
        self.T = []
        if directory:
            self.dir = directory
        if filename:
            self.filename = filename
                
        myspamReader = csv.reader(open(os.path.join(self.dir, self.filename),'rb'), delimiter=',')
        self.labels = next(myspamReader)
        emlog.debug("New INPUT table "+str(self.dir)+str(self.filename)+str(self.labels))
        for row in myspamReader:
            self.T.append(mmddyyyy2date(row[0]))
            myrow = []
            for i in range(len(self.labels)):
                if i == 0:
                    continue
                myrow.append(NuN(row[i]))
            self.Rows.append(myrow)
        del self.labels[0]
        emlog.debug("Saved "+str(len(self.T))+" rows and "+str(len(self.labels))+" columns")
        self.T = np.ascontiguousarray(self.T, dtype=object)
        emlog.debug("Converted dates to contiguous np.array")
        self.Rows = np.ascontiguousarray(self.Rows, dtype=object)
        emlog.debug("Converted input data to contiguous np.array")
        if np.isnan(np.sum(self.Rows)):
            emlog.warn("Input data contains NaN values")
    def Draw(self, block=True):
        """
        Plot TimeSeries

        :param block: Blocking or non-blocking
        :type bool: bool

        Simple matplotlib plotting wrapper
        
        """
        plt.figure()
        plt.plot(self.T,self.Rows)
        plt.legend(self.labels)
        plt.suptitle(self.filename)
        plt.show(block=block)
    def Print(self,column=None):
        """
        Prints entire TimeSeries, or column, to **STDOUT**.
        
        """
        if column:
            try:
                self.labels.index(column)
            except ValueError:
                emlog.warn(str(column)+" not in table. Try:"+str(self.labels))
                return
            col = self.labels.index(column)
            print "Date\t"+column
            for i in range((len(self.T))):
                print self.T[i],"\t",self.Rows[i][col]
        else:
            for i in range((len(self.T))):
                print self.T[i],"\t",self.Rows[i]
    def GetLabels(self):
        """
        Simple procedure to get array of string labels
        
        
        :returns: list
        :rtype: str
    
        :Example:
        
        - Simple print::
        
            >>> print myTable.GetLabels()
            ['SALINITY', 'TEMP']
         
        """
   
        return self.labels
    
    def Get(self,columnLabel):
        """
        Return a column as array.  
        
        :param columnLabel:  The column to return
        :type param: str
        
        
        :returns: list
        :rtype: float,np.Nan,str,...
    
        :Example:
        
        - Simple grab::
        
            >>> salinity =  myTable.Get("SALINITY")
         
         
        """
        try:
            self.labels.index(columnLabel)
        except ValueError:
            emlog.warn(str(columnLabel)+" not in table. Try:"+str(self.labels))
            return []
        col = self.labels.index(columnLabel)
        tmp = []
        for i in range((len(self.T))):
            tmp = self.Rows[i][col]
        return tmp

    
class Model:
    """
    Class method creates a new ODE model structure.


    :param ODEFunction: The ODE code function to be integrated.
    :param jacobian: Optional jacobian matrix
    :param algorithm: Optional integration algorithm, default *Vode*
    :param method: Optional algorithm method type, default *bdf*
    :param order: Optinal inegrator order, default *13*
    :param nsteps: Optional integrator internal steps, default *3000*
    :type ODEFunction1: Python function
    :type jacobian: jacobian array
    :type algorithm: str
    :type method: str
    :type order: int
    :type nsteps: int

    :returns: Model object
    :rtype: emlib.Model

    :Example:

     - First declare an ODE_INT function. This will be passed to the :func:`scipy.integrate.odeint` integrator::
    
        def LV_int(initial, t):
            x = initial[0]
            y = initial[1]
            A = 1
            B = 1
            C = 1
            D = 1

            x_dot = (A * x) - (B * x *y)
            y_dot = (D * x * y) - (C * y) 

            return [x_dot, y_dot]

     .. seealso:: For help creating ODE_INT functions see :mod:`scipy.integrate`
     .. warning:: Use logical operators with caution inside the ODE function.  Declaring a derivative *_dot* after a conditional will yield unpredictable results.

     - Pass the ODE function to :class:`emlib.Model`  as::

         >>> myModel = emlib.Model(LV_int)
    
    """
    _count = 0
    def __init__(self,ODEFunction,jacobian=None,algorithm=None,method=None,order=None,nsteps=None,dt=None):
       
        self.__class__._count += 1
        self.ID = self.__class__._count
        self.dt = 1
        self.myodesolve = scipy.integrate.ode(ODEFunction, jac=jacobian)
        emlog.info('New Model('+str(self.ID)+"): "+ODEFunction.__name__)
        if jacobian:
            emlog.debug('Jaccobian loaded')
        if method:
            self.method = method
        else:
            self.method = 'bdf'
        if algorithm:
            self.algorithm = algorithm
        else:
            self.algorithm = 'vode'
        if not method and not algorithm:
            emlog.info('No algorithm supplied assuming vode/bfd O12 Nsteps3000 dt1')
        if order:
            self.order = order
        else:
            self.order = 12
        if nsteps:
            self.nsteps = nsteps
        else:
            self.nsteps = 3000
        if dt:
            self.dt = dt
        else:
            self.dt = 1
        self.myodesolve.set_integrator(self.algorithm, method=self.method, order=self.order,nsteps=self.nsteps)
        emlog.debug('Integrator:'+self.algorithm+"/"+self.method+" order:"+str(self.order)+" nsteps:"+str(self.nsteps)+" dt:"+str(self.dt))
    def Integrate(self,initial,maxdt=None,Calibration=None,TimeSeries=None,start=None,end=None, dt=None):

        computed = []
        computedT = []
        
        self.myodesolve.set_initial_value(initial,0)
        emlog.debug("ODEINT Initials:"+"".join(map(str,initial)))

        if dt:
            self.dt = dt
        
        if TimeSeries and start:
            s = np.where(TimeSeries.T==start)
            
            if not s[0]:
                emlog.error("Supplied Start does not exist, assuming 0")
                s = 0
            else:
                s = s[0][0]
        else:
            s = 0

        if TimeSeries and end:
            e = np.where(TimeSeries.T==end)
            if not e[0]:
                e = len(TimeSeries.T)  - 1
                emlog.error("Supplied End does not exist, assuming "+str(TimeSeries.T[e]))
            else:
                e = e[0][0]
        if TimeSeries and maxdt:
            e = maxruns + s
            if e > len(TimeSeries.T)  - 1:
                e = len(TimeSeries.T)  - 1
                emlog.error("Maxruns > input ending, assuming "+str(TimeSeries.T[e]))
                
        if not TimeSeries:
            if maxdt:
                e = maxdt * int(1 / self.dt) + s
            else:
                emlog.error("No maxruns specified, exiting!")
                return 

        if TimeSeries:
            emlog.debug("Starting:"+str(TimeSeries.T[s])+" Ending:"+str(TimeSeries.T[e]))
            emlog.debug("Passing DtInput:"+str(TimeSeries.GetLabels()))
        else:
            emlog.debug("Ending in "+str(e)+" runs")

            
        if Calibration:
            emlog.debug("Passing Cs:"+str(Calibration.GetLabels()))
        
        tcount = 0
        for i in range(s,e,1):
        
            if TimeSeries and Calibration:
                self.myodesolve.set_f_params(TimeSeries.Rows[i],Calibration.Get())
        
            elif Calibration and not TimeSeries:
                self.myodesolve.set_f_params(Calibration.Get())
                
  
                
            
                
            self.myodesolve.integrate(self.myodesolve.t + self.dt)
            self.myodesolve.set_initial_value(self.myodesolve.y,self.myodesolve.t)
            if ((tcount % 500) == 0):
                emlog.debug( "Integration dT:"+str(tcount)+" of "+str(e - s)+" Remaining:"+str(e - s - tcount))
        
            tcount+=1
            if TimeSeries:
                computedT.append(TimeSeries.T[i])
            else:
                computedT.append(i)
            computed.append(self.myodesolve.y)
            
        
        self.computed = np.ascontiguousarray(computed)
        self.computedT = computedT
        emlog.debug("Completed Integration, created np.array shape:"+str(self.computed.shape))
        return
    def Draw(self, block=True,graph='ts',order=None):
        """
        Plot Computed Series

        :param block: Blocking or non-blocking
        :type bool: bool

        Simple matplotlib plotting wrapper
        
        """
        if graph == 'ts':
            plt.figure()
            plt.suptitle("Computed Integral")
            plt.plot(self.computedT,self.computed)
            plt.show(block=block)
            
        if graph == 'fp':
            plt.figure()
            plt.suptitle("Computed Integral")
            if order:
                plt.plot(self.computed[:,int(order[0])],self.computed[:,int(order[1])])
            else:
                plt.plot(self.computed[:,0],self.computed[:,1])
            plt.show(block=block)

        if graph == '3d':
            fig = plt.figure()

            fig = plt.figure()
            ax = Axes3D(fig)
            fig.suptitle("Computed Integral")
            if order:
                ax.plot(self.computed[:,int(order[0])],self.computed[:,int(order[1])],self.computed[:,int(order[2])],label="3D Plot")
            else:
                
                ax.plot(self.computed[:,0],self.computed[:,1],self.computed[:,2],label="3D Plot")
            plt.show(block=block)
    def Validate(self,Observation):
        """
        Validate model output to observed data

        :param Observation: The Observation class
        :type Observation: emlib.Observation
    
        :returns: fitness object
        :rtype: emlib.Fitness


        This function is a wrapper for the functions :func:`emlib.GFModel` and :func:`emlib.GFSingle` .
        Model simulation output is tested against historical Observations.  A series of Goodness of Fit statistics are returned as an :class:`emlib.Fitness` structure.
        
        :Example:
        
        >>> Model.Integrate(calibration.initial,
                             Calibration=calibration)

        .. note::  Model is assumed to be integrated via :func:`Model.Integrate` and results stored in Model.computed
         
        """
        fit = GFModel(self,Observation)
        return fit
    def Calibrate(self,Calibration,Observation,runs=None,TimeSeries=None,Algorithm=None,start=None,end=None):
        """
        Wrapper to calibrate model via supplied Monte Carlo algorithm.

        :param Calibration: Model Coefficients
        :type Calibration: emlib.Calibration
        :param Observation: What really happend
        :type Observation: emlib.Observation
        :param maxruns: Maximum times to integrate
        :type maxruns: int
        :param TimeSeries: Optional dtInput Table
        :type TimeSeries: emlib.TimeSeries
        :param Algorithm: Calibration Function
        :type Algorithm: **func**
        :param start: Optinal simulation start
        :type start: datetime.date,int
        :param end: optional simulation end
        :type end: datetime.date,int
        
        :returns: Model Calibration
        :rtype: emlib.Calibration       

        This function will integrate the current model *maxruns* times using the supplied **Algorithm**.  If no algorithm is supplied :func:`GF_BruteForceMSE` is assumed.

        :Example:

        >>> bestCalibration = Model.Calibrate(startingCalibration,
                                              Observation, runs=5000)

        .. note::  Supplying a large *maxruns* may hang the terminal while the calibrator executes.  Using CTRL+C will break out of the program but all progress calibrating will be lost.

        """
        if not Algorithm:
            emlog.warn("No fitness method provided, assuming GF_BruteForceMSE")
            return GF_BruteForceMSE(self,Calibration,Observation,runs,TimeSeries,start,end)
        else:
            emlog.info("Applying fitness function:"+str(Algorithm.__name__))
            return Algorithm(self,Calibration,Observation,runs,TimeSeries,start,end)     
        
def GF_BruteForceMSE(Model,Calibration,Observation,maxruns,TimeSeries=None,start=None,end=None):

    testingC = copy.deepcopy(Calibration)
    Model.Integrate(testingC.initial,Calibration=testingC, TimeSeries=TimeSeries, start=start, end=end)
    GF = Model.Validate(Observation)
    bestMSE = GF.MSE
    for i in range(maxruns-1):
        testingC.Randomize()
        Model.Integrate(testingC.initial,Calibration=testingC, TimeSeries=TimeSeries, start=start, end=end)
        GF = Model.Validate(Observation)
        if GF.MSE < bestMSE:
            emlog.info("New Best Calibration")
            Calibration = copy.deepcopy(testingC)
            bestMSE = GF.MSE
    return Calibration
        
def GF_BruteForceMSERANGE(Model,Calibration,Observation,maxruns,TimeSeries=None,start=None,end=None):

    testingC = copy.deepcopy(Calibration)
    Model.Integrate(testingC.initial,Calibration=testingC, TimeSeries=TimeSeries, start=start, end=end)
    GF = Model.Validate(Observation)
    bestMSE = GF.MSE
    bestRANGE = GF.RANGE
    for i in range(maxruns-1):
        testingC.Randomize()
        Model.Integrate(testingC.initial,Calibration=testingC, TimeSeries=TimeSeries, start=start, end=end)
        GF = Model.Validate(Observation)
        if (GF.MSE < bestMSE) and (GF.RANGE > bestRANGE) :
            emlog.info("New Best Calibration")
            Calibration = copy.deepcopy(testingC)
            bestMSE = GF.MSE
            GF.Print()
    return Calibration
        


class Fitness:
    """
    Goodness of Fit Structure
    
    
    :param fit: list of fitness measurements
    :type fit: list
    
    :Attributes:
    
    * *Fitness.matches*         Number of fitness values 
    * *Fitness.MSE*             Mean Square Error
    * *Fitness.WMSE*            Weighted Mean Square Error
    * *Fitness.RANGE*           % Inside STDEV
    * *Fitness.MSER*            Mean Square Error outside STDEV
    * *Fitness.O*               list of observed means
    * *Fitness.E*               list of expected values
        
    This is an internal :mod:`emlib` structure for housing Goodness of Fit statistics.
    """
    _count = 0
    def __init__(self,fit):
        self.__class__._count += 1
        self.ID = self.__class__._count
        #matches,MSE,WMSE,RANGE,MSER,O,E
        self.matches = fit[0]
        self.MSE = fit[1]
        self.WMSE = fit[2]
        self.RANGE = fit[3]
        self.MSER = fit[4]
        self.O = fit[5]
        self.E = fit[6]
        emlog.info("New fitness object:"+str(self.ID))
    def Print(self):
        """
        Print all statistics to STDOUT
        """
        print("GFMODEL #"+str(self.matches)+" MSE:"+str(self.MSE)+" RANGE%"+str(self.RANGE)+" MSER:"+str(self.MSER)+" WMSE:"+str(self.WMSE))



