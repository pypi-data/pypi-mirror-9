# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This class holds the LatinHyperCube algorithm based on McKay et al. (1979).
'''

from _algorithm import _algorithm
import numpy as np
import random
import time

class lhs(_algorithm):
    '''
    Implements the LatinHyperCube algorithm.
    
    Input
    ----------
    spot_setup: class
        model: function 
            Should be callable with a parameter combination of the parameter-function 
            and return an list of simulation results (as long as evaluation list)
        parameter: function
            When called, it should return a random parameter combination. Which can 
            be e.g. uniform or Gaussian
        likelihood: function 
            Should return the likelihood for a given list of a model simulation and 
            observation.
        evaluation: function
            Should return the true values as return by the model.
            
    dbname: str
        * Name of the database where parameter, likelihood value and simulation results will be saved.
    
    dbformat: str
        * ram: fast suited for short sampling time. no file will be created and results are saved in an array.
        * csv: A csv file will be created, which you can import afterwards.        

    parallel: str
        * seq: Sequentiel sampling (default): Normal iterations on one core of your cpu.
        * mpi: Message Passing Interface: Parallel computing on cluster pcs (recommended for unix os).
        
    save_sim: boolean
        *True:  Simulation results will be saved
        *False: Simulationt results will not be saved
     '''
    def __init__(self, spot_setup, dbname='test', dbformat='ram', parallel='seq',save_sim=True):

        _algorithm.__init__(self,spot_setup, dbname=dbname, dbformat=dbformat, parallel=parallel,save_sim=save_sim)

    def find_min_max(self):
        randompar=self.parameter()['random']        
        for i in range(1000):
            randompar=np.column_stack((randompar,self.parameter()['random']))
        return np.amin(randompar,axis=1),np.amax(randompar,axis=1)
        
    def sample(self, repetitions):
        """
        Samples from the LatinHypercube algorithm.
        
        Input
        ----------
        repetitions: int 
            Maximum number of runs.  
        """
        print 'Creating LatinHyperCube Matrix'
        #Get the names of the parameters to analyse
        names     = self.parameter()['name']
        #Define the jump size between the parameter
        segment   = 1/float(repetitions)
        #Get the minimum and maximum value for each parameter from the distribution
        parmin,parmax=self.find_min_max()
        
        #Create an Matrix to store the parameter sets
        Matrix=np.empty((repetitions,len(parmin)))      
        #Create the LatinHypercube Matrix as in McKay et al. (1979):
        for i in range(int(repetitions)):
            segmentMin     = i * segment
            pointInSegment = segmentMin + (random.random() * segment)
            parset=pointInSegment *(parmax-parmin)+parmin                            
            Matrix[i]=parset
        for i in range(len(names)):
            random.shuffle(Matrix[:,i])
        
        
        print 'Start sampling'
        starttime=time.time()
        intervaltime=starttime
        # A generator that produces the parameters
        #param_generator = iter(Matrix)
        param_generator = ((rep,list(Matrix[rep])) for rep in xrange(int(repetitions)-1))        
        for rep,randompar,simulations in self.repeat(param_generator):        
            #Calculate the objective function
            like        = self.likelihood(simulations,self.evaluation)
            self.status(rep,like,randompar)
            #Save everything in the database
            self.datawriter.save(like,randompar,simulations=simulations)
            #Progress bar
            acttime=time.time()
            #Refresh progressbar every second
            if acttime-intervaltime>=2:
                print '%i of %i (best like=%g)' % (rep,repetitions,self.status.likelihood)
                intervaltime=time.time()        
        self.repeat.terminate()
        
        self.datawriter.finalize()
        print '%i of %i (best like=%g)' % (self.status.rep,repetitions,self.status.likelihood)
        print 'Duration:'+str(round((acttime-starttime),2))+' s'
