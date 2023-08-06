import sys
import datetime
import os

sys.path.insert(0, os.path.abspath('EasyModeler'))
import emlib


print emlib.NuN("4.5")

totest = "05/20/2013"
date = emlib.mmddyyyy2date(totest)
print date
print type(date)

def ODE():
    return
print emlib.Model(ODE)



def LV_int(t,initial,dtinput,constants):
        x = initial[0]
        y = initial[1]
        A = 1
        B = 1
        C = 1
        D = 1

        x_dot = (A * x) - (B * x *y)
        y_dot = (D * x * y) - (C * y) 

        return [x_dot, y_dot]
    
def LV2_int(t,initial,dtinput,constants):
        x = initial[0]
        y = initial[1]
        food = dtinput.Val("food")
        A = constants.Val("A")
        B = constants.Val("B")
        C = constants.Val("C")
        D = constants.Val("D")

        x_dot = (A * food* x) - (B * x *y)
        y_dot = (D * x * y) - (C * y) 

        return [x_dot, y_dot]


LV = emlib.Model(LV_int)

LV.Integrate([3,2],maxdt=20)
#LV.Draw()
LV.Integrate([3,2],maxdt=20, dt=.01)
#LV.Draw()



def Lorenz_int(t,initial,dtinput,constants):
        x = initial[0]
        y = initial[1]
        z = initial[2]
    
        sigma = constants.Val("Sigma")
        rho = constants.Val("Rho")
        beta = constants.Val("Beta")
        
        x_dot = sigma * (y - x)
        y_dot = x * (rho - z) - y
        z_dot = (x * y) - (beta* z)
        
        return [x_dot, y_dot, z_dot]

LZ = emlib.Model(Lorenz_int)


LZcalibration = emlib.Calibration()
LZcalibration.Add("Sigma",val=10,isconst=True)
LZcalibration.Add("Rho",val=99.96,min=10,max=100)
LZcalibration.Add("Beta",val=2,isconst=True)
LZcalibration.initial = [1,1,1]

print LZcalibration.Val("blah")



LZ.Integrate(LZcalibration.initial,Calibration=LZcalibration,maxdt=30,dt=.01)

#LZcalibration.UpdateC("Rho",val=16)



LZcalibration.Print()
#LZ.Integrate(LZcalibration.initial,Calibration=LZcalibration,maxdt=30,dt=.01)

#LZ.Draw()
#LZ.Draw(graph="fp")
#LZ.Draw(graph="fp", order=[0,1])
#LZ.Draw(graph="fp", order=[1,2])
#LZ.Draw(graph="fp", order=[0,2])

#LZ.Draw(graph="3d")

LVob = emlib.Observation("Hares",filename="LVdata.csv")
#sasseries = emlib.TimeSeries(filename="testsas.sas7bdat",fformat="sas")
#csvseries = emlib.TimeSeries(filename="testcsv.csv")
#sasob = emlib.Observation("salinity",filename="testsas.sas7bdat",fformat="sas")
#sasob = emlib.Observation("Cl_a___g_ltr_",filename="testcsv.csv")
LVtime = emlib.TimeSeries(filename="LVinput.csv")

LVob.Print()
#sasseries.Print()
#csvseries.Draw()
#sasob.Print()
#sasob.Draw()
#sasseries.Print()
#sasseries.Draw()

LVBEST = emlib.Calibration()
LVBEST.Add("A",val=.5,min=.01,max=.7)
LVBEST.Add("B",val=.02,min=.01,max=.07)
LVBEST.Add("C",val=.9,min=.5,max=1.0)
LVBEST.Add("D",val=.03,min=.01,max=.05)
LVBEST.initial = [30.0,4.0]


LVtest = emlib.Calibration()
LVtest.Add("A",val=.3,min=.1,max=.7)
LVtest.Add("B",val=.04,min=.01,max=.05)
LVtest.Add("C",val=.7,min=.5,max=1.0)
LVtest.Add("D",val=.04,min=.01,max=.05)
LVtest.initial = [30.0,4.0]

LVmodel = emlib.Model(LV2_int)

LVmodel.Integrate(LVBEST.initial,Calibration=LVBEST,TimeSeries=LVtime,dt=(1.0/12.0))

LVmodel.Validate(LVob,graph=True)
#LVob.Draw(block=False)

#LVmodel.Draw()

#best = LVmodel.Calibrate(LVtest,LVob,runs=500,TimeSeries=LVtime,dt=(1.0/12.0))

best.Print()
LVmodel.Integrate(LVtest.initial,Calibration=best,TimeSeries=LVtime,dt=(1.0/12.0))
LVmodel.Validate(LVob,graph=True)
