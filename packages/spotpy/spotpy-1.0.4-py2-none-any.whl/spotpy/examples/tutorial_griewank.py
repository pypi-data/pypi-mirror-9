# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This class holds the example code from the Griewank tutorial web-documention.
'''

import spotpy
#from spot_setup_griewank import spot_setup
#from spot_setup_rosenbrock import spot_setup
from spot_setup_ackley import spot_setup

from spotpy import analyser

#Create samplers for every algorithm:
results=[]
spot_setup=spot_setup()
rep=5000

#sampler=spotpy.algorithms.mc(spot_setup,    dbname='GriewankMC',    dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.lhs(spot_setup,   dbname='GriewankLHS',   dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.mle(spot_setup,   dbname='GriewankMLE',   dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.mcmc(spot_setup,  dbname='GriewankMCMC',  dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.sceua(spot_setup, dbname='GriewankSCEUA', dbformat='csv')
#sampler.sample(rep,ngs=4)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.sa(spot_setup,    dbname='GriewankSA',    dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.demcz(spot_setup, dbname='GriewankDEMCz', dbformat='csv')
#sampler.sample(rep,nChains=20,convergenceCriteria=1.1)
#results.append(sampler.getdata())
#
#sampler=spotpy.algorithms.rope(spot_setup,  dbname='GriewankROPE',  dbformat='csv')
#sampler.sample(rep)
#results.append(sampler.getdata())

sampler=spotpy.algorithms.fast(spot_setup,  dbname='RosenFAST',  dbformat='csv')
sampler.sample(rep)
results.append(sampler.getdata())

#algorithms=['MC','LHS','MLE','MCMC','SCEUA','SA','DEMCz','ROPE']
#results=[]
#for algorithm in algorithms:
#    results.append(spotpy.analyser.load_csv_results('Griewank'+algorithm))


evaluation = spot_setup.evaluation()

#spotpy.analyser.plot_heatmap_griewank(results,algorithms)
#spotpy.analyser.plot_parametertrace_algorithms(results,algorithmnames=algorithms)