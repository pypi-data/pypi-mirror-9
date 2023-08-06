'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

This example implements the Griewank function into SPOT.	
'''

import numpy as np
import spotpy

class spot_setup(object):
    def __init__(self):
        self.dim=2
        
    def parameters(self):
        pars = []   #distribution of random value      #name  #stepsize# optguess
        for i in range(self.dim):        
            pars.append((np.random.uniform(low=-50,high=50),  str(i),   5.5,  -20.0))        
        #pars.append((np.random.uniform(low=-20,high=20),  'y',    2.5,   4.0))
        dtype=np.dtype([('random', '<f8'), ('name', '|S30'),('step', '<f8'),('optguess', '<f8')])
        return np.array(pars,dtype=dtype)
                
  
    def simulation(self, vector):
        n = len(vector)
        fr = 4000
        s = 0
        p = 1
        for j in range(n): 
            s = s+vector[j]**2
        for j in range(n): 
            p = p*np.cos(vector[j]/np.sqrt(j+1))
        simulation = [s/fr-p+1]
        return simulation     
     
     
     
    def evaluation(self):
        observations=[0]
        return observations
    
    def likelihood(self,simulation,evaluation):
        likelihood= -spotpy.likelihoods.rmse(simulation,evaluation)
        return likelihood