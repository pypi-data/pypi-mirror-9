# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska and Alejandro Chamorro-Chavez

This class holds the Robust Parameter Estimation (ROPE) algorithm based on Bárdossy and Singh (2008).
'''

from _algorithm import _algorithm
import time
import numpy as np

class rope(_algorithm):
    '''
    Implements the Robust Parameter Estimation (ROPE) algorithm (Bárdossy and Singh, 2008)
    
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
        * mpc: Multi processing: Iterations on all available cores on your cpu (recommended for windows os).
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

    def create_par(self,min_bound,max_bound):
        return np.random.uniform(low=min_bound,high=max_bound)

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
    
    def get_best_runs(self,likes,pars,runs):
        '''
        Returns the best 20% of the runs'''
        return [new_pars for (new_likes,new_pars) in sorted(zip(likes,pars))[int(len(likes)*(1-self.percentage)):]]
     
    def sample(self, repetitions,subsets=5,percentage=0.05):
        """
        Samples from the ROPE algorithm.
        
        Input
        ----------
        repetitions: int 
            Maximum number of runs.  
        """
        starttime=time.time()
        intervaltime=starttime
        self.min_bound, self.max_bound = self.find_min_max()
        randompar   = list(self.parameter()['optguess'])
        simulations = self.model(randompar)
        like        = self.likelihood(simulations,self.evaluation)
        self.percentage=percentage
        runs=int(repetitions/subsets)
        #Init ROPE with one subset
        likes=[]        
        pars=[]        
       
        param_generator = ((rep,list(self.parameter()['random'])) 
            for rep in xrange(int(runs)))
        for rep,ropepar,simulations in self.repeat(param_generator):
            #Calculate the objective function
            like        = self.likelihood(simulations,self.evaluation)
            likes.append(like)
            pars.append(ropepar)
            #Save everything in the database
            self.datawriter.save(like,ropepar,simulations=simulations)            
            
            pars.append(ropepar)
            likes.append(like)                
            self.status(rep,like,ropepar)            
            #Progress bar                
            acttime=time.time()
            #Refresh progressbar every second
            if acttime-intervaltime>=2:
                print '%i of %i (best like=%g)' % (rep,repetitions,self.status.likelihood)
                intervaltime=time.time()
       
        
        
        for i in range(subsets-1):
            best_pars=self.get_best_runs(likes,pars,runs)
            new_pars=self.programm_depth(best_pars,runs)
            pars=[]
            likes=[]

            param_generator = ((rep,list(new_pars[rep])) for rep in xrange(int(runs)))        
            for rep,ropepar,simulations in self.repeat(param_generator):        
                #Calculate the objective function
                like        = self.likelihood(simulations,self.evaluation)
                likes.append(like)
                pars.append(ropepar)
                #Save everything in the database
                self.datawriter.save(like,ropepar,simulations=simulations)            
                
                pars.append(ropepar)
                likes.append(like)
                self.status(rep+runs*i,like,ropepar)                
                #Progress bar                
                acttime=time.time()
                #Refresh progressbar every second
                if acttime-intervaltime>=2:
                    print '%i of %i (best like=%g)' % (rep+runs*i,repetitions,self.status.likelihood)
                    intervaltime=time.time()        
                        
        self.repeat.terminate()                    
        self.datawriter.finalize()
        print 'End of sampling'
        print '%i of %i (best like=%g)' % (self.status.rep,repetitions,self.status.likelihood)
        print 'Best parameter set:'        
        print self.status.params        
        print 'Duration:'+str(round((acttime-starttime),2))+' s'

        
    
    def programm_depth(self,pars,runs):
        X=np.array(pars)
        
        N, NP = X.shape
        print str(N)+' input vectors with '+str(NP)+' parameters'
        
        Ngen= int(runs)#int(N*(1/self.percentage))
        print('Generating '+str(Ngen)+' parameters:')
               
        NPOSI=Ngen   # Number of points to generate
        NDIR=Ngen/100   # The number of samples to draw 10000
        
        
        EPS=0.00001
        
        # Find  max and min values
        XMIN=np.zeros(NP); XMAX=np.zeros(NP)
        for j in range (NP):
            XMIN[j]=min(X[:,j])
            XMAX[j]=max(X[:,j])
        
        # Beginn to generate
        ITRY=1
        IPOS=1
        LLEN=N
        
        CL=np.zeros(NP)
        TL=np.zeros(shape=(LLEN, NP))
        while (IPOS<NPOSI):
            for IM in range (LLEN):   # LLEN=1000 Random Vectors of dim NP
                for j in range (NP):
                    DRAND=np.random.rand()
                    TL[IM,j]=XMIN[j]+DRAND*(XMAX[j]-XMIN[j])
            LNDEP=self.fHDEPTHAB(N, NP, NDIR, X, TL, EPS, LLEN) 
            for L in range (LLEN):
                ITRY=ITRY+1
                if LNDEP[L]>1:
                    CL=np.vstack((CL, TL[L, :]))
                    IPOS=IPOS+1
            print IPOS, ITRY
        CL=np.delete(CL,0, 0)
        CL=CL[:NPOSI]
        return CL
        
    def fHDEPTHAB(self,N, NP, NDIR, X, TL, EPS, LLEN):
        LNDEP=self.fDEP(N, NP, NDIR, X, TL, EPS, LLEN)
        return LNDEP
    
    def fDEP(self,N, NP, NDIR, X, TL, EPS, LLEN):    
        LNDEP=np.array([N for i in range (N)])
        for NRAN in range (NDIR):
    
    #       Random sample of size NP
            JSAMP=np.zeros(N)
            I=np.random.randint(1, N)
            if I>N: I=N
            JSAMP[0]=I
            NSAMP=1
    
            for index in range (NP-1):
                dirac=0
                while dirac==0:
                    dirac=1
                    L=np.random.randint(1, N+1)
                    if L>N: L=N
                    for j in range (NSAMP):
                        if L==JSAMP[j]: dirac=0
                NSAMP=NSAMP+1
                JSAMP[index+1]=L
    
    #       Covariance matrix of the sample
            S=np.zeros(shape=(NP, NP))
            for i in range(NP):
                row=JSAMP[i]
                S[i,:]=[X[row-1,j] for j in range (NP)] # S: random sample from X
            nx, NP = S.shape
            C=np.zeros(shape=(NP, NP))
            y=np.zeros(shape=(2,2))       
            for j in range(NP):
                for k in range (j+1):
                    y=np.cov(S[:,k], S[:,j])
                    C[j,k]=y[0,1]
                    C[k,j]=y[0,1]
            COV=C
    
            EVALS, EVE=np.linalg.eig(COV)
            arg=np.argsort(EVALS)
            EVECT=EVE[:, arg[0]] # Eigenvector in the direction of min eigenvalue
    
    #       Project all points on the line through theta with direction given by
    #       the eigenvector of the smallest eigenvalue, i.e. the direction
    #       orthogonal on the hyperplane given by the np-subset.
    #       Compute the one-dimensional halfspace depth of theta on this line
            HELP=[]
            for L in range (N):
                k=np.dot(EVECT, X[L,:])
                HELP.append(k)
            HELP=np.array(HELP)
            HELP=sorted(HELP)
    
            ICROSS=0
            for LU in range (LLEN):
                if (LNDEP[LU]>ICROSS):
                    EKT=0.
                    NT=0
                    EKT=EKT+np.dot(TL[LU, :], EVECT)  
                    if ((EKT<(HELP[0]-EPS)) or (EKT>(HELP[N-1]+EPS))):
                        N1=0
                    else:
                        N1=1
                        N2=N
                        dirac=0
                        while dirac==0:
                            dirac=1
                            N3=(N1+N2)/2.
                            if (HELP[int(N3)]<EKT):
                                N1=N3
                            else:
                                N2=N3
                            if(N2-N1)>1: dirac=0
                    NUMH=N1
                    LNDEP[LU]=min(LNDEP[LU], min(NUMH+NT, N-NUMH))
        return LNDEP
    
     