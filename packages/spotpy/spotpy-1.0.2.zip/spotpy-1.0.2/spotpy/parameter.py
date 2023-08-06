# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Philipp Kraft

Contains classes to generate random parameter sets
'''
import numpy.random as rnd
import numpy as np

class Base(object):
    """
    This is a universal random parameter class
    
    
    TODO: Tobi needs to explain this better
    """
    def __init__(self,name,rndfunc,rndargs,step,optguess):
        """
        :name: Name of the parameter
        :rndfunc: Function to draw a random number, eg. the random functions from numpy.random
        :rndargs: Argument-tuple for the random function, eg. lower and higher bound 
                  (number and meaning of arguments depends on the function)
        :step:  Some algorithms, eg. mcmc need a parameter of the variance for the next step
        :optguess: Some algorithms depend on a good start point, this is given by optguess

        """
        self.name =name
        self.rndfunc = rndfunc
        self.rndargs = rndargs
        self.step = step
        self.optguess = optguess
    def __call__(self):
        """
        Returns a pparameter realization
        """
        return self.rndfunc(*self.rndargs)
    def astuple(self):
        """
        Returns a tuple of a realization and the other parameter properties
        """
        return self(),self.name,self.step,self.optguess

class Uniform(Base):
    """
    A specialization of the Base parameter for uniform distributions
    
    """
    def __init__(self,name,low,high,step=None,optguess=None):
        """
        :name: Name of the parameter
        :low: lower bound of the uniform distribution
        :high: higher bound of the uniform distribution
        :step: Step size for mcmc like alg. If None, 0.1 * (high-low) is used
        :optguess: First guess of optimum for mcmc like alg. If None, mean(low,high) is used 
        """
        Base.__init__(self,name,rnd.uniform,(low,high),None,None)
        self.step = step or 0.1 * (high-low)
        self.optguess = optguess or 0.5*(low+high)

class Normal(Base):
    """
    A specialization of the Base parameter for normal distributions
    """
    def __init__(self,name,mean,stddev,step=None,optguess=None):
        """
        :name: Name of the parameter
        :mean: center of the normal distribution
        :stddev: variance of the normal distribution
        :step: Step size for mcmc like alg. If None, 0.1 * (high-low) is used
        :optguess: First guess of optimum for mcmc like alg. If None, mean(low,high) is used 
        """

        Base.__init__(self,name,rnd.normal,(mean,stddev),None,None)
        self.step = step or 0.5 * stddev
        self.optguess = optguess or mean
    

def generate(parameters):
    """
    This function generates a parameter set from a list of parameter objects. The parameter set
    is given as a structured array in the format the parameters function of a setup expects
    
    :parameters: A sequence of parameter objects
    """
    dtype=[('random', '<f8'), ('name', '|S30'),('step', '<f8'),('optguess', '<f8')]
    return np.fromiter((param.astuple() for param in parameters),dtype=dtype,count=len(parameters))
        