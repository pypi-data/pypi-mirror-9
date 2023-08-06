#!/home/gh2365/local/bin/python2.7
#$ -S /home/gh2365/local/bin/python2.7
#$ -l h_rt=24::
#$ -N bcf-sensi
#$ -V
#$ -cwd
# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

Example how to use the algorithms of spotpy
'''
import sys
import os
sys.path.append('../..')
import spot
#from spot_setup_griewank import spot_setup
#from spot_setup_ackley import spot_setup
from spot_setup_rosenbrock import spot_setup
spot_setup.slow=0
#from spot_setup_cmf1d import spot_setup
import pylab as plt
import numpy as np
import random
from scipy.stats import t
#import argparse
#parser = argparse.ArgParser()

rep=2000
#parameter=spot_setup().parameters
#param_generator = ((rep,Matrix[rep]) for rep in xrange(int(rep)-1)) 
samplers=[]
# Check if script is started with mpirun - works only with OpenMPI
parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'

#samplers.append(spot.algorithms.mc(spot_setup(),dbname='TestMC',dbformat='ram',parallel=parallel,save_sim=False))
#samplers.append(spot.algorithms.mcmc(spot_setup(),dbname='AckleyMCMC',dbformat='csv',parallel=parallel))
#samplers.append(bcf.algorithms.mle(spot_setup(),dbname='AckleyMLE',dbformat='csv',parallel=parallel))
#samplers.append(spot.algorithms.lhs(spot_setup(),dbname='TestLHS',dbformat='csv',parallel=parallel))
#samplers.append(spot.algorithms.sceua(spot_setup(),dbname='TestMPISCE-UA',dbformat='csv',parallel=parallel))
#samplers.append(spot.algorithms.sceua_old(spot_setup(),dbname='TestSCE-UA',dbformat='csv',parallel=parallel))

#samplers.append(spot.algorithms.demcz(spot_setup(),dbname='AckleyDE-MCz',dbformat='csv',parallel=parallel))
#samplers.append(spot.algorithms.sa(spot_setup(),dbname='AckleySim-Anneal',dbformat='csv',parallel=parallel))
#samplers.append(spot.algorithms.rope(spot_setup(),dbname='AckleyROPE',dbformat='csv',save_sim=False,parallel=parallel))

#sampler=spot.algorithms.rope(spot_setup(),dbname='RosenMCMC',dbformat='csv')
#sampler.sample(rep)
#a=sampler.getdata()
##sampler=spot.algorithms.mle(spot_setup(),dbname='RosenMLE',dbformat='csv')

#sampler=spot.algorithms.lhs(spot_setup(),dbname='TestLHS',dbformat='csv',parallel=parallel)

#sampler=spot.algorithms.sceua(spot_setup(),dbname='TestMPISCE-UA',dbformat='csv')

#sampler=spot.algorithms.demcz(spot_setup(),dbname='AckleyDE-MCz',dbformat='csv')

#sampler=spot.algortihm.sa(spot_setup(),dbname='AckleySA',dbformat='csv')

#sampler=spot.algorithms.rope(spot_setup(),dbname='AckleyROPE',dbformat='csv')





#for sampler in samplers:
#    a=sampler.sample(rep)
#    results.append(a)
#print results[0]
#    bcf.analyser.plot_likelihood(a,evaluation)
#
#evaluation = bcf_setup().evaluation()
#algorithms=['MC','LHS','MLE','MCMC','SCE-UA','Sim-Anneal','DE-MCz','ROPE']
#res=[]
#for algorithm in algorithms:
#    res.append(bcf.analyser.load_csv_results('Ackley'+algorithm))
#res.append(bcf.analyser.load_csv_results('AckleyLHS'))
#res.append(bcf.analyser.load_csv_results('AckleyMLE'))#[5000:]
#res.append(bcf.analyser.load_csv_results('AckleyMCMC'))#[5000:]
#res.append(bcf.analyser.load_csv_results('AckleySCEUA'))#[5000:]
#res.append(bcf.analyser.load_csv_results('AckleyDEMC'))#[5000:]
#res.append(bcf.analyser.load_csv_results('AckleyANNEAL'))#[5000:]

#
#results=[]
#for sampler in samplers:
#    results.append(sampler.sample(5000))
#
##bcf.analyser.plot_parametertrace(results,parameternames=['y'])
#bcf.analyser.plot_likelihood(results[0],evaluation)#,xlabel='MonteCarlo')
#bcf.analyser.plot_likelihood(results[1],evaluation)#,xlabel='MonteCarlo')

#def calc_best_like(likes):
#    bestlike=[likes[0]]
#    for like in likes:
#        if like<bestlike[-1]:
#            bestlike.append(like)
#        else:
#            bestlike.append(bestlike[-1])
#    return bestlike
#
##bcf.analyser.plot_bestmodelruns(res[0],evaluation,algorithms=algorithms,dates=evaldates, ylabel='soil moisture [%]')
#
#
'''HEATMAP GRIEWANK'''
#from matplotlib import ticker, cm
#font = {'family' : 'calibri',
#    'weight' : 'normal',
#    'size'   : 20}
#plt.rc('font', **font)  
#subplots=len(res)
#xticks=[-40,0,40]
#yticks=[-40,0,40]
#fig=plt.figure(figsize=(16,3))
#N = 2000
#x = np.linspace(-50.0, 50.0, N)
#y = np.linspace(-50.0, 50.0, N)
#
#x, y = np.meshgrid(x, y)
#
#z=1+ (x**2+y**2)/4000 - np.cos(x/np.sqrt(2))*np.cos(y/np.sqrt(3))
##z = 100.0*(x - x**2.0)**2.0 + (1 - y)**2.0
##
##norm = cm.colors.Normalize(vmax=abs(z).max(), vmin=-abs(z).max())
#cmap = plt.get_cmap('autumn')
##levels = np.linspace(-5, 5, 20)
#for i in range(subplots):
#    ax  = plt.subplot(1,subplots,i+1)
#    CS = ax.contourf(x, y, z,locator=ticker.LogLocator(),cmap=cmap)#,levels=levels)
#    ax.plot(res[i]['par0'],res[i]['par1'],'ko-',alpha=0.1,markersize=1.9) 
#    if i>0:
#        ax.yaxis.set_ticks([])
#    if i==0:
#        ax.set_ylabel('y')
#    ax.set_xlabel('x')
#    ax.xaxis.set_ticks(xticks)   
#    ax.set_title(algorithms[i])
#
#plt.tight_layout()  
#fig.savefig('test.png', bbox_inches='tight')  # <------ this
#fig.close()   


'''Like Trace Rosenbrock'''
#font = {'family' : 'calibri',
#    'weight' : 'normal',
#    'size'   : 20}
#plt.rc('font', **font)   
#fig=plt.figure(figsize=(17,5))
#xticks=[0,2000,4000]
#
#subplots=len(res)
#rows=2
#for j in range(rows):
#    for i in range(subplots):
#        ax  = plt.subplot(rows,subplots,i+1+j*subplots)
#        if j==0:
#            data=res[i]['parx']
#        if j==1:
#            data=res[i]['pary']
#            ax.set_xlabel(algorithms[i-subplots])
#        
#        ax.plot(data,'b-')
#        ax.plot([1]*rep,'r--')
#        ax.set_xlim(0,rep)
#        ax.set_ylim(-10,10)            
#        ax.xaxis.set_ticks(xticks)
#        if i==0 and j==0:
#            ax.set_ylabel('x')
#            ax.yaxis.set_ticks([-5,0,5])
#        if i==0 and j==1:
#            ax.set_ylabel('y')    
#            ax.yaxis.set_ticks([-5,0,5])
#        if j==0:
#            ax.xaxis.set_ticks([])
#        if i>0:
#            ax.yaxis.set_ticks([])
#    
#plt.tight_layout()
#fig.savefig('test2.png', bbox_inches='tight')  # <------ this
#fig.close() 


#subplots=len(res)
#rows=3
#for j in range(rows):
#    for i in range(subplots):
#        ax  = plt.subplot(rows,subplots,i+1+j*subplots)
#        if j==0:
#            data=bcf.analyser.calc_like(res[i],evaluation) 
#        if j==1:
#            data=res[i]['parx']
#        if j==2:
#            data=res[i]['pary']
#            ax.set_xlabel(algorithms[i-subplots])
#        
#        ax.plot(data,'b-')
#        ax.plot([1]*xticks[-1],'r--')
#        ax.set_xlim(0,rep)
#        
#        if j==0:
#            ax.set_ylim(0)            
#        if j>0:
#            ax.set_ylim(-10,10)            
#        if i==0 and j==0:
#            ax.set_ylabel('RMSE')
#        if i==0 and j==1:
#            ax.set_ylabel('x')
#            ax.set_ylim(-10,10)
#        if i==0 and j==2:
#            ax.set_ylabel('y')    
#            ax.set_ylim(-10,10)
#        else:
#            ax.yaxis.set_ticks([])
#        ax.xaxis.set_ticks(xticks)
#    
#plt.tight_layout()






'''Ackley Likelihood plotting'''     
#font = {'family' : 'calibri',
#    'weight' : 'normal',
#    'size'   : 20}
#plt.rc('font', **font)   
#fig=plt.figure(figsize=(16,3))
#xticks=[5000,15000]
#
#for i in range(len(res)):
#    ax  = plt.subplot(1,len(res),i+1)
#    likes=bcf.analyser.calc_like(res[i],evaluation)  
#    #bestlike=calc_best_like(likes)
#    #ax1.plot(bestlike,'k-')
#    ax.plot(likes,'b-')
#    ax.set_ylim(0,25)
#    ax.set_xlim(0,rep)
#    ax.set_xlabel(algorithms[i])
#    ax.xaxis.set_ticks(xticks)
#    if i==0:
#        ax.set_ylabel('RMSE')
#        ax.yaxis.set_ticks([0,10,20])   
#    else:
#        ax.yaxis.set_ticks([])        
#    
#plt.tight_layout()
#fig.savefig('Like_trace.png')




#ax2  = plt.subplot(1,8,2)
#likes=bcf.analyser.calc_like(resLHS,evaluation)  
##bestlike=calc_best_like(likes)
##ax2.plot(bestlike,'k-')
#ax2.plot(likes,'b-')
#ax2.set_ylim(0,1200000)
#ax2.set_xlim(0,rep)
#ax2.set_xlabel('LHC')
#ax2.xaxis.set_ticks(xticks)
#ax2.yaxis.set_ticks([])
#
#ax3  = plt.subplot(1,8,3)
#likes=bcf.analyser.calc_like(resMLE,evaluation)  
##bestlike=calc_best_like(likes)
##ax3.plot(bestlike,'k-')
#ax3.plot(likes,'b-')
#ax3.set_ylim(0,1200000)
#ax3.set_xlim(0,rep)
#ax3.set_xlabel('MLE')
#ax3.xaxis.set_ticks(xticks)
#ax3.yaxis.set_ticks([])
#
#ax4  = plt.subplot(1,8,4)
#likes=bcf.analyser.calc_like(resMCMC,evaluation)  
##bestlike=calc_best_like(likes)
##ax4.plot(bestlike,'k-')
#ax4.plot(likes,'b-')
#ax4.set_ylim(0,1200000)
#ax4.set_xlim(0,rep)
#ax4.set_xlabel('MCMC')
#ax4.xaxis.set_ticks(xticks)
#ax4.yaxis.set_ticks([])
#
#ax5  = plt.subplot(1,8,5)
#likes=bcf.analyser.calc_like(resSCEUA,evaluation)  
##bestlike=calc_best_like(likes)
##ax5.plot(bestlike,'k-')
#ax5.plot(likes,'b-')
#ax5.set_ylim(0,1200000)
#ax5.set_xlim(0,rep)
#ax5.set_xlabel('SCE-UA')
#ax5.xaxis.set_ticks(xticks)
#ax5.yaxis.set_ticks([])
#
#ax6  = plt.subplot(1,8,6)
#likes=bcf.analyser.calc_like(resANNEAL,evaluation)  
##bestlike=calc_best_like(likes)
##ax6.plot(bestlike,'k-')
#ax6.plot(likes,'b-')
#ax6.set_ylim(0,1200000)
#ax6.set_xlim(0,rep)
#ax6.set_xlabel('Sim-Anneal')
#ax6.xaxis.set_ticks(xticks)
#ax6.yaxis.set_ticks([])
#
#ax7  = plt.subplot(1,8,7)
#likes=bcf.analyser.calc_like(resDEMC,evaluation)  
##bestlike=calc_best_like(likes)
##ax6.plot(bestlike,'k-')
#ax7.plot(likes,'b-')
#ax7.set_ylim(0,1200000)
#ax7.set_xlim(0,rep)
#ax7.set_xlabel('DE-MC$_Z$')
#ax7.xaxis.set_ticks(xticks)
#ax7.yaxis.set_ticks([])
#
#ax8  = plt.subplot(1,8,7)
#likes=bcf.analyser.calc_like(resROPE,evaluation)  
##bestlike=calc_best_like(likes)
##ax6.plot(bestlike,'k-')
#ax8.plot(likes,'b-')
#ax8.set_ylim(0,1200000)
#ax8.set_xlim(0,rep)
#ax8.set_xlabel('ROPE')
#ax8.xaxis.set_ticks(xticks)
#ax8.yaxis.set_ticks([])







#results['parx']

#evaldates= bcf_setup().evaluation(evaldates=True)
##
#bcf.analyser.plot_bestmodelrun(resMC[500:-9000],evaluation,dates=evaldates, ylabel='soil moisture [%]')
#bcf.analyser.plot_bestmodelrun(resLHC[610:612],evaluation,dates=evaldates, ylabel='soil moisture [%]')
###bcf.analyser.plot_bestmodelrun(resMLE,evaluation,dates=evaldates, ylabel='soil moisture [%]')
###bcf.analyser.plot_bestmodelrun(resMCMC,evaluation,dates=evaldates, ylabel='soil moisture [%]')
###bcf.analyser.plot_bestmodelrun(resSCE,evaluation,dates=evaldates, ylabel='soil moisture [%]')
##bcf.analyser.plot_bestmodelrun(resDEMC,evaluation,dates=evaldates, ylabel='soil moisture [%]')
#
#def calc_like(results):
#    likes = []
#    sim   = bcf.analyser.get_modelruns(results)
#    for s in sim:
#        likes.append(bcf.likelihoods.nashsutcliff(s,evaluation))
#    return likes
#
#def sort_like(likes):
#    sort_likes=[]    
#    lastlike=-np.inf
#    for like in likes:
#        if like > lastlike:
#            lastlike = like
#            sort_likes.append(like)
#        else:
#            sort_likes.append(lastlike)
#    return sort_likes
##
#
#def parameters():
#    pars = []   #distribution of random value      #name  #stepsize# optguess
#    pars.append((np.random.normal(loc=.3,scale=0.1,size=10000),  'alpha',   0.02,  0.2))  
#    pars.append((np.random.normal(loc=1.2,scale=0.035,size=10000),     'n',     0.01,  1.22))        
#    pars.append((np.random.normal(loc=1,scale=0.3,size=10000),      'ksat' ,  0.1,   2.0))
#    pars.append((np.random.normal(loc=.55,scale=0.04,size=10000),  'porosity',  0.02,  0.6))
#    #dtype=np.dtype([('random', '<f8'), ('name', '|S30'),('step', '<f8'),('optguess', '<f8')])
#    return np.array(pars)
#    
#a=parameters()
#
#
#
#alpha=a[0][0]
#n=a[1][0]
#ksat=a[2][0]
#porosity=a[3][0
#]
#alphapost=resMC['paralpha']
#npost=resMC['parn']
#ksatpost=resMC['parksat']
#porositypost=resMC['parporosity']
#
#
#
#from scipy.stats import gaussian_kde
#font = {'family' : 'calibri',
#    'weight' : 'normal',
#    'size'   : 18}
#plt.rc('font', **font)   
#fig=plt.figure(figsize=(16,9))
#
#ax1  = plt.subplot(2,2,1)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#ax1.plot(xs,density(xs),label='prior')
#ax1.yaxis.set_ticklabels([])
#ax1.set_xlabel('alpha')
#ax1.set_xlim(0,0.7)
#
#ax2  = plt.subplot(2,2,2)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#ax2.plot(xs,density(xs),label='prior')
#ax2.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax2.yaxis.set_ticklabels([])
#ax2.set_xlim(1.05,1.35)
#ax2.set_xlabel('n')
##ax2.legend()
#
#
#ax3  = plt.subplot(2,2,3)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#ax3.plot(xs,density(xs),label='prior')
#ax3.yaxis.set_ticklabels([])
#ax3_new.yaxis.set_ticklabels([])
#ax3.set_xlabel('ksat')
#ax3.set_xlim(0,2.5)
#
#ax4  = plt.subplot(2,2,4)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#ax4.plot(xs,density(xs),label='prior')
#ax4.yaxis.set_ticklabels([])
#ax4.set_xlabel('porosity')
#ax4.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax4.set_xlim(0.35,0.75)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#alpha=a[0][0]
#n=a[1][0]
#ksat=a[2][0]
#porosity=a[3][0
#]
#alphapost=resMC['paralpha']
#npost=resMC['parn']
#ksatpost=resMC['parksat']
#porositypost=resMC['parporosity']
#
#from scipy.stats import gaussian_kde
#font = {'family' : 'calibri',
#    'weight' : 'normal',
#    'size'   : 18}
#plt.rc('font', **font)   
#fig=plt.figure(figsize=(16,9))
#
#ax1  = plt.subplot(6,4,1)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax1.plot(xs,density(xs),label='prior')
#ax1_new = ax1.twinx()
#ax1_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax1.yaxis.set_ticklabels([])
#ax1_new.yaxis.set_ticklabels([])
#ax1.set_xlabel('alpha')
#ax1.set_ylabel('Monte Carlo')
#ax1.axvline(x=0.3565,c='red')
#ax1.set_xlim(0,0.7)
#
#ax2  = plt.subplot(6,4,2)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax2.plot(xs,density(xs),label='prior')
#ax2_new = ax2.twinx()
#ax2_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax2.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax2_new.yaxis.set_ticklabels([])
#ax2.yaxis.set_ticklabels([])
#ax2.set_xlim(1.05,1.35)
#ax2.axvline(x=1.2039,c='red',label='best fit')
#ax2.set_xlabel('n')
##ax2.legend()
#
#
#ax3  = plt.subplot(6,4,3)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax3.plot(xs,density(xs),label='prior')
#ax3_new = ax3.twinx()
#ax3_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax3.yaxis.set_ticklabels([])
#ax3_new.yaxis.set_ticklabels([])
#ax3.set_xlabel('ksat')
#ax3.axvline(x=0.8718,c='red')
#ax3.set_xlim(0,2.5)
#
#ax4  = plt.subplot(6,4,4)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(porositypost)
#xspost = np.linspace(min(porositypost),max(porositypost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax4.plot(xs,density(xs),label='prior')
#ax4_new = ax4.twinx()
#ax4_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax4.yaxis.set_ticklabels([])
#ax4_new.yaxis.set_ticklabels([])
#ax4.set_xlabel('porosity')
#ax4.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax4.axvline(x=0.658,c='red')
#ax4.set_xlim(0.35,0.75)
#
#
#alphapost=resLHC['paralpha']
#npost=resLHC['parn']
#ksatpost=resLHC['parksat']
#porositypost=resLHC['parporosity']
#
#
#ax5  = plt.subplot(6,4,5)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax5.plot(xs,density(xs),label='prior')
#ax5_new = ax5.twinx()
#ax5_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax5.yaxis.set_ticklabels([])
#ax5_new.yaxis.set_ticklabels([])
#ax5.set_xlabel('alpha')
#ax5.set_ylabel('LHC')
#ax5.axvline(x=0.3248,c='red')
#ax5.set_xlim(0,0.7)
#
#ax6  = plt.subplot(6,4,6)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax6.plot(xs,density(xs),label='prior')
#ax6_new = ax6.twinx()
#ax6_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax6.yaxis.set_ticklabels([])
#ax6_new.yaxis.set_ticklabels([])
#ax6.set_xlim(1.05,1.35)
#ax6.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax6.axvline(x=1.2052,c='red',label='best fit')
#ax6.set_xlabel('n')
##ax2.legend()
#
#
#ax7  = plt.subplot(6,4,7)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax7.plot(xs,density(xs),label='prior')
#ax7_new = ax7.twinx()
#ax7_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax7.yaxis.set_ticklabels([])
#ax7_new.yaxis.set_ticklabels([])
#ax7.set_xlabel('ksat')
#ax7.axvline(x=1.088,c='red')
#ax7.set_xlim(0,2.5)
#
#ax8  = plt.subplot(6,4,8)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(porositypost)
#xspost = np.linspace(min(porositypost),max(porositypost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax8.plot(xs,density(xs),label='prior')
#ax8_new = ax8.twinx()
#ax8_new.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax8.yaxis.set_ticklabels([])
#ax8_new.yaxis.set_ticklabels([])
#ax8.set_xlabel('porosity')
#ax8.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax8.axvline(x=0.667,c='red')
#ax8.set_xlim(0.35,0.75)
#
#
#
#
#alphapost=resMLE['paralpha']
#npost=resMLE['parn']
#ksatpost=resMLE['parksat']
#porositypost=resMLE['parporosity']
#
#
#ax9  = plt.subplot(6,4,9)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax9.plot(xs,density(xs),label='prior')
#ax91 = ax9.twinx()
#ax91.plot(xspost,densitypost(xspost),label='posterior')
#ax9.yaxis.set_ticklabels([])
#ax91.yaxis.set_ticklabels([])
#ax9.set_xlabel('alpha')
#ax9.set_ylabel('MLE')
#ax9.axvline(x=0.3456,c='red')
#ax9.set_xlim(0,0.7)
#
#ax10  = plt.subplot(6,4,10)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax10.plot(xs,density(xs),label='prior')
#ax101 = ax10.twinx()
#ax101.plot(xspost,densitypost(xspost),label='posterior')
#ax10.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax10.yaxis.set_ticklabels([])
#ax101.yaxis.set_ticklabels([])
#ax10.set_xlim(1.05,1.35)
#ax10.axvline(x=1.1754,c='red',label='best fit')
#ax10.set_xlabel('n')
##ax2.legend()
#
#
#ax11  = plt.subplot(6,4,11)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax11.plot(xs,density(xs),label='prior')
#ax111 = ax11.twinx()
#ax111.plot(xspost,densitypost(xspost),label='posterior')
#ax11.yaxis.set_ticklabels([])
#ax111.yaxis.set_ticklabels([])
#ax11.set_xlabel('ksat')
#ax11.axvline(x=1.7764,c='red')
#ax11.set_xlim(0,2.5)
#
#ax12  = plt.subplot(6,4,12)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
##densitypost = gaussian_kde(porositypost)
##xspost = np.linspace(min(porositypost),max(porositypost),200)
##densitypost.covariance_factor = lambda : .9
##densitypost._compute_covariance()
#ax12.plot(xs,density(xs),label='prior')
##ax121 = ax12.twinx()
##ax121.plot(xspost,densitypost(xspost),label='posterior')
#ax12.yaxis.set_ticklabels([])
##ax121.yaxis.set_ticklabels([])
#ax12.set_xlabel('porosity')
#ax12.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax12.axvline(x=0.622,c='red')
#ax12.set_xlim(0.35,0.75)
#
#
#alphapost=resMCMC['paralpha']
#npost=resMCMC['parn']
#ksatpost=resMCMC['parksat']
#porositypost=resMCMC['parporosity']
#
#
#ax13  = plt.subplot(6,4,13)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax13.plot(xs,density(xs),label='prior')
#ax131 = ax13.twinx()
#ax131.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax13.yaxis.set_ticklabels([])
#ax131.yaxis.set_ticklabels([])
#ax13.set_xlabel('alpha')
#ax13.set_ylabel('MCMC')
#ax13.axvline(x=0.3248,c='red')
#ax13.set_xlim(0,0.7)
#
#ax14  = plt.subplot(6,4,14)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax14.plot(xs,density(xs),label='prior')
#ax141 = ax14.twinx()
#ax141.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax14.yaxis.set_ticklabels([])
#ax141.yaxis.set_ticklabels([])
#ax14.set_xlim(1.05,1.35)
#ax14.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax14.axvline(x=1.1833,c='red',label='best fit')
#ax14.set_xlabel('n')
##ax2.legend()
#
#
#ax15  = plt.subplot(6,4,15)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax15.plot(xs,density(xs),label='prior')
#ax151 = ax15.twinx()
#ax151.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax15.yaxis.set_ticklabels([])
#ax151.yaxis.set_ticklabels([])
#ax15.set_xlabel('ksat')
#ax15.axvline(x=1.3355,c='red')
#ax15.set_xlim(0,2.5)
#
#ax16  = plt.subplot(6,4,16)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(porositypost)
#xspost = np.linspace(min(porositypost),max(porositypost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax16.plot(xs,density(xs),label='prior')
#ax161 = ax16.twinx()
#ax161.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax16.yaxis.set_ticklabels([])
#ax161.yaxis.set_ticklabels([])
#ax16.set_xlabel('porosity')
#ax16.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax16.axvline(x=0.627,c='red')
#ax16.set_xlim(0.35,0.75)
#
#
#
#alphapost=resSCE['paralpha']
#npost=resSCE['parn']
#ksatpost=resSCE['parksat']
#porositypost=resSCE['parporosity']
#
#
#ax17  = plt.subplot(6,4,17)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax17.plot(xs,density(xs),label='prior')
#ax171 = ax17.twinx()
#ax171.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax17.yaxis.set_ticklabels([])
#ax171.yaxis.set_ticklabels([])
#ax17.set_xlabel('alpha')
#ax17.set_ylabel('SCE-UA')
#ax17.axvline(x=0.3409,c='red')
#ax17.set_xlim(0,0.7)
#
#ax18  = plt.subplot(6,4,18)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax18.plot(xs,density(xs),label='prior')
#ax181 = ax18.twinx()
#ax181.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax18.yaxis.set_ticklabels([])
#ax181.yaxis.set_ticklabels([])
#ax18.set_xlim(1.05,1.35)
#ax18.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax18.axvline(x=1.2089,c='red',label='best fit')
#ax18.set_xlabel('n')
##ax2.legend()
#
#
#ax19  = plt.subplot(6,4,19)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax19.plot(xs,density(xs),label='prior')
#ax191 = ax19.twinx()
#ax191.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax19.yaxis.set_ticklabels([])
#ax191.yaxis.set_ticklabels([])
#ax19.set_xlabel('ksat')
#ax19.axvline(x=0.8437,c='red')
#ax19.set_xlim(0,2.5)
#
#ax20  = plt.subplot(6,4,20)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(porositypost)
#xspost = np.linspace(min(porositypost),max(porositypost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax20.plot(xs,density(xs),label='prior')
#ax201 = ax20.twinx()
#ax201.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax20.yaxis.set_ticklabels([])
#ax201.yaxis.set_ticklabels([])
#ax20.set_xlabel('porosity')
#ax20.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax20.axvline(x=0.668,c='red')
#ax20.set_xlim(0.35,0.75)
#
#
#
#
#alphapost=resDEMC['paralpha']
#npost=resDEMC['parn']
#ksatpost=resDEMC['parksat']
#porositypost=resDEMC['parporosity']
#
#
#ax21  = plt.subplot(6,4,21)
#density = gaussian_kde(alpha)
#xs = np.linspace(min(alpha),max(alpha),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(alphapost)
#xspost = np.linspace(min(alphapost),max(alphapost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax21.plot(xs,density(xs),label='prior')
#ax211 = ax21.twinx()
#ax211.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax21.yaxis.set_ticklabels([])
#ax211.yaxis.set_ticklabels([])
#ax21.set_xlabel('alpha')
#ax21.set_ylabel('DREAMz')
#ax21.axvline(x=0.2534,c='red')
#ax21.set_xlim(0,0.7)
#
#ax22  = plt.subplot(6,4,22)
#density = gaussian_kde(n)
#xs = np.linspace(min(n),max(n),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(npost)
#xspost = np.linspace(min(npost),max(npost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax22.plot(xs,density(xs),label='prior')
#ax221 = ax22.twinx()
#ax221.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax22.yaxis.set_ticklabels([])
#ax221.yaxis.set_ticklabels([])
#ax22.set_xlim(1.05,1.35)
#ax22.xaxis.set_ticks([1.05,1.15,1.25,1.35])
#ax22.axvline(x=1.1742,c='red',label='best fit')
#ax22.set_xlabel('n')
##ax2.legend()
#
#
#ax23  = plt.subplot(6,4,23)
#density = gaussian_kde(ksat)
#xs = np.linspace(min(ksat),max(ksat),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(ksatpost)
#xspost = np.linspace(min(ksatpost),max(ksatpost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax23.plot(xs,density(xs),label='prior')
#ax231 = ax23.twinx()
#ax231.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax23.yaxis.set_ticklabels([])
#ax231.yaxis.set_ticklabels([])
#ax23.set_xlabel('ksat')
#ax23.axvline(x=0.9685,c='red')
#ax23.set_xlim(0,2.5)
#
#ax24  = plt.subplot(6,4,24)
#density = gaussian_kde(porosity)
#xs = np.linspace(min(porosity),max(porosity),200)
#density.covariance_factor = lambda : .9
#density._compute_covariance()
#densitypost = gaussian_kde(porositypost)
#xspost = np.linspace(min(porositypost),max(porositypost),200)
#densitypost.covariance_factor = lambda : .9
#densitypost._compute_covariance()
#ax24.plot(xs,density(xs),label='prior')
#ax241 = ax24.twinx()
#ax241.plot(xspost,densitypost(xspost),'g-',label='posterior')
#ax24.yaxis.set_ticklabels([])
#ax241.yaxis.set_ticklabels([])
#ax24.set_xlabel('porosity')
#ax24.xaxis.set_ticks([0.35,0.45,0.55,0.65,0.75])
#ax24.axvline(x=0.591,c='red')
#ax24.set_xlim(0.35,0.75)
#
#
##hist(alpha)
##hist(alphapost)
#plt.show()
#fig.savefig('paradist.png')   
#bcf.analyser.plot_posterior(resMC,evaluation,dates=evaldates, ylabel='soil moisture [%]')
#MClike = calc_like(resMC)
#MCslike=sort_like(MClike)
#
#LHClike = calc_like(resLHC)
#LHCslike=sort_like(LHClike)
#
#MLElike = calc_like(resMLE)
#MLEslike=sort_like(MLElike)
#
#MCMClike = calc_like(resMCMC)
#MCMCslike=sort_like(MCMClike)
#
#SCElike = calc_like(resSCE)
#SCEslike=sort_like(SCElike)
#
#DEMClike = calc_like(resDEMC)
#DEMCslike=sort_like(DEMClike)
#
#
#fig=plt.figure(figsize=(16,9))
#
#ax1  = plt.subplot(4,6,1)
#ax1.plot(MClike)
#ax1.plot(MCslike)
#ax1.set_ylabel('cummulative NSE')
#ax1.set_ylim(-5,1)
#ax1.xaxis.set_ticklabels([])
#
#ax2 = plt.subplot(4,6,2)
#ax2.plot(LHClike)
#ax2.plot(LHCslike)
#ax2.set_ylim(-5,1)
#ax2.xaxis.set_ticklabels([])
#ax2.yaxis.set_ticklabels([])
#
#ax3 = plt.subplot(4,6,3)
#ax3.plot(MLElike)
#ax3.plot(MLEslike)
#ax3.set_ylim(-5,1)
#ax3.xaxis.set_ticklabels([])
#ax3.yaxis.set_ticklabels([])
#
#ax4 = plt.subplot(4,6,4)
#ax4.plot(MCMClike)
#ax4.plot(MCMCslike)
#ax4.set_ylim(-5,1)
#ax4.xaxis.set_ticklabels([])
#ax4.yaxis.set_ticklabels([])
#
#ax5 = plt.subplot(4,6,5)
#ax5.plot(SCElike)
#ax5.plot(SCEslike)
#ax5.set_ylim(-5,1)
#ax5.xaxis.set_ticklabels([])
#ax5.yaxis.set_ticklabels([])
#
#ax6 = plt.subplot(4,6,6)
#ax6.plot(DEMClike)
#ax6.plot(DEMCslike)
#ax6.set_ylim(-5,1)
#ax6.xaxis.set_ticklabels([])
#ax6.yaxis.set_ticklabels([])
#
#
    
#fig=plt.figure(figsize=(16,9))
#ax1 = plt.subplot(4,6,1)
#ax1.plot(resMC['paralpha'])
#ax1.set_ylabel('alpha')
#ax1.set_ylim(0,0.6)
#ax1.xaxis.set_ticklabels([])
#ax1.xaxis.set_ticks([0,2500,5000])
#
#ax2 = plt.subplot(4,6,2)
#ax2.plot(resLHC['paralpha'])
#ax2.set_ylim(0,0.6)
#ax2.xaxis.set_ticklabels([])
#ax2.yaxis.set_ticklabels([])
#ax2.xaxis.set_ticks([0,2500,5000])
#
#ax3 = plt.subplot(4,6,3)
#ax3.plot(resMLE['paralpha'])
#ax3.set_ylim(0,0.6)
#ax3.xaxis.set_ticklabels([])
#ax3.yaxis.set_ticklabels([])
#ax3.xaxis.set_ticks([0,2500,5000])
#
#ax4 = plt.subplot(4,6,4)
#ax4.plot(resMCMC['paralpha'])
#ax4.set_ylim(0,0.6)
#ax4.xaxis.set_ticklabels([])
#ax4.yaxis.set_ticklabels([])
#ax4.xaxis.set_ticks([0,2500,5000])
#
#ax5 = plt.subplot(4,6,5)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax5.plot(list(resSCE[chain]['paralpha']))
#ax5.set_ylim(0,0.6)
#ax5.xaxis.set_ticklabels([])
#ax5.yaxis.set_ticklabels([])
#ax5.xaxis.set_ticks([0,150,300])
#
#ax6 = plt.subplot(4,6,6)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax6.plot(list(resDEMC[chain]['paralpha']))
#ax6.set_ylim(0,0.6)
#ax6.xaxis.set_ticklabels([])
#ax6.yaxis.set_ticklabels([])
#ax6.xaxis.set_ticks([0,500,1000])
#
#
#ax7 = plt.subplot(4,6,7)
#ax7.plot(resMC['parn'])
#ax7.set_ylabel('n')
#ax7.set_ylim(1.05,1.35)
#ax7.xaxis.set_ticklabels([])
#ax7.xaxis.set_ticks([0,2500,5000])
#
#ax8 = plt.subplot(4,6,8)
#ax8.plot(resLHC['parn'])
#ax8.set_ylim(1.05,1.35)
#ax8.xaxis.set_ticklabels([])
#ax8.yaxis.set_ticklabels([])
#ax8.xaxis.set_ticks([0,2500,5000])
#
#ax9 = plt.subplot(4,6,9)
#ax9.plot(resMLE['parn'])
#ax9.set_ylim(1.05,1.35)
#ax9.xaxis.set_ticklabels([])
#ax9.yaxis.set_ticklabels([])
#ax9.xaxis.set_ticks([0,2500,5000])
#
#ax10 = plt.subplot(4,6,10)
#ax10.plot(resMCMC['parn'])
#ax10.set_ylim(1.05,1.35)
#ax10.xaxis.set_ticklabels([])
#ax10.yaxis.set_ticklabels([])
#ax10.xaxis.set_ticks([0,2500,5000])
#
#ax11 = plt.subplot(4,6,11)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax11.plot(list(resSCE[chain]['parn']))
#ax11.set_ylim(1.05,1.35)
#ax11.xaxis.set_ticklabels([])
#ax11.yaxis.set_ticklabels([])
#ax11.xaxis.set_ticks([0,150,300])
#
#ax12 = plt.subplot(4,6,12)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax12.plot(list(resDEMC[chain]['parn']))
#ax12.set_ylim(1.05,1.35)
#ax12.xaxis.set_ticklabels([])
#ax12.yaxis.set_ticklabels([])
#ax12.xaxis.set_ticks([0,500,1000])
#
#
#ax13 = plt.subplot(4,6,13)
#ax13.plot(resMC['parporosity'])
#ax13.set_ylabel('porosity')
#ax13.set_ylim(.4,.7)
#ax13.xaxis.set_ticklabels([])
#ax13.xaxis.set_ticks([0,2500,5000])
#
#
#ax14 = plt.subplot(4,6,14)
#ax14.plot(resLHC['parporosity'])
#ax14.set_ylim(.4,.7)
#ax14.xaxis.set_ticklabels([])
#ax14.yaxis.set_ticklabels([])
#ax14.xaxis.set_ticks([0,2500,5000])
#
#ax15 = plt.subplot(4,6,15)
#ax15.plot(resMLE['parporosity'])
#ax15.set_ylim(.4,.7)
#ax15.xaxis.set_ticklabels([])
#ax15.yaxis.set_ticklabels([])
#ax15.xaxis.set_ticks([0,2500,5000])
#
#ax16 = plt.subplot(4,6,16)
#ax16.plot(resMCMC['parporosity'])
#ax16.set_ylim(.4,.7)
#ax16.xaxis.set_ticklabels([])
#ax16.yaxis.set_ticklabels([])
#ax16.xaxis.set_ticks([0,2500,5000])
#
#ax17 = plt.subplot(4,6,17)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax17.plot(list(resSCE[chain]['parporosity']))
#ax17.set_ylim(.4,.7)
#ax17.xaxis.set_ticklabels([])
#ax17.yaxis.set_ticklabels([])
#ax17.xaxis.set_ticks([0,150,300])
#
#ax18 = plt.subplot(4,6,18)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax18.plot(list(resDEMC[chain]['parporosity']))
#ax18.set_ylim(.4,.7)
#ax18.xaxis.set_ticklabels([])
#ax18.yaxis.set_ticklabels([])
#ax18.xaxis.set_ticks([0,500,1000])
#
#
#
#ax19 = plt.subplot(4,6,19)
#ax19.plot(resMC['parksat'])
#ax19.set_ylabel('ksat')
#ax19.set_ylim(0,2.5)
#ax19.xaxis.set_ticks([0,2500,5000])
#ax19.set_xlabel('MonteCarlo')
#
#ax20 = plt.subplot(4,6,20)
#ax20.plot(resLHC['parksat'])
#ax20.set_ylim(0,2.5)
#ax20.yaxis.set_ticklabels([])
#ax20.xaxis.set_ticks([0,2500,5000])
#ax20.set_xlabel('LHC')
#
#ax21 = plt.subplot(4,6,21)
#ax21.plot(resMLE['parksat'])
#ax21.set_ylim(0,2.5)
#ax21.yaxis.set_ticklabels([])
#ax21.xaxis.set_ticks([0,2500,5000])
#ax21.set_xlabel('MLE')
#
#ax22 = plt.subplot(4,6,22)
#ax22.plot(resMCMC['parksat'])
#ax22.set_ylim(0,2.5)
#ax22.yaxis.set_ticklabels([])
#ax22.xaxis.set_ticks([0,2500,5000])
#ax22.set_xlabel('MCMC')
#
#ax23 = plt.subplot(4,6,23)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax23.plot(list(resSCE[chain]['parksat']))
#ax23.set_ylim(0,2.5)
#ax23.yaxis.set_ticklabels([])
#ax23.xaxis.set_ticks([0,150,300])
#ax23.set_xlabel('SCE-UA')
#
#ax24 = plt.subplot(4,6,24)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax24.plot(list(resDEMC[chain]['parksat']))
#ax24.set_ylim(0,2.5)
#ax24.yaxis.set_ticklabels([])
#ax24.xaxis.set_ticks([0,500,1000])
#ax24.set_xlabel('DREAMz')
#
#plt.tight_layout()
#
#
#
#fig.savefig('bestmodel.png')    
    
    
    
#
#fig=plt.figure(figsize=(16,9))
#ax1 = plt.subplot(4,6,1)
#ax1.plot(resMC['paralpha'])
#ax1.set_ylabel('alpha')
#ax1.set_ylim(0,0.6)
#ax1.xaxis.set_ticklabels([])
#
#ax2 = plt.subplot(4,6,2)
#ax2.plot(resLHC['paralpha'])
#ax2.set_ylim(0,0.6)
#ax2.xaxis.set_ticklabels([])
#ax2.yaxis.set_ticklabels([])
#
#ax3 = plt.subplot(4,6,3)
#ax3.plot(resMLE['paralpha'])
#ax3.set_ylim(0,0.6)
#ax3.xaxis.set_ticklabels([])
#ax3.yaxis.set_ticklabels([])
#
#ax4 = plt.subplot(4,6,4)
#ax4.plot(resMCMC['paralpha'])
#ax4.set_ylim(0,0.6)
#ax4.xaxis.set_ticklabels([])
#ax4.yaxis.set_ticklabels([])
#
#ax5 = plt.subplot(4,6,5)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax5.plot(list(resSCE[chain]['paralpha']))
#ax5.set_ylim(0,0.6)
#ax5.xaxis.set_ticklabels([])
#ax5.yaxis.set_ticklabels([])
#
#ax6 = plt.subplot(4,6,6)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax6.plot(list(resDEMC[chain]['paralpha']))
#ax6.set_ylim(0,0.6)
#ax6.xaxis.set_ticklabels([])
#ax6.yaxis.set_ticklabels([])
#
#
#
#ax7 = plt.subplot(4,6,7)
#ax7.plot(resMC['parn'])
#ax7.set_ylabel('n')
#ax7.set_ylim(1.05,1.35)
#ax7.xaxis.set_ticklabels([])
#
#ax8 = plt.subplot(4,6,8)
#ax8.plot(resLHC['parn'])
#ax8.set_ylim(1.05,1.35)
#ax8.xaxis.set_ticklabels([])
#ax8.yaxis.set_ticklabels([])
#
#ax9 = plt.subplot(4,6,9)
#ax9.plot(resMLE['parn'])
#ax9.set_ylim(1.05,1.35)
#ax9.xaxis.set_ticklabels([])
#ax9.yaxis.set_ticklabels([])
#
#ax10 = plt.subplot(4,6,10)
#ax10.plot(resMCMC['parn'])
#ax10.set_ylim(1.05,1.35)
#ax10.xaxis.set_ticklabels([])
#ax10.yaxis.set_ticklabels([])
#
#ax11 = plt.subplot(4,6,11)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax11.plot(list(resSCE[chain]['parn']))
#ax11.set_ylim(1.05,1.35)
#ax11.xaxis.set_ticklabels([])
#ax11.yaxis.set_ticklabels([])
#
#ax12 = plt.subplot(4,6,12)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax12.plot(list(resDEMC[chain]['parn']))
#ax12.set_ylim(1.05,1.35)
#ax12.xaxis.set_ticklabels([])
#ax12.yaxis.set_ticklabels([])
#
#
#
#ax13 = plt.subplot(4,6,13)
#ax13.plot(resMC['parporosity'])
#ax13.set_ylabel('porosity')
#ax13.set_ylim(.4,.7)
#ax13.xaxis.set_ticklabels([])
#
#
#ax14 = plt.subplot(4,6,14)
#ax14.plot(resLHC['parporosity'])
#ax14.set_ylim(.4,.7)
#ax14.xaxis.set_ticklabels([])
#ax14.yaxis.set_ticklabels([])
#
#ax15 = plt.subplot(4,6,15)
#ax15.plot(resMLE['parporosity'])
#ax15.set_ylim(.4,.7)
#ax15.xaxis.set_ticklabels([])
#ax15.yaxis.set_ticklabels([])
#
#ax16 = plt.subplot(4,6,16)
#ax16.plot(resMCMC['parporosity'])
#ax16.set_ylim(.4,.7)
#ax16.xaxis.set_ticklabels([])
#ax16.yaxis.set_ticklabels([])
#
#ax17 = plt.subplot(4,6,17)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax17.plot(list(resSCE[chain]['parporosity']))
#ax17.set_ylim(.4,.7)
#ax17.xaxis.set_ticklabels([])
#ax17.yaxis.set_ticklabels([])
#
#ax18 = plt.subplot(4,6,18)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax18.plot(list(resDEMC[chain]['parporosity']))
#ax18.set_ylim(.4,.7)
#ax18.xaxis.set_ticklabels([])
#ax18.yaxis.set_ticklabels([])
#
#
#
#ax19 = plt.subplot(4,6,19)
#ax19.plot(resMC['parksat'])
#ax19.set_ylabel('ksat')
#ax19.set_ylim(0,2.5)
#ax19.xaxis.set_ticks([0,5000,10000])
#ax19.set_xlabel('MonteCarlo')
#
#ax20 = plt.subplot(4,6,20)
#ax20.plot(resLHC['parksat'])
#ax20.set_ylim(0,2.5)
#ax20.yaxis.set_ticklabels([])
#ax20.xaxis.set_ticks([0,5000,10000])
#ax20.set_xlabel('LHC')
#
#ax21 = plt.subplot(4,6,21)
#ax21.plot(resMLE['parksat'])
#ax21.set_ylim(0,2.5)
#ax21.yaxis.set_ticklabels([])
#ax21.xaxis.set_ticks([0,5000,10000])
#ax21.set_xlabel('MLE')
#
#ax22 = plt.subplot(4,6,22)
#ax22.plot(resMCMC['parksat'])
#ax22.set_ylim(0,2.5)
#ax22.yaxis.set_ticklabels([])
#ax22.xaxis.set_ticks([0,5000,10000])
#ax22.set_xlabel('MCMC')
#
#ax23 = plt.subplot(4,6,23)
#chains=int(max(resSCE['chain']))
#for i in range(chains):
#    chain=np.where(resSCE['chain']==i+1)
#    ax23.plot(list(resSCE[chain]['parksat']))
#ax23.set_ylim(0,2.5)
#ax23.yaxis.set_ticklabels([])
#ax23.xaxis.set_ticks([0,200,400,600])
#ax23.set_xlabel('SCE-UA')
#
#ax24 = plt.subplot(4,6,24)
#chains=int(max(resDEMC['chain']))
#for i in range(chains):
#    chain=np.where(resDEMC['chain']==i+1)
#    ax24.plot(list(resDEMC[chain]['parksat']))
#ax24.set_ylim(0,2.5)
#ax24.yaxis.set_ticklabels([])
#ax24.xaxis.set_ticks([0,1000,2000])
#ax24.set_xlabel('DREAMz')
#
#plt.tight_layout()
#
#
#
#fig.savefig('bestmodel.png')
#print 'The figure as been saved as "Modelruns.png"' 


#

#bcf.analyser.plot_bestmodelrun(results,evaluation,dates=evaldates, ylabel='soil moisture [%]')
#bcf.analyser.plot_parametertrace(results,parameternames=['alpha','n'])
##bcf.analyser.plot_regression(results[chain],evaluation)
#bcf.analyser.plot_parameterInteraction(results)#[:5000])
##plt.show()


