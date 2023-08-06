from emlowfuncs import *
import sys
import os
import copy
import csv
import numpy as np
import math
from scipy.integrate import odeint
import scipy
import logging
import datetime



class ModelCalibration:
    "A collection of parameters for a model"
    count = 0
    def __init__(self, coeffs=None, directory=None,filename=None):
        self.__class__.count +=1
        
        self.initial = []
        self.ID = self.__class__.count
        emlog.info('New ModelCalibration instance: '+str(self.ID))
        self.dir = directory
        self.filename = filename
        if not directory:
            self.dir = ""
        if filename:
            self.Load()
            
    def Load(self, filename=None,directory=None):
        self.C = []
        if directory:
            self.dir = directory
        if filename:
            self.filename = filename
                
        myspamReader = csv.reader(open(os.path.join(self.dir, self.filename),'rb'), delimiter=',')
        firstline = next(myspamReader)

        for row in myspamReader:
            self.C.append(Coefficient(row[0],val=NuN(row[1]),minval=NuN(row[2]),maxval=NuN(row[3]),const=NuN(row[4], Type=int),desc=row[5]))
        emlog.info('imported C file')
    def SetCoeffs(Coeffs):
        self.C = coeffs[:]

    def Save(self,directory=None,filename=None):
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
            spamWriter.writerow(i.Dump())

        f.close()
        emlog.info('Saved C file')
    def Print(self):
        print "Label\tValue\tMin\tMax\tISConst\tDesc"
        for i in self.C:
            i.Print()
        

    def GetSingleC(self,tag):
        for i in self.C:
            if i.label == tag:
                return i
    def Randomize(self):
        for i in self.C:
            i.Randomize()
        self.GF = []
    def GetCoefficients(self):
        tmp = []
        for i in self.C:
            tmp.append(i.var)
        return tmp
    def GetLabels(self):
        tmp = []
        for i in self.C:
            tmp.append(i.label)
        return tmp
            
class Coefficient:
    "A single Paramter Coefficient"
    _count = 0
    def __init__(self,mylabel,val=None,minval=None,maxval=None,const=None,desc=None):
        self.__class__._count +=1
        self.label = mylabel
        self.desc = desc
        self.var = val
        self.min = minval
        self.max = maxval
        if const:
            self.constant = const
        else:
             self.constant = 0
        self.input = 0
        self.index = 0
        self.ID = self.__class__._count
        emlog.debug("C:"+str(self.ID)+" " +self.label+" "+str(self.var))
    def Randomize(self):
        if not self.constant:
            self.var = np.random.uniform(self.min,self.max)
    def SetRange(self,minval,maxval):
        self.min=minval
        self.max=maxval
    def Print(self):
        print self.label,'\t',self.var,'\t',self.min,'\t',self.max,'\t',self.constant,'\t',self.desc
    def Dump(self):
        return [self.label,self.var,self.min,self.max,self.constant,self.desc]
    
            
  
