# -*- coding: utf-8 -*-
'''
Copyright 2015 by Tobias Houska
This file is part of Statistical Parameter Estimation Tool (SPOTPY).

:author: Tobias Houska

Holds functions to analyse results out of the database.
'''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from spotpy import likelihoods
import random
from matplotlib import colors

font = {'family' : 'calibri',
    'weight' : 'normal',
    'size'   : 18}

cnames=list(colors.cnames)
        
def load_csv_results(filename):
    """
    Get an array of your results in the given file, without the first and the 
    last column. The first line may have a different likelihood and the last 
    line may be incomplete, which would result in an error.
    
    :filename: Expects an available filename, without the csv, in your working directory
    :type: str
    
    :return: Result array
    :rtype: array
    """
    return np.genfromtxt(filename+'.csv',delimiter=',',names=True,skip_footer=1)[1:]   
    
def get_modelruns(results):
    """
    Get an shorter array out of your result array, containing just the 
    simulations of your model.
    
    :results: Expects an numpy array which should have indices beginning with "sim"
    :type: array
             
    :return: Array containing just the columns beginnning with the indice "sim"
    :rtype: array
    """   
    fields=[word for word in results.dtype.names if word.startswith('sim')]
    return results[fields]

def get_parameters(results):
    """
    Get an shorter array out of your result array, containing just the 
    parameters of your model.
    
    :results: Expects an numpy array which should have indices beginning with "par"
    :type: array
         
    :return: Array containing just the columns beginnning with the indice "par"
    :rtype: array
    """ 
    fields=[word for word in results.dtype.names if word.startswith('par')]
    results = results[fields]
    print results.dtype.names# = get_parameternames(results)
    results.dtype.names = get_parameternames(results)    
    return results

def get_parameternames(results):
    """
    Get list of strings with the names of the parameters of your model.
    
    :results: Expects an numpy array which should have indices beginning with "par"
    :type: array
    
    :return: Strings with the names of the analysed parameters 
    :rtype: list
        
    """
    fields=[word for word in results.dtype.names if word.startswith('par')]
    
    parnames=[]
    for field in fields:
        parnames.append(field[3:])
    return parnames
    
def get_maxlikeindex(results):
    """
    Get the maximum likelihood of your result array
    
    :results: Expects an numpy array which should of an index "like" for likelihoods 
    :type: array    
    
    :return: Index of the position in the results array with the maximum likelihood
        value and value of the maximum likelihood of your result array
    :rtype: int and float
    """        
    maximum=max(results['like'])    
    print 'The best model run has an likelihood of: '+str(round(maximum,4))
    index=np.where(results['like']==maximum)
    return index, maximum

def get_minlikeindex(results):
    """
    Get the minimum likelihood of your result array
    
    :results: Expects an numpy array which should of an index "like" for likelihoods 
    :type: array    
    
    :return: Index of the position in the results array with the minimum likelihood
        value and value of the minimum likelihood of your result array
    :rtype: int and float
    """            
    minimum=min(results['like'])    
    print 'The best model run has an likelihood of: '+str(round(minimum,4))
    index=np.where(results['like']==minimum)
    return index, minimum    

def calc_like(results,evaluation):
    likes=[]
    sim=get_modelruns(results)
    for s in sim:
        likes.append(likelihoods.rmse(list(s),evaluation))
        #likes.append(likelihoods.agreementindex(list(s),evaluation))
    return likes

def get_posterior(results,threshold=0.9):
	return np.sort(results,axis=0)[len(results)*threshold:]


def sort_like(results):
    return np.sort(results,axis=0)

def get_best_parameterset(results,maximize=True):
    try:
        likes=results['like']
    except ValueError:
        likes=results['like1']
    if maximize:
        best=max(likes)
    else:
        best=min(likes)
    index=np.where(likes==best)
    return get_parameters(results[index])
        
#def heat_trace_interaction(parameter,simulation):
    
