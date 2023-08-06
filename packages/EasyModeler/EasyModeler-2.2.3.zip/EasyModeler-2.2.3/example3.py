import emlib

"""
Example 3. Lotka Volterra with dtInput
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""


def LV2_int(t,initial,dtinput,constants):
    x = initial[0]
    y = initial[1]
    food = dtinput.Val("food")
    A = 1
    B = 1
    C = 1
    D = 1

    x_dot = (A * food* x) - (B * x *y)
    y_dot = (D * x * y) - (C * y) 

    return [x_dot, y_dot]

LVmodel = emlib.Model(LV2_int)

LVtime = emlib.TimeSeries(filename="LVinput.csv")


LVmodel.Integrate([3,2],TimeSeries=LVtime)

LVmodel.Draw()
