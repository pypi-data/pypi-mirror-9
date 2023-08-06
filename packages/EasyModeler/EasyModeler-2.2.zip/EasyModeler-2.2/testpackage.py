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



def LV_int(t,initial):
        x = initial[0]
        y = initial[1]
        A = 1
        B = 1
        C = 1
        D = 1

        x_dot = (A * x) - (B * x *y)
        y_dot = (D * x * y) - (C * y) 

        return [x_dot, y_dot]


LV = emlib.Model(LV_int)

LV.Integrate([3,2],maxdt=20)
#LV.Draw()
LV.Integrate([3,2],maxdt=20, dt=.01)
#LV.Draw()



def Lorenz_int(t,initial,constants):
        x = initial[0]
        y = initial[1]
        z = initial[2]
    
        sigma = constants[0]
        rho = constants[1]
        beta = constants[2]
        
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

LZ.Integrate(LZcalibration.initial,Calibration=LZcalibration,maxdt=10,dt=.01)

LZcalibration.UpdateC("Rho",val=16)



LZcalibration.Print()
#LZ.Integrate(LZcalibration.initial,Calibration=LZcalibration,maxdt=30,dt=.01)

#LZ.Draw(graph="ts")
#LZ.Draw(graph="fp")
#LZ.Draw(graph="fp", order=[0,1])
#LZ.Draw(graph="fp", order=[1,2])
#LZ.Draw(graph="fp", order=[0,2])

#LZ.Draw(graph="3d")