def plot_heatmap_griewank(results,algorithms):
    from matplotlib import ticker
    font = {'family' : 'calibri',
        'weight' : 'normal',
        'size'   : 20}
    plt.rc('font', **font)  
    subplots=len(results)
    xticks=[-40,0,40]
    yticks=[-40,0,40]
    fig=plt.figure(figsize=(16,3))
    N = 2000
    x = np.linspace(-50.0, 50.0, N)
    y = np.linspace(-50.0, 50.0, N)
    
    x, y = np.meshgrid(x, y)
            
    z=1+ (x**2+y**2)/4000 - np.cos(x/np.sqrt(2))*np.cos(y/np.sqrt(3))
    #z = 100.0*(x - x**2.0)**2.0 + (1 - y)**2.0
    #
    #norm = cm.colors.Normalize(vmax=abs(z).max(), vmin=-abs(z).max())
    cmap = plt.get_cmap('autumn')
    #levels = np.linspace(-5, 5, 20)
    for i in range(subplots):
        ax  = plt.subplot(1,subplots,i+1)
        CS = ax.contourf(x, y, z,locator=ticker.LogLocator(),cmap=cmap)#,levels=levels)
        ax.plot(results[i]['par0'],results[i]['par1'],'ko-',alpha=0.1,markersize=1.9) 
        if i>0:
            ax.yaxis.set_ticks([])
        if i==0:
            ax.set_ylabel('y')
        ax.set_xlabel('x')
        ax.xaxis.set_ticks(xticks)   
        ax.set_title(algorithms[i])
    
    plt.tight_layout()  
    fig.savefig('test.png', bbox_inches='tight')  # <------ this
    fig.close()   
    
    
def plot_likelihood(results,evaluation,limit=None,sort=True):
    likes=calc_like(results,evaluation)    
    #likes=results['like']
    data=likes
    #if sort==True:    
    #Calc confidence Interval    
    mean = np.average(data)
    # evaluate sample variance by setting delta degrees of freedom (ddof) to
    # 1. The degree used in calculations is N - ddof
    stddev = np.std(data, ddof=1)
    from scipy.stats import t
    # Get the endpoints of the range that contains 95% of the distribution
    t_bounds = t.interval(0.999, len(data) - 1)
    # sum mean to the confidence interval
    ci = [mean + critval * stddev / np.sqrt(len(data)) for critval in t_bounds]
    print "Mean: %f" % mean
    print "Confidence Interval 95%%: %f, %f" % (ci[0], ci[1])    
    threshold=ci[1]
    happend=None
    bestlike=[data[0]]
    for like in data:
        if like<bestlike[-1]:
            bestlike.append(like)
        if bestlike[-1]<threshold and not happend:
            thresholdpos=len(bestlike)
            happend=True
        else:
            bestlike.append(bestlike[-1])
    if limit:
        plt.plot(bestlike,'k-')#[0:limit])
        plt.axvline(x=thresholdpos,color='r')
        plt.plot(likes,'b-')
        #plt.ylim(ymin=-1,ymax=1.39)
    else:
        plt.plot(bestlike)
        
def plot_parametertrace_algorithms(results,algorithmnames=None,parameternames=None,xticks=[0,2000,4000]):        
    font = {'family' : 'calibri',
        'weight' : 'normal',
        'size'   : 20}
    plt.rc('font', **font)   
    fig=plt.figure(figsize=(17,5))
    rep=len(results[0])
    subplots=len(results)
    rows=2
    for j in range(rows):
        for i in range(subplots):
            ax  = plt.subplot(rows,subplots,i+1+j*subplots)
            if j==0:
                data=results[i]['parx']
            if j==1:
                data=results[i]['pary']
                ax.set_xlabel(algorithmnames[i-subplots])
            
            ax.plot(data,'b-')
            ax.plot([1]*rep,'r--')
            ax.set_xlim(0,rep)
            ax.set_ylim(-10,10)            
            ax.xaxis.set_ticks(xticks)
            if i==0 and j==0:
                ax.set_ylabel('x')
                ax.yaxis.set_ticks([-5,0,5])
            if i==0 and j==1:
                ax.set_ylabel('y')    
                ax.yaxis.set_ticks([-5,0,5])
            if j==0:
                ax.xaxis.set_ticks([])
            if i>0:
                ax.yaxis.set_ticks([])
        
    plt.tight_layout()
    fig.savefig('test2.png', bbox_inches='tight')
    fig.close() 
    
