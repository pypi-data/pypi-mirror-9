.. vim: set fileencoding=utf-8 :
.. author: Ivana Chingovska <ivana.chingovska@idiap.ch>
.. date: Tue Jul  8 17:37:31 CEST 2014

.. antispoofing.evaluation documentation master file, created by
   sphinx-quickstart on Tue Jul  8 17:40:07 CEST 2014
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to antispoofing.evaluation's documentation!
===================================================

This package provides methods for evaluation of biometric verification systems under spoofing attacks. The evaluation is based on the Expected Performance and Spoofability Curve (EPSC). Using this package, you can compute thresholds based on EPSC, compute various error rates and plot various curves related to EPSC. 

Besides providing methods for plotting EPSC within your own scripts, this package brings several scripts that you can use to evaluate your own verification system from several perspectives. For example, you can: 
  - evaluate the threshold of a classification system on the development set
  - apply the threshold on an evaluation or any other set to compute different error rates
  - plot score distributions
  - plot different performance curves (DET, EPC and EPSC)

Furthermore, you can generate hypothetical data and use them to exemplify the above mentioned functionalities.

Finally, several scripts enable you to evaluate 4 state-of-the-art face verification systems, before and after they are fused with an anti-spoofing system for better robustness to spoofing. The scripts enable you to plot the relevant curves of the systems together and compare them.

You can continue reading the documentation of the methods providing the EPSC functionality in the Reference Manual, or see how to use them, as well as how to run the evaluation of the face verification systems using the User Guide.

.. toctree::
   :maxdepth: 2
   
   reference
   userguide


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

