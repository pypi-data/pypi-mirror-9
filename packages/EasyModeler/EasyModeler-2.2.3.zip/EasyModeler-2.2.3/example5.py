import emlib
import logging
"""
Example 5. Lotka Volterra Calibration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
emlib.emlog.setLevel(logging.INFO)

def LV3_int(t,initial,dtinput,constants):
    x = initial[0]
    y = initial[1]
    A = constants.Val("A")
    B = constants.Val("B")
    C = constants.Val("C")
    D = constants.Val("D")

    x_dot = (A * x) - (B * x *y)
    y_dot = (D * x * y) - (C * y) 

    return [x_dot, y_dot]



hares = emlib.Observation("Hares",filename="LVdata.csv")


LVmodel = emlib.Model(LV3_int)

LVtest = emlib.Calibration()
LVtest.Add("A",val=.3,min=.01,max=.7)
LVtest.Add("B",val=.04,min=.01,max=.07)
LVtest.Add("C",val=.6,min=.5,max=1.0)
LVtest.Add("D",val=.04,min=.01,max=.05)
LVtest.initial = [30.0,4.0]

LVtime = emlib.TimeSeries(filename="LVinput.csv")
LVmodel.Integrate(LVtest.initial,Calibration=LVtest,TimeSeries=LVtime,dt=(1.0/12.0))
LVmodel.Validate(hares,graph=True)
LVmodel.fit.Print()

best = LVmodel.Calibrate(LVtest,hares,runs=500,TimeSeries=LVtime,dt=(1.0/12.0))

best.Print()
LVmodel.Integrate(LVtest.initial,Calibration=best,TimeSeries=LVtime,dt=(1.0/12.0))
LVmodel.Validate(hares,graph=True)
LVmodel.fit.Print()