def plot_parametertrace(results,parameternames=None):
    """
    Get a plot with all values of a given parameter in your result array.
    The plot will be saved as a .png file.
    
    :results: Expects an numpy array which should of an index "like" for likelihoods 
    :type: array   
    
    :parameternames: A List of Strings with parameternames. A line object will be drawn for each String in the List.
    :type: list
        
    :return: Plot of all traces of the given parameternames.
    :rtype: figure
    """  
    fig=plt.figure(figsize=(16,9))
    if not parameternames:
        parameternames=get_parameternames(results)
    names=''
    i=1
    for name in parameternames:
        ax = plt.subplot(len(parameternames),1,i)
        ax.plot(results['par'+name],label=name)
        names+=name+'_'
        ax.set_ylabel(name)
        if i==len(parameternames):
            ax.set_xlabel('Repetitions')
        if i==1:
            ax.set_title('Parametertrace')
        ax.legend()
        i+=1
    fig.savefig(names+'_trace.png')
    print 'The figure as been saved as "'+names+'trace.png"' 

def plot_posterior_parametertrace(results,parameternames=None,threshold=0.1):
    """
    Get a plot with all values of a given parameter in your result array.
    The plot will be saved as a .png file.
    
    :results: Expects an numpy array which should of an index "like" for likelihoods 
    :type: array   
    
    :parameternames: A List of Strings with parameternames. A line object will be drawn for each String in the List.
    :type: list
        
    :return: Plot of all traces of the given parameternames.
    :rtype: figure
    """  
    fig=plt.figure(figsize=(16,9))
    
    results=sort_like(results)
    if not parameternames:
        parameternames=get_parameternames(results)
    names=''
    i=1
    for name in parameternames:
        ax = plt.subplot(len(parameternames),1,i)
        ax.plot(results['par'+name][int(len(results)*threshold):],label=name)
        names+=name+'_'
        ax.set_ylabel(name)
        if i==len(parameternames):
            ax.set_xlabel('Repetitions')
        if i==1:
            ax.set_title('Parametertrace')
        ax.legend()
        i+=1
    fig.savefig(names+'_trace.png')
    print 'The figure as been saved as "'+names+'trace.png"'

def plot_posterior(results,evaluation,dates=None,ylabel='Posterior model simulation',xlabel='Time',likelihood='NSE',likelihoodmax=True,calculatelike=True,sort=True, bestperc=0.1):
    """
    Get a plot with the maximum likelihood of your simulations in your result 
    array.
    The plot will be saved as a .png file.
    
    Args:
        results (array): Expects an numpy array which should of an index "like" for 
              likelihoods and "sim" for simulations.
  
        evaluation (list): Should contain the values of your observations. Expects that this list has the same lenght as the number of simulations in your result array.
    Kwargs:
        dates (list): A list of datetime values, equivalent to the evaluation data.
        
        ylabel (str): Labels the y-axis with the given string.

        xlabel (str): Labels the x-axis with the given string.
                
        likelihood (str): Name of the Likelihood function used for the simulations.
        
        likelihoodmax (boolean): If True the maximum value of the likelihood will be searched. If false, the minimum will be searched.
        
        calculatelike (boolean): If True, the NSE will be calulated for each simulation in the result array.
    
    Returns: 
        figure. Plot of the simulation with the maximum likelihood value in the result array as a blue line and dots for the evaluation data.
    
    A really great idea. A way you might use me is
    >>> bcf.analyser.plot_bestmodelrun(results,evaluation, ylabel='Best model simulation')
        
    """


    plt.rc('font', **font)
    if sort:
        results=sort_like(results)
    if calculatelike:
        likes=calc_like(results)
        maximum=max(likes)
        par=get_parameters(results)
        sim=get_modelruns(results)
        index=likes.index(maximum)
        bestmodelrun=list(sim[index])
        bestparameterset=list(par[index])
        
    else:
        if likelihoodmax==True:
            index,maximum=get_maxlikeindex(results)
        else:
            index,maximum=get_minlikeindex(results)
        sim=get_modelruns(results)
        bestmodelrun=list(sim[index][0])#Transform values into list to ensure plotting
        bestparameterset=list(get_parameters(results)[index][0])

    parameternames=list(get_parameternames(results)    )
    bestparameterstring=''
    maxNSE=likelihoods.nashsutcliff(bestmodelrun,evaluation)
    for i in range(len(parameternames)):
        if i%8==0:
            bestparameterstring+='\n'
        bestparameterstring+=parameternames[i]+'='+str(round(bestparameterset[i],4))+','
    fig=plt.figure(figsize=(16,8))
    if dates is not None:
        chains=int(max(results['chain']))
        colors=list(cnames)
        random.shuffle(colors)        
