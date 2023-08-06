=================
Purpose
=================

SPOTPY is a Python tool that enables the use of calibration, uncertainty 
and sensitivity analysis techniques for almost every environmental model.
 
The simplicity and flexibility enables the use and test of different 
algorithms without the need of complex codes::

	sampler = spotpy.algorithms.sceua(model_setup())     # Initialize your model with a setup file
	sampler.sample(10000)                                # Run the model
	results = sampler.getdata()                          # Load the results
	spotpy.analyser.plot_parametertrace(results)         # Show the results


=================
Features
=================

Complex algorithms bring complex tasks to link them with a model. 
We want to make this task as easy as possible. 
Some features you can use with the SPOTPY package are:

* Fitting models to evaluation data with different algorithms. 
  Available algorithms are: 
  
  * Monte Carlo (`MC`)
  * Markov-Chain Monte-Carlo (`MCMC`)
  * Maximum Likelihood Estimation (`MLE`)
  * Latin-Hypercube Sampling (`LHS`) 
  * Simulated Annealing (`SA`)
  * Shuffled Complex Evolution Algorithm (`SCE-UA`)
  * Differential Evolution Adaptive Metropolis Algorithm (`DE-MCz`) 
  * RObust Parameter Estimation (`ROPE`).
  * Fourier Amplitude Sensitivity Test (`FAST`)

* Wide range of likelihood functions to validate the sampled results. Available Lieklihoods are
  Bias, Nash-Sutcliff (`NSE`), log Nash-Sutcliff (`logNSE`), Logarithmic probability (`logp`), Correlation Coefficient (`r`),
  Coefficient of Determination (`r^2`), Mean Squared Error (`MSE`), Root Mean Squared Error (`RMSE`), Mean Absolute Error (`MAE`),
  Relative Root Mean Squared Error (`RRMSE`), Agreement Index (`AI`), Covariance, Decomposed MSE (`dMSE`).

* Prebuild parameter distribution functions: Uniform, Normal, logNormal, Chisquare,
  Exponential, Gamma, Wald, Weilbull

* Wide range to adapt algorithms to perform uncertainty-, sensitivity analysis or calibration
  of a model.

* Multi-objective support
 
* MPI support for fast parallel computing

* A progress bar monitoring the sampling loops. Enables you to plan your coffee brakes.

* Use of NumPy functions as often as possible. This makes your coffee brakes short.

* Different databases solutions: `ram` storage for fast sampling a simple , `csv` tables
  the save solution for long duration samplings.

* Automatic best run selecting and plotting

* Parameter trace plotting

* Parameter interaction plot including the Gaussian-kde function

* Regression analysis between simulation and evaluation data

* Posterior distribution plot

* Convergence diagnostics with Gelman-Rubin and the Geweke plot

=================
Install
=================

Installing SPOTPY is easy. Just use:

	pip install spotpy

Or, after downloading the source code:

Linux:

	sudo python setup.py install

Windows (after making sure python is in your path):

	python setup.py install