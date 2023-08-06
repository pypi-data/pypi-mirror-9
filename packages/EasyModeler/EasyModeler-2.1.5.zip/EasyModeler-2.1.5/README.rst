EasyModeler is a package for calibration and 
simulation of ODEs using SciPy and NumPy

URL
---
* Coming soon once I find a good document host!


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
* Supports comprehensive autodocs with example usage inside source
* Looking for a permanent document home online *please suggest ideas to me!*


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
2.1.4 - 2.1.5 (2015-3-7)
~~~~~~~~~~~~~~~~~~~~~~~~
* trying yet again to fix the pypi readme
* autodocs continue to update
* rename functions to naming conventions


2.0.0 - 2.1.3 (2015-3-6)
~~~~~~~~~~~~~~~~~~~~~~~~
* autodocs continue to update
* README change
* Sample Example
* LICENSE


Sample Usage
------------

Lotka Volterra Predator Prey Interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Lotka Volterra system is a simple model of predator-prey dynamics and consists of two coupled differentials. http://en.wikipedia.org/wiki/Lotka%E2%80%93Volterra_equation

This is a simple example highlighting **EasyModler's** ability to integrate ODEs without complication! At a minimum to integrate we require:

1. An defined ODE function

2. A set of initial conditions as a list

3. Number of times to run the integrator


Declare an ODE_INT function in your source code. This will be passed to the **scipy.integrate.odeint** integrator

::
    
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



Pass the ODE function to **emlib.Model**  as

::

    >>> import emlib
    >>> LV = emlib.Model(LV_int)
    INFO -512- New Model(1): LV_int
    INFO -524- No algorithm supplied assuming vode/bfd O12 Nsteps3000
    
Now lets integrate our LV function for 200 timesteps!

::

    >>> LV.Integrate([1,1],maxdt=200)
    DEBUG -541- ODEINT Initials:11
    DEBUG -579- Ending in 200 runs
    DEBUG -600- Integration dT:0 of 200 Remaining:200
    DEBUG -612- Completed Integration, created np.array shape:(200, 2)
  
The model output is stored in the **emlib.Model** object as arrays *computedT* and *computed*

::

    >>> print LV.computed
    [[ 0.37758677  2.93256414]
    [ 0.13075395  1.32273451]
    [ 0.14707288  0.55433421]
    [ 0.27406944  0.24884565]
    

**EasyModeler** is organized where time is stored separately from data.  
This is a design feature to aid processing timeseries data. 