#        for i in range(chains):
#            chain=np.where(results['chain']==i+1)
#            posteriorlen=int(len(results[chain]))/2
#            posterior_modelruns=list(get_modelruns(results[chain][posteriorlen:]))
#            for j in range(len(posterior_modelruns)):
#                plt.plot(dates,list(posterior_modelruns[j]),colors[i],alpha=.2)
        for s in sim[5000:]:
            plt.plot(dates,list(s),'c-',alpha=0.05)        
        plt.plot(dates,bestmodelrun,'b-',label='Simulations: '+likelihood+'='+str(round(maxNSE,4)))        
        plt.plot(dates,evaluation,'ro',label='Evaluation')
    else:
        for s in s:
            plt.plot(dates,list(s),'c-',alpha=0.05)
        plt.plot(bestmodelrun,'b-',label='Simulations: '+likelihood+'='+str(round(maxNSE,4)))
        plt.plot(evaluation,'ro',label='Evaluation')
    plt.legend()
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.ylim(0,70) #DELETE WHEN NOT USED WITH SOIL MOISTUR RESULTS
    plt.title('Maximum Likelihood of Simulations with '+bestparameterstring[0:-2])
#    plt.text(0, 0, bestparameterstring[0:-2],
#        horizontalalignment='left',
#        verticalalignment='bottom')
    fig.savefig('bestmodelrun.png')
    print 'The figure as been saved as "bestmodelrun.png"'
    

