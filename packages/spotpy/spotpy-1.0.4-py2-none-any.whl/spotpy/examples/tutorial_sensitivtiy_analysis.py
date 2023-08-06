# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This class holds the example code from the FAST tutorial web-documention.
'''

import spotpy
#from spot_setup_griewank import spot_setup
from spot_setup_rosenbrock import spot_setup
#from spot_setup_ackley import spot_setup

#Create samplers for every algorithm:
results=[]
spot_setup=spot_setup()
rep=5000

sampler=spotpy.algorithms.fast(spot_setup,  dbname='AckleyFAST',  dbformat='csv')
sampler.sample(rep)