class Observations:
    "Historical Observations"
    count = 0
    def __init__(self,dirname,filename,value=None):
        self.__class__.count += 1
        self.label = value
        self.T = []
        self.X = []
        self.XM = []
        self.XE = []
        self.ID = self.__class__.count
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
    

        emlog.info( "Read file "+dirname+filename+" "+str(len(self.X))+" observations for value "+self.label)
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
    "A series of data known as a table"
    count = 0
    def __init__(self,dirname=None,filename=None):
        self.__class__.count += 1
        self.ID = self.__class__.count
        emlog.info('New DataSeries instance: '+str(self.ID))
        self.dir = dirname
        self.filename = filename
        self.labels = []
        if not dirname:
            self.dir = ""
        if filename:
            self.Load()
            
    def Load(self, filename=None,directory=None):
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
    def Print(self,column=None):
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
        return self.labels
    
    def Get(self,column):
        try:
            self.labels.index(column)
        except ValueError:
            emlog.warn(str(column)+" not in table. Try:"+str(self.labels))
            return
        col = self.labels.index(column)
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

     - First declare an ODE_INT function. This will be passed to the **scipy.ODEINT** integrator::
    
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

     .. seealso:: For help creating ODE_INT functions see **SCIPY**
     .. warning:: Use logical operators with caution inside the ODE function.  Declaring a derivative *_dot* after a conditional will yield unpredicable results.

     - Pass the ODE function to the **emlib.Model** class::

         >>> myModel = emlib.Model(LV_int)
    
    """
    _count = 0
    def __init__(self,ODEFunction,jacobian=None,algorithm=None,method=None,order=None,nsteps=None):
       
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
            emlog.info('No algorithm supplied assuming vode/bfd O12 Nsteps3000')
        if order:
            self.order = order
        else:
            self.order = 12
        if nsteps:
            self.nsteps = nsteps
        else:
            self.nsteps = 3000
        self.myodesolve.set_integrator(self.algorithm, method=self.method, order=self.order,nsteps=self.nsteps)
        emlog.debug('Integrator:'+self.algorithm+"/"+self.method+" order:"+str(self.order)+" nsteps:"+str(self.nsteps))
    def Integrate(self,initial,maxdt=None,ModelCalibration=None,DataSeries=None,start=None,end=None):

        computed = []
        computedT = []
        
        self.myodesolve.set_initial_value(initial,0)
        emlog.debug("ODEINT Initials:"+"".join(map(str,initial)))
        
        
        if DataSeries and start:
            s = np.where(DataSeries.T==start)
            
            if not s[0]:
                emlog.error("Supplied Start does not exist, assuming 0")
                s = 0
            else:
                s = s[0][0]
        else:
            s = 0

        if DataSeries and end:
            e = np.where(DataSeries.T==end)
            if not e[0]:
                e = len(DataSeries.T)  - 1
                emlog.error("Supplied End does not exist, assuming "+str(DataSeries.T[e]))
            else:
                e = e[0][0]
        if DataSeries and maxdt:
            e = maxruns + s
            if e > len(DataSeries.T)  - 1:
                e = len(DataSeries.T)  - 1
                emlog.error("Maxruns > input ending, assuming "+str(DataSeries.T[e]))
                
        if not DataSeries:
            if maxdt:
                e = maxdt + s
            else:
                emlog.error("No maxruns specified, exiting!")
                return 

        if DataSeries:
            emlog.debug("Starting:"+str(DataSeries.T[s])+" Ending:"+str(DataSeries.T[e]))
            emlog.debug("Passing DtInput:"+str(DataSeries.GetLabels()))
        else:
            emlog.debug("Ending in "+str(e)+" runs")

            
        if ModelCalibration:
            emlog.debug("Passing Cs:"+str(ModelCalibration.GetLabels()))
        
        tcount = 0
        for i in range(s,e,1):
        
            if DataSeries and ModelCalibration:
                self.myodesolve.set_f_params(DataSeries.Rows[i],ModelCalibration.GetCoefficients())
        
            elif ModelCalibration and not DataSeries:
                self.myodesolve.set_f_params(ModelCalibration.GetCoefficients())
                
  
                
                
            self.myodesolve.integrate(self.myodesolve.t + self.dt)
            self.myodesolve.set_initial_value(self.myodesolve.y,self.myodesolve.t)
            if ((tcount % 500) == 0):
                emlog.debug( "Integration dT:"+str(tcount)+" of "+str(e - s)+" Remaining:"+str(e - s - tcount))
        
            tcount+=1
            if DataSeries:
                computedT.append(DataSeries.T[i])
            else:
                computedT.append(i)
            computed.append(self.myodesolve.y)
            
        
        self.computed = np.ascontiguousarray(computed)
        self.computedT = computedT
        emlog.debug("Completed Integration, created np.array shape:"+str(self.computed.shape))
        return
    def Fitness(self,Observations):
        """
        Runs Goodness of Fit metrics using supplied Observations

        :param Observations: The Observation class
        :type Observations: emlib.Observations
    
        :returns: fitness object
        :rtype: emlib.Fitness


        This function is a wrapper for the functions :func:`emlib.GFModel` and :func:`emlib.GFSingle` .
        Model simulation output is tested against historical observations.  A series of Goodness of Fit statistics are returned as an :class:`emlib.Fitness` structure.
        
        :Example:
        
        >>> Model.Integrate(calibration.initial,
                             ModelCalibration=calibration)

        .. note::  Model is assumed to be integrated via :func:`Model.Integrate` and results stored in Model.computed
         
        """
        fit = Fitness(GFModel(self,Observations))
        return fit
    def Calibrate(self,Calibration,Observations,runs=None,DataSeries=None,Algorithm=None,start=None,end=None):
        """
        Wrapper to calibrate model via supplied algorithm.

        :param Calibration: Model Coefficients
        :type Calibration: emlib.ModelCalibration
        :param Observations: What really happend
        :type Observations: emlib.Observations
        :param maxruns: Maximum times to integrate
        :type maxruns: int
        :param DataSeries: Optional dtInput Table
        :type DataSeries: emlib.TimeSeries
        :param Algorithm: Calibration Function
        :type Algorithm: **func**
        :param start: Optinal simulation start
        :type start: datetime.date,int
        :param end: optional simulation end
        :type end: datetime.date,int
        
        :returns: Model Calibration
        :rtype: emlib.ModelCalibration       

        This function will integrate the current model *maxruns* times using the supplied **Algorithm**.  If no algorithm is supplied :func:`GF_BruteForceMSE` is assumed.

        :Example:

        >>> bestCalibration = Model.Calibrate(startingCalibration,
                                              Observations, runs=5000)

        .. note::  Supplying a large *maxruns* may hang the terminal while the calibrator executes.  Using CTRL+C will break out of the program but all progress calibrating will be lost.

        """
        if not Algorithm:
            emlog.warn("No fitness method provided, assuming GF_BruteForceMSE")
            return GF_BruteForceMSE(self,Calibration,Observations,runs,DataSeries,start,end)
        else:
            emlog.info("Applying fitness function:"+str(Algorithm.__name__))
            return Algorithm(self,Calibration,Observations,runs,DataSeries,start,end)     
        
def GF_BruteForceMSE(Model,Calibration,Observations,maxruns,DataSeries=None,start=None,end=None):

    testingC = copy.deepcopy(Calibration)
    Model.Integrate(testingC.initial,ModelCalibration=testingC, DataSeries=DataSeries, start=start, end=end)
    GF = Model.Fitness(Observations)
    bestMSE = GF.MSE
    for i in range(maxruns-1):
        testingC.Randomize()
        Model.Integrate(testingC.initial,ModelCalibration=testingC, DataSeries=DataSeries, start=start, end=end)
        GF = Model.Fitness(Observations)
        if GF.MSE < bestMSE:
            emlog.info("New Best Calibration")
            Calibration = copy.deepcopy(testingC)
            bestMSE = GF.MSE
    return Calibration
        
def GF_BruteForceMSERANGE(Model,Calibration,Observations,maxruns,DataSeries=None,start=None,end=None):

    testingC = copy.deepcopy(Calibration)
    Model.Integrate(testingC.initial,ModelCalibration=testingC, DataSeries=DataSeries, start=start, end=end)
    GF = Model.Fitness(Observations)
    bestMSE = GF.MSE
    bestRANGE = GF.RANGE
    for i in range(maxruns-1):
        testingC.Randomize()
        Model.Integrate(testingC.initial,ModelCalibration=testingC, DataSeries=DataSeries, start=start, end=end)
        GF = Model.Fitness(Observations)
        if (GF.MSE < bestMSE) and (GF.RANGE > bestRANGE) :
            emlog.info("New Best Calibration")
            Calibration = copy.deepcopy(testingC)
            bestMSE = GF.MSE
            GF.Print()
    return Calibration
        


class Fitness:
    "Goodness of Fit object"
    count = 0
    def __init__(self,fit):
        self.__class__.count += 1
        self.ID = self.__class__.count
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
        print("GFMODEL #"+str(self.matches)+" MSE:"+str(self.MSE)+" RANGE%"+str(self.RANGE)+" MSER:"+str(self.MSER)+" WMSE:"+str(self.WMSE))