def plot_bestmodelrun(results,evaluation,dates=None,ylabel='Best model simulation',xlabel='Time',likelihood='NSE',likelihoodmax=True,calculatelike=True):
    """
    Get a plot with the maximum likelihood of your simulations in your result 
    array.
    The plot will be saved as a .png file.
    
    Args:
        results (array): Expects an numpy array which should of an index "like" for 
              likelihoods and "sim" for simulations.
  
        evaluation (list): Should contain the values of your observations. Expects that this list has the same lenght as the number of simulations in your result array.
    Kwargs:
        dates (list): A list of datetime values, equivalent to the evaluation data.
        
        ylabel (str): Labels the y-axis with the given string.

        xlabel (str): Labels the x-axis with the given string.
                
        likelihood (str): Name of the Likelihood function used for the simulations.
        
        likelihoodmax (boolean): If True the maximum value of the likelihood will be searched. If false, the minimum will be searched.
        
        calculatelike (boolean): If True, the NSE will be calulated for each simulation in the result array.
    
    Returns: 
        figure. Plot of the simulation with the maximum likelihood value in the result array as a blue line and dots for the evaluation data.
    
    A really great idea. A way you might use me is
    >>> bcf.analyser.plot_bestmodelrun(results,evaluation, ylabel='Best model simulation')
        
    """


    plt.rc('font', **font)       
    if calculatelike:
        likes=[]
        sim=get_modelruns(results)
        par=get_parameters(results)
        for s in sim:
            likes.append(likelihoods.nashsutcliff(s,evaluation))
        maximum=max(likes)
        index=likes.index(maximum)
        bestmodelrun=list(sim[index])
        bestparameterset=list(par[index])
        
    else:
        if likelihoodmax==True:
            index,maximum=get_maxlikeindex(results)
        else:
            index,maximum=get_minlikeindex(results)
        bestmodelrun=list(get_modelruns(results)[index][0])#Transform values into list to ensure plotting
        bestparameterset=list(get_parameters(results)[index][0])
        
    parameternames=list(get_parameternames(results)    )
    bestparameterstring=''
    maxNSE=likelihoods.nashsutcliff(bestmodelrun,evaluation)
    for i in range(len(parameternames)):
        if i%8==0:
            bestparameterstring+='\n'
        bestparameterstring+=parameternames[i]+'='+str(round(bestparameterset[i],4))+','
    fig=plt.figure(figsize=(16,8))
    if dates is not None:
        plt.plot(dates,bestmodelrun,'b-',label='Simulations: '+likelihood+'='+str(round(maxNSE,4)))        
        plt.plot(dates,evaluation,'ro',label='Evaluation')
    else:
        plt.plot(bestmodelrun,'b-',label='Simulations: '+likelihood+'='+str(round(maxNSE,4)))
        plt.plot(evaluation,'ro',label='Evaluation')
    plt.legend()
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.ylim(0,70) #DELETE WHEN NOT USED WITH SOIL MOISTUR RESULTS
    plt.title('Maximum Likelihood of Simulations with '+bestparameterstring[0:-2])
#    plt.text(0, 0, bestparameterstring[0:-2],
#        horizontalalignment='left',
#        verticalalignment='bottom')
    fig.savefig('bestmodelrun.png')
    print 'The figure as been saved as "bestmodelrun.png"'


def plot_bestmodelruns(results,evaluation,algorithms=None,dates=None,ylabel='Best model simulation',xlabel='Date',likelihoodmax=True,calculatelike=True):
    """
    Get a plot with the maximum likelihood of your simulations in your result 
    array.
    The plot will be saved as a .png file.
    
    Args:
        results (list of arrays): Expects list of numpy arrays which should of an index "like" for 
              likelihoods and "sim" for simulations.
  
        evaluation (list): Should contain the values of your observations. Expects that this list has the same lenght as the number of simulations in your result array.
    Kwargs:
        dates (list): A list of datetime values, equivalent to the evaluation data.
        
        ylabel (str): Labels the y-axis with the given string.

        xlabel (str): Labels the x-axis with the given string.
                
        likelihood (str): Name of the Likelihood function used for the simulations.
        
        likelihoodmax (boolean): If True the maximum value of the likelihood will be searched. If false, the minimum will be searched.
        
        calculatelike (boolean): If True, the NSE will be calulated for each simulation in the result array.
    
    Returns: 
        figure. Plot of the simulation with the maximum likelihood value in the result array as a blue line and dots for the evaluation data.
    
    A really great idea. A way you might use me is
    >>> bcf.analyser.plot_bestmodelrun(results,evaluation, ylabel='Best model simulation')
        
    """


    plt.rc('font', **font)
    fig=plt.figure(figsize=(17,8))
    colors=['grey', 'black', 'brown','red','orange', 'yellow','green','blue',]
    plt.plot(dates,evaluation,'ro',label='Evaluation data')
    for i in range(len(results)):       
        if calculatelike:
            likes=[]
            sim=get_modelruns(results[i])
            par=get_parameters(results[i])
            for s in sim:
                likes.append(likelihoods.lognashsutcliff(evaluation,list(s)))                                
                #likes.append(-likelihoods.rmse(evaluation,list(s)))
                #likes.append(likelihoods.nashsutcliff(evaluation,list(s)))
                #likes.append(likelihoods.agreementindex(evaluation,list(s)))
                                
            maximum=max(likes)
            index=likes.index(maximum)
            bestmodelrun=list(sim[index])
            bestparameterset=list(par[index])
            print bestparameterset
            
        else:
            if likelihoodmax==True:
                index,maximum=get_maxlikeindex(results[i])
            else:
                index,maximum=get_minlikeindex(results[i])
            bestmodelrun=list(get_modelruns(results[i])[index][0])#Transform values into list to ensure plotting
        
        maxLike=likelihoods.lognashsutcliff(evaluation,bestmodelrun)        
        #maxLike=likelihoods.nashsutcliff(evaluation,bestmodelrun)
        #maxLike=likelihoods.agreementindex(evaluation,bestmodelrun)
        
        if dates is not None:
            plt.plot(dates,bestmodelrun,'-',color=colors[i],label=algorithms[i]+': LogNSE='+str(round(maxLike,4)))        
            
        else:
            plt.plot(bestmodelrun,'-',color=colors[i],label=algorithms[i]+': AI='+str(round(maxLike,4))) 
            #plt.plot(evaluation,'ro',label='Evaluation data')
        plt.legend(bbox_to_anchor=(.0, 0), loc=3)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.ylim(15,50) #DELETE WHEN NOT USED WITH SOIL MOISTUR RESULTS

        fig.savefig('bestmodelrun.png')
        print 'The figure as been saved as "bestmodelrun.png"'

def plot_likelihoodtraces(results,evaluation,algorithms):
    font = {'family' : 'calibri',
        'weight' : 'normal',
        'size'   : 20}
    plt.rc('font', **font)   
    fig=plt.figure(figsize=(16,3))
    xticks=[5000,15000]
    
    for i in range(len(results)):
        ax  = plt.subplot(1,len(results),i+1)
        likes=calc_like(results[i],evaluation)  
        ax.plot(likes,'b-')
        ax.set_ylim(0,25)
        ax.set_xlim(0,len(results[0]))
        ax.set_xlabel(algorithms[i])
        ax.xaxis.set_ticks(xticks)
        if i==0:
            ax.set_ylabel('RMSE')
            ax.yaxis.set_ticks([0,10,20])   
        else:
            ax.yaxis.set_ticks([])        
        
    plt.tight_layout()
    fig.savefig('Like_trace.png')


def plot_regression(results,evaluation):
    fig=plt.figure(figsize=(16,9))
    simulations=get_modelruns(results)
    for sim in simulations:
        plt.plot(evaluation,list(sim),'bo',alpha=.05)
    plt.ylabel('simulation')
    plt.xlabel('evaluation')
    plt.title('Regression between simulations and evaluation data')
    fig.savefig('regressionanalysis.png')
    print 'The figure as been saved as "regressionanalysis.png"'
    
    
def plot_parameterInteraction(results):
    '''Input:  List with values of parameters and list of strings with parameter names
       Output: Dotty plot of parameter distribution and gaussian kde distribution'''
    parameterdistribtion=get_parameters(results)
    parameternames=get_parameternames(results)  
    df = pd.DataFrame(parameterdistribtion, columns=parameternames)
    pd.tools.plotting.scatter_matrix(df, alpha=0.2, figsize=(12, 12), diagonal='kde')
    plt.savefig('ParameterInteraction',dpi=300)    
    
    
def plot_allmodelruns(modelruns,observations,dates=None):
    '''Input:  Array of modelruns and list of Observations
       Output: Plot with all modelruns as a line and dots with the Observations
    ''' 
    fig=plt.figure(figsize=(16,9))
    ax = plt.subplot(1,1,1)
    if dates is not None:
        for i in range(len(modelruns)):
            if i==0:
                ax.plot(dates, modelruns[i],'b',alpha=.05,label='Simulations')
            else:            
                ax.plot(dates, modelruns[i],'b',alpha=.05)

    else:
        for i in range(len(modelruns)):
            if i==0:
                ax.plot(modelruns[i],'b',alpha=.05,label='Simulations')
            else:            
                ax.plot(modelruns[i],'b',alpha=.05)
    ax.plot(observations,'ro',label='Evaluation')
    ax.legend()
    ax.set_xlabel = 'Best model simulation'
    ax.set_ylabel = 'Evaluation points'
    ax.set_title  = 'Maximum Likelihood of Simulations'
    fig.savefig('bestmodel.png')
    print 'The figure as been saved as "Modelruns.png"' 
    
  
