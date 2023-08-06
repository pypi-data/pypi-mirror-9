`EasyModeler` is a package for calibration and 
simulation of ODEs using Scipy's ODEINT

URL
---
* http://pypi.python.org/pypi/EasyModeler


Requirements
------------
* Python 2.6
* SciPy and NumPy 2.6

Features
--------
* ODEINT Wrapper        Intelligent non-invasive wrapper to Scipy's integrator
* ODE Calibration       Auto-calibrate a series of ODEs
* TimeSeries Files      Handling of dtInput
* Model Validation      Validate using Goodness of Fit statistics


Documentation
-------------
*  Supports comprehensive autodocs with example usage inside source
*  Looking for a permanent document home online *please suggest ideas to me!*


Install as python module
------------------------
from internet
~~~~~~~~~~~~~
::

   $ easy_install easymodeler

from archive
~~~~~~~~~~~~
::

   $ unzip easymodeler-x.x.x.zip
   $ cd easymodler-x.x.x
   $ python setup.py install


Change Log
----------
2.1.2 (2015-3-6)
~~~~~~~~~~~~~~~~~~
* autodocs continue to update
* README change
* Userguide inclusion
* LICENSE

2.1.1 (2015-3-6)
~~~~~~~~~~~~~~~~~~
* autodocs continue to update
* package module hierarchy altered


User Guide
----------
`EasyModler` is a package for calibration and 
simulation of Ordinary Differential Equations *ODEs* built on :mod:`scipy.odeint`  

Lotka Volterra Predator Prey Interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lotka Volterra system is a simple model of predator-prey dynamics and consists of two coupled differentials. http://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equation

This is a simple example highlighting **EasyModler's** ability to integrate ODEs without complication! At a minimum to integrate we require::

1.  An defined ODE function

2.  A set of initial conditions as a list

3.  Number of times to run the integrator


- Declare an ODE_INT function in your source code. This will be passed to the :func:`scipy.integrate.odeint` integrator::
    
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



- Pass the ODE function to :class:`emlib.Model`  as::

    >>> LV = emlib.Model(LV_int)
    INFO -512- New Model(1): LV_int
    INFO -524- No algorithm supplied assuming vode/bfd O12 Nsteps3000
    
- Now lets integrate our LV function for 200 timesteps!

    >>> LV.Integrate([1,1],maxdt=200)
    DEBUG -541- ODEINT Initials:11
    DEBUG -579- Ending in 200 runs
    DEBUG -600- Integration dT:0 of 200 Remaining:200
    DEBUG -612- Completed Integration, created np.array shape:(200, 2)
  
- The model output is stored in the :class:`emlib.Model` object as arrays *computedT* and *computed*

    >>> print LV.computed
    [[ 0.37758677  2.93256414]
    [ 0.13075395  1.32273451]
    [ 0.14707288  0.55433421]
    [ 0.27406944  0.24884565]
    ...
    

**EasyModeler** is organized where time is stored separately from data.  This is a design feature to aid processing timeseries data. This will become more relevant as we integrate more complex systems.

-  Lets graph the results of Lotka Volterra instead of printing a table!  EasyModeler contains built-in plotting of structures using the :mod:`matplotlib` module.

.. note:: Plotting feature coming in version 2.2!

Lorenz System
~~~~~~~~~~~~~

The Lorenz system is a series of three differentials that were described by Edward Lorenz.  http://en.wikipedia.org/wiki/Lorenz_system This system is a great example of the power of coefficients!  
In this example we will delve into the EasyModeler :mod:`emlib` package to manage passing constants, or *coefficients* to our ODE function.

- Declare the Lorenz ODE function and create an :class:`emlib.Model` object.  However, we will now pass another list structure to our define which will become our coefficients::

    def Lorenz_int(t,initial,constants):
        x = initial[0]
        y = initial[1]
        z = initial[2]
    
        sigma = constants[0]
        rho = constants[1]
        beta = constants[2]
        
        x_dot = sigma * (y - x)
        y_dot = x * (rho -z) - y
        z_dot = x * y - beta* z
        
        return [x_dot, y_dot, z_dot]
    
- Initialize the model::


    >>> LZ = emlib.Model(Lorenz_int)
    INFO -512- New Model(1): LZ_int
    INFO -524- No algorithm supplied assuming vode/bfd O12 Nsteps3000


