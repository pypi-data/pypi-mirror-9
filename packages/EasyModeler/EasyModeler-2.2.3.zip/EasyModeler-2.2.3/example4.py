import emlib

"""
Example 4. Lotka Volterra Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""


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

LVBEST = emlib.Calibration()
LVBEST.Add("A",val=.5)
LVBEST.Add("B",val=.02)
LVBEST.Add("C",val=.9)
LVBEST.Add("D",val=.03)
LVBEST.initial = [30.0,4.0]

LVtime = emlib.TimeSeries(filename="LVinput.csv")
LVmodel.Integrate(LVBEST.initial,Calibration=LVBEST,TimeSeries=LVtime,dt=(1.0/12.0))
LVmodel.Validate(hares,graph=True)