def plot_autocorellation(parameterdistribution,parametername):
    '''Input:  List of sampled values for one Parameter
       Output: Parameter Trace, Histogramm and Autocorrelation Plot'''
    fig=plt.figure(figsize=(16,9))
    ax = plt.subplot(1,1,1)
    pd.tools.plotting.autocorrelation_plot(parameterdistribution)
    plt.savefig('Autocorellation'+str(parametername),dpi=300)
    

def plot_gelman_rubin(r_hat_values):
    '''Input:  List of R_hat values of chains (see Gelman & Rubin 1992) 
       Output: Plot as seen for e.g. in (Sadegh and Vrugt 2014)'''
    fig=plt.figure(figsize=(16,9))
    ax = plt.subplot(1,1,1)
    ax.plot(r_hat_values)
    ax.plot([1.2]*len(r_hat_values),'k--')
    ax.set_xlabel='r_hat'
    
    	
def gelman_rubin(x):
    '''NOT USED YET'''
    if np.shape(x) < (2,):
        raise ValueError(
            'Gelman-Rubin diagnostic requires multiple chains of the same length.')
    try:
        m, n = np.shape(x)
    except ValueError:
        return [gelman_rubin(np.transpose(y)) for y in np.transpose(x)]
    # Calculate between-chain variance
    B_over_n = np.sum((np.mean(x, 1) - np.mean(x)) ** 2) / (m - 1)
    # Calculate within-chain variances
    W = np.sum(
        [(x[i] - xbar) ** 2 for i,
         xbar in enumerate(np.mean(x,
                                   1))]) / (m * (n - 1))
    # (over) estimate of variance
    s2 = W * (n - 1) / n + B_over_n
    # Pooled posterior variance estimate
    V = s2 + B_over_n / m
    # Calculate PSRF
    R = V / W
    return R


def plot_Geweke(parameterdistribution,parametername):
    '''Input:  Takes a list of sampled values for a parameter and his name as a string
       Output: Plot as seen for e.g. in BUGS or PyMC'''
    # perform the Geweke test
    Geweke_values = _Geweke(parameterdistribution)
    
    # plot the results
    fig = plt.figure()
    plt.plot(Geweke_values,label=parametername)
    plt.legend()
    plt.title(parametername + '- Geweke_Test')
    plt.xlabel('Subinterval')
    plt.ylabel('Geweke Test')
    plt.ylim([-3,3])
    
    # plot the delimiting line
    plt.plot( [2]*len(Geweke_values), 'r-.')
    plt.plot( [-2]*len(Geweke_values), 'r-.')
	

def _Geweke(samples, intervals=20):
    '''Calculates Geweke Z-Scores'''    
    length=len(samples)/intervals/2
    # discard the first 10 per cent
    first = 0.1*len(samples)
    
    # create empty array to store the results
    z = np.empty(intervals)
    
    for k in np.arange(0, intervals):
        # starting points of the two different subsamples
        start1 = first + k*length
        start2 = len(samples)/2 + k*length
                
        # extract the sub samples
        subsamples1 = samples[start1:start1+length]
        subsamples2 = samples[start2:start2+length]
        
        # calculate the mean and the variance
        mean1 = np.mean(subsamples1)
        mean2 = np.mean(subsamples2)
        var1  = np.var(subsamples1)
        var2  = np.var(subsamples2)
        
        # calculate the Geweke test
        z[k] = (mean1-mean2)/np.sqrt(var1+var2)    
    return z