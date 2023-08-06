from setuptools import setup

setup(name='EasyModeler',
      version='2.1.9',
      description='Simple ODE Tools for Modelers',
      url='https://bitbucket.org/evanleeturner/easymodel',
      author='Evan L Turner',
      author_email='evanlee.turner@gmail.com',
      license='BSD',
      packages=['emlib'],
      requires=['SciPy','NumPy'],
      keywords='EasyModel,GCOOS,ODE,SciPy,ODEINT,calibration',
      classifiers=[
			'Development Status :: 4 - Beta',
			'Environment :: Console',
			'Intended Audience :: Science/Research',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
			'Topic :: Scientific/Engineering :: Mathematics',
			'Topic :: Scientific/Engineering :: Visualization',
			'Topic :: Utilities'
		],
      zip_safe=False)
