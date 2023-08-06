import emlib


"""
Example2. Lorenz Chaotic System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



"""


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

LZ.Integrate(LZcalibration.initial,Calibration=LZcalibration,maxdt=30,dt=.01)

LZ.Draw()
LZ.Draw(graph="3d")
