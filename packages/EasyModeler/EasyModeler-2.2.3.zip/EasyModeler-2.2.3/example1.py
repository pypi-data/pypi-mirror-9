import emlib

"""
Example 1. Lotka Volterra Predator Prey Interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""


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


LV = emlib.Model(LV_int)

LV.Integrate([3,2],maxdt=20)
LV.Draw()
LV.Integrate([3,2],maxdt=20, dt=.01)
LV.Draw()


