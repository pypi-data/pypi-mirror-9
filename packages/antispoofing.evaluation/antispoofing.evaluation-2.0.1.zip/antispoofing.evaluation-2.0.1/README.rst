==================================================================
Evaluation methods for verification systems under spoofing attacks
==================================================================

This package provides methods for evaluation of biometric verification systems under spoofing attacks. The evaluation is based on the Expected Performance and Spoofability Curve (EPSC). Using this package, you can compute thresholds based on EPSC, compute various error rates and plot various curves related to EPSC. 

Besides providing methods for plotting EPSC within your own scripts, this package brings several scripts that you can use to evaluate your own verification system (fused with an anti-spoofing system or not) from several perspectives. For example, you can: 
  - evaluate the threshold of a classification system on the development set
  - apply the threshold on an evaluation or any other set to compute different error rates
  - plot score distributions
  - plot different performance curves (DET, EPC and EPSC)

Furthermore, you can generate hypothetical data and use them to exemplify the above mentioned functionalities.

.. Finally, several scripts enable you to compare 4 state-of-the-art face verification systems, before and after they are fused with an anti-spoofing system for better robustness to spoofing. These systems are the ones that we use in our paper (to be announces soon), and have the following shortcuts: GMM, LBGPHS, GJet, and ISV, fused with different anti-spoofing systems using various fusion techniques. The scripts enable you to plot the relevant curves of the systems together and compare them.

If you use this package and/or its results, please cite the following
publication:

1. Our original paper on biometric evaluation (title, pdf and bibtex to be announced soon)::
 
    @ARTICLE{Chingovska_IEEETIFS_2014,
       author = {Chingovska, Ivana and Anjos, Andr{\'{e}} and Marcel, S{\'{e}}bastien},
       title = {Biometrics Evaluation Under Spoofing Attacks},
       journal = {IEEE Transactions on Information Forensics and Security},
       year = {2014},
    }
 
2. Bob_ as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
        author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
    }

If you wish to report problems or improvements concerning this code, please
contact the authors of the above mentioned papers.

Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.evaluation
  <http://pypi.python.org/pypi/antispoofing.evaluation>`_ to download the latest
  stable version of this package. Then, extract the .zip file to a folder of your choice.

The ``antispoofing.evaluation`` package is a satellite package of the free signal processing and machine learning library Bob_. This dependency has to be downloaded manually. This version of the package depends on Bob_ version 2 or greater. To install `packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_, please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_. For Bob_ to be able to work properly, some dependent Bob packages are required to be installed. Please make sure that you have read the Dependencies for your operating system.

The most simple solution is to download and extract ``antispoofing.evaluation`` package, then to go to the console and write::

  $ cd antispoofing.evaluation
  $ python bootstrap-buildout.py
  $ bin/buildout

This will download all required dependent Bob_ and other packages and install them locally. 


Using the package
-----------------

After instalation of the package, go to the console and type::

  $ ./bin/sphinx-build doc sphinx

Now, the full documentation of the package, including a User Guide, will be availabe in ``sphinx/index.html``.

Problems
--------

In case of problems, please contact ivana.chingovska@idiap.ch

.. _bob: http://www.idiap.ch/software/bob
.. _idiap: http://www.idiap.ch
