# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska and Alejandro Chamorro-Chavez

This class holds the Simulated Annealing (SA) algorithm based on Kirkpatrick et al. (1983).
'''

from _algorithm import _algorithm
import time
import numpy as np

class sa(_algorithm):
    '''
    Implements the Simulated annealing algorithm.
    
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

    def check_par_validity(self,par):
        if len(par) == len(self.min_bound) and len(par) == len(self.max_bound):
            for i in range(len(par)):
                if par[i]<self.min_bound[i]: 
                    par[i]=self.min_bound[i]
                if par[i]>self.max_bound[i]:
                    par[i]=self.max_bound[i] 
        else:
            print 'ERROR: Bounds have not the same lenghts as Parameterarray'
        return par
    
    def sample(self,repetitions,Tini=80,Ntemp=50,alpha=0.99):
        """
        Samples from the MonteCarlo algorithm.
        
        Input
        ----------
        repetitions: int 
            Maximum number of runs.  
        """
        #Tini=80#repetitions/100
        #Ntemp=6
        self.min_bound, self.max_bound = self.find_min_max()
        stepsizes    = self.parameter()['step']
        starttime=time.time()
        intervaltime=starttime
        Eopt=999999
        Titer=Tini
        #vmin,vmax = self.find_min_max()        
        x=self.parameter()['optguess']
        Xopt = x        
        simulations=self.model(x)
        SimOpt=simulations
        Enew = self.likelihood(simulations,self.evaluation)
        Eopt = Enew
        self.datawriter.save(Eopt,Xopt,simulations=simulations)
        #k=(vmax-vmin)/self.parameter()['step']
        rep=0
        while (Titer>0.001*Tini and rep<repetitions):
                   
            for counter in range(Ntemp):
               
                if (Enew>Eopt):
                    #print 'Better'
                    Eopt=Enew
                    Xopt=x
                    SimOpt=simulations
                    Eopt=Enew
                    x=[]
                    for i in range(len(Xopt)):
                        #print Xopt
                        # Use stepsize provided for every dimension.
                        x.append(np.random.uniform(low=Xopt[i]-stepsizes[i], high=Xopt[i]+stepsizes[i]))
                        #x.append(fgener(Xopt[i], self.min_bound[i], self.max_bound[i], k))
                    x=self.check_par_validity(x)
                
                else:
                    accepted = frandom(Enew, Eopt, Titer)
                    if accepted==True:
                        #print Xopt
                        Xopt=x                        
                        SimOpt=self.model(x)
                        Eopt = self.likelihood(simulations,self.evaluation) 
                        x=[]
                        for i in range(len(Xopt)):
                            # Use stepsize provided for every dimension.
                            x.append(np.random.uniform(low=Xopt[i]-stepsizes[i], high=Xopt[i]+stepsizes[i]))
                            #x.append(fgener(Xopt[i], self.min_bound[i], self.max_bound[i], k))
                        x=self.check_par_validity(x)    
                    
                    else:
                        x=[]
                        for i in range(len(Xopt)):
                            #print Xopt
                            # Use stepsize provided for every dimension.
                            x.append(np.random.normal(loc=Xopt[i], scale=stepsizes[i]))
                            #x.append(fgener(Xopt[i], self.min_bound[i], self.max_bound[i], k))
                        x=self.check_par_validity(x)
              
                
                simulations=self.model(x)
                Enew = self.likelihood(simulations,self.evaluation)
                self.status(rep,Enew,Xopt) 
                self.datawriter.save(Eopt,Xopt,simulations=SimOpt)
                rep+=1        
                #Progress bar
                acttime=time.time()
                #Refresh progressbar every second
                if acttime-intervaltime>=2:
                    print '%i of %i (best like=%g)' % (rep,repetitions,self.status.likelihood)
                    intervaltime=time.time()
                
            Titer=alpha*Titer
        print '%i of %i (best like=%g)' % (rep,repetitions,self.status.likelihood)       
        self.datawriter.finalize()
        print 'Duration:'+str(round((acttime-starttime),2))+' s'
        data = self.datawriter.getdata()
        return data


def frandom(Enew, Eold, Titer):
    #dE=Enew-Eold
    dE=Eold-Enew
    accepted=False
    if (dE>0):
        P=np.exp(-(dE)/Titer)  # Boltzmann distr.
        rn=np.random.rand()   
                
        if (rn<=P):   # New configuration accepted
            #print 'accepted'
            accepted=True
    else:
        #print 'else'
        accepted=True
    return accepted
    
def fgener(param, vmin, vmax, k):         # random displacement
    rv=np.random.rand()
    k=10
    rd=2.0*(rv-0.5)*param/float(k)
    new=param+rd
    if (new<vmin):
        new=vmin
    if (new>vmax):
        new=vmax
    return new
