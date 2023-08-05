.. vim: set fileencoding=utf-8 :
.. author: Ivana Chingovska <ivana.chingovska@idiap.ch>
.. date: Tue Jul  8 17:39:09 CEST 2014

.. antispoofing.evaluation documentation master file, created by
   sphinx-quickstart on Tue Jul  8 17:39:28 CEST 2014
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========
User guide
==========

This User Guide consists of three parts:

1. **Part 1**: we are going to show how to use the EPSC framework within your own code, having lists of real access, zero-effort impostors and spoofing attack scores.

2. **Part 2**: we are going to show how to use the scripts to evaluate a **single** verification system. For demonstration purposes, we are going to use a hypothetical verification system. This means, the score files we are going to use will be syntetically generated. However, note that you can use the same scripts to generate plots for real verification system. All that is needed are the *4 score files* for that system.

3. **Part 3**: we are going to show how to call scripts to compare several verification systems by different criteria (eg. the baseline verification system used, the anti-spoofing system used, or the fusion methodology). We are going to demonstrate this on real verification systems (the ones which are used in the paper): GMM, LGBPHS, GJet and ISV.

Let's first give some prerequisities. It is important to emphasize that this satellite package enables evaluation biometric verification systems under spoofing attacks. The scripts in this method, thus, depend on score files, where the scores of the verification system are written. These scores can be before or after a fusion with an anti-spoofing system. 

The score files need to be in a special format which is used in Bob: `4-column format file <http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/measure/generated/bob.measure.load.four_column.html?highlight=four%20column#bob.measure.load.four_column>`_ . Each row of the file corresponds to one entry to the system, while the columns correspond to:

1. claimed identity (string)
2. real identity (string)
3. sample filename (string)
4. score (string)

A real access sample have the same real and claimed identity (1st and 2nd column). A zero-effort impostor will have different real and claimed identity (1st and 2nd column). A spoofing attack will have different real and claimed identity (1st column will be the claimed identity, 2nd column will be the keyword ``spoof``.

To generate the plots, we need **4 score files**:
 - score file for *development* set, **licit** scenario
 - score file for *test* set, **licit** scenario
 - score file for *development* set, **spoof** scenario
 - score file for *test* set, **spoof** scenario.
  
  The files for the licit scenario contain scores for real accesses and zero-effort impostors only, while the files for the spoof scenario contain scores for real accesses and spoofing attacks only. The scores for the development set will be used to compute decision thresholds and tune the metrics, while the scores for the test set will be the one to be evaluated.

Part 1: Using EPSC framework
----------------------------

To use the EPSC framework within your own code, you need 4 sets of scores (numpy.array) for each of the subsets (development and test): 
- positives for licit scenario (real access scores)
- negatives for licit scenario (zero-effort impostor scores)
- positives for spoof scenario (real access scores, usually the same as the positives for the licit scenario)
- negatives for spoof scenario (spoofing attacks).

These can be extracted from the 4-column format files, and parsing these files is the first step towards evaluation. However, you can use the framework even if you have your own sources for these score sets. 

To use the EPSC framework, you first need to import the ``error_utils`` module::

  $ from utils import error_utils
  
To obtain the EPSC values to be plotted, first you have to calculate the thresholds for a range of values of the weight parameters \omega and \beta, using the method ``epsc_thresholds()``. By default, these parameters will span 100 values in the range [0, 1]. This is useful for computing 3D EPSC. You can set one of them to have one or more fixed values, and that is necessary for computing 2D EPSC curves. To compute the thresholds, you need to use the scores from the development set. You can also specify number of points (values of \omega and/or \beta) as well threshold criteria (EER or Minimum HTER). 

In our example, we will fix the parameter beta=0.5 and we will be plotting EPSC for varying parameter omega. The code below computes the tresholds for 100 values of \omega.

.. code-block:: python
  
  omega, beta, thrs = error_utils.epsc_thresholds(licit_neg_dev, licit_pos_dev, spoof_neg_dev, spoof_pos_dev, points=100, criteria='eer', beta=(0.5,))

Having the values of the omega and beta parameters and the corresponding thresholds, you can calculate EPSC related error rates on the test set, using the method: ``epsc_error_rates()``. You can also calculate more relevant error rates, using the method: ``all_error_rates()``. 

.. code-block:: python
  
  [far_w, wer_w] = error_utils.epsc_error_rates(licit_neg_test, licit_pos_test, spoof_neg_test, spoof_pos_test, thrs, omega, beta) 
  [frr, far, sfar, far_w, hter_w] = error_utils.all_error_rates(licit_neg_test, licit_pos_test, spoof_neg_test, spoof_pos_test, thrs, omega, beta) 

Now you can plot any error with respect to the varying error parameter, in this example \omega. For example, if you use `Matplotlib <http://www.matplotlib.org>`_ , plotting of WER_w  (in [%]) will look like this:

.. code-block:: python

  mpl.plot(omega, [100.*k for k in wer_w], label = "WER_w")

Finally, you can also compute Area Under the EPSC (AUE) value using the method ``calc_aue()``, in any range for the weight parameter between 0 and 1. In the code below, it is computed for the range [0.2, 0.5].

.. code-block:: python
  
  aue = error_utils.calc_aue(licit_neg_test, licit_pos_test, spoof_neg_test, spoof_pos_test, thrs, omega, beta, l_bound=0.2, h_bound=0.5, var_param='omega')
  
Please refer to the Reference Manual for detailed documentation of these methods.   


Part 2: Evaluation of a single verification system
--------------------------------------------------

This section explains how to use the ready scripts we provide for evaluation and plotting of different plots ona  single verification system. These scripts are using the 4 4-column score files which were explained before.

We are going to illustrate the evaluation scripts using hypothetical verifications scores that we are going to generate. Here are the functionalities you can use:

1. **Generating hypothetical verification scores**

  If you don't have 4-column score files of a real verification system at hand, you can generate hypotehtical ones using ``./bin/score_distr_generator.py``. The hypothetical verification scores are generated from three Gaussian distributions: for the real accesses, zero-effort impostors and spoofing attacks. To generate them, call::

    $ ./bin/score_distr_generator.py --mean_real 3 --mean_imp 0 --mean_spoof 2 --outdir dir-hpt
  
  This method generates real access scores from a Gaussian distribution with mean 3, zero-effort impostors from a Gaussian with mean 0 and spoofing attacks from a Gaussian with mean 2. It write the generated scores in the four score files described above. These files are: ``dir-hpt/licit/scores-dev``, ``dir-hpt/licit/scores-test``, ``dir-hpt/spoof/scores-dev`` and ``dir-hpt/spoof/scores-test``. Type ``--help`` after the command to see all the available options.

2. **Computing bare error rates**

  You can compute numerical error rates on the scores (no plots), by first computing a decision threshold::

    $ ./bin/eval_threshold.py --scores dir-hpt/licit/scores-dev --criterium eer
  
  The above call conforms with Evaluation Methodology 2, where, to compute the decision threshold, we use the devel scores of the licit scenario. The threshold (float) printed out by the above method, can be used to compute error rates. Let's assume the obtained threshold is 1.46. To compute the error rates call::

    $ ./bin/apply_threshold.py --scores dir-hpt/licit/scores-test --threshold 1.46
    $ ./bin/apply_threshold.py --scores dir-hpt/spoof/scores-test --threshold 1.46
  
  The first call of the script will compute error rates on the test set of the licit protocol, giving FAR and FRR values. The second call will compute error rates on the test set of the spoof protocol, giving SFAR values.

  Type ``--help`` after any of these commands to see all the available options.

3. **Plotting different plots**

  You need to use the script ``./bin/plot_on_demand.py`` to plot various cruves and visualizations. There are a total of 13 possible plots: DET curves, score distribution plots, EPC curves for licit and spoof protocol, as well as EPSC curves for WER and SFAR. The command argument you need to set to demand a particular plot is ``-i`` and can be one or more integers between 1 and 13 (depending on the demanded plot(s)). Type ``--help`` after the command to see the correspondence between the value of the argument and the plot.

  The basic call of the script needs to get at least the four score files explained before as command line arguments. The call of the script below gives an example how to plot score distribution plots with decision threshold and probability of success line, using EER threshold criteria, and dump the plot in ``output.pdf``::

    $ ./bin/plot_on_demand.py dir-hpt/licit/scores-dev dir-hpt/licit/scores-test dir-hpt/spoof/scores-dev dir-hpt/spoof/scores-test -c eer -o output.pdf -i 7 
  
  Using this script, you can plot 2D or 3D EPSC curves. If you plot a 2D EPSC, you need to specify the name of the varying parameter (omega or beta) using the ``--vp`` argument, as well as the value of the fixed parameter using the ``--fp`` argument. For example, to plot WER using EPSC with varying omega and beta=0.7, call::

    $ ./bin/plot_on_demand.py dir-hpt/licit/scores-dev dir-hpt/licit/scores-test dir-hpt/spoof/scores-dev dir-hpt/spoof/scores-test -c eer --vp omega --fp 0.7 -o output.pdf -i 10
  
  Calling the script for other plots should be analogous. Also, there are other options in the script, that will set the title you like, plot in grey-scale etc. Type ``--help`` after the command to see explanations about all the available options.

  There is one additional value for the ``-i`` parameter, which does not plot a meaningful plot, but only a legend for the score distribution plot outside of the plot.

4. **Plotting EPSC with different parameters**

  Using the script ``./bin/plot_epsc_on_demand.py``, you can plot several 2D EPSC curves on one plot, each of which has different values for the varying parameter. To plot this plot, you need to specify the name of the varying parameter (omega or beta) using the ``--vp`` argument, as well as the one or more values of the fixed parameter using the ``--fp`` argument. Using the ``-i`` parameter, you can specify an integer coding which type of EPSC you want plotted: one showing WER or one showing SFAR. To plot WER for varying omega and three values of beta=(0.3, 0.5, 0.7), call::

    $ ./bin/plot_epsc_on_demand.py dir-hpt/licit/scores-dev dir-hpt/licit/scores-test dir-hpt/spoof/scores-dev dir-hpt/spoof/scores-test -c eer --vp omega --fp 0.3 0.5 0.7 -o output.pdf -i 1
  
  Type ``--help`` after the command to see explanations about all the available options. 

  Similarly as for ``./bin/plot_on_demand.py``, there is one additional value for the ``-i`` parameter, which does not plot a meaningful plot, but only a legend outside of the plot.
  
5. **Computing Area Under EPSC value**

  To do this, use the script ``./bin/calc_aue_value.py``. Again, you need to specify the name of the varying parameter (omega or beta) using the ``--vp`` argument, as well as the one or more values of the fixed parameter using the ``--fp`` argument. Additionally, you can set the low and high bound of integrations. The command below computes AUE between 0 and 0.1 for EPSC for varying omega and beta=0.5::

    $ ./bin/calc_aue_value.py dir-hpt/licit/scores-dev dir-hpt/licit/scores-test dir-hpt/spoof/scores-dev dir-hpt/spoof/scores-test--vp omega --fp 0.5 -c eer --lb 0 --hb 0.1


Part 3: Comparison of verification systems by different criteria
----------------------------------------------------------------

This section requires that you have access to the real system verification scores that we WILL provide soon.

This section will demonstrate how to plot 2D EPSC figures where several verification systems are compared by different criteria: Fig.9, Fig.10, Fig.11 and Fig.12 of the paper and Fig.5 and Fig.6 from the Appendix. The scripts to do this comparison need to use 4 score files for each compared system. Intead of giving them as parameters, we give just the base directories where the scores are stored, as well as the name of the compared methods. The scripts figure out the full path to the score files by themselves.

The scripts explained here are written IN PARTICULAR for the following verification systems: UBMGMM, LGBPHS, EBGM and ISV; the following anti-spoofing systems: LBP, LBP-TOP, MOTION and ALL; and the following fusion methods: SUM, LLR and PLR. On request [#]_, we can provide the verification scores for all of these systems, so that you can reproduce the plots in the paper [#]_. 

.. Together with this satellite package, in the directory ``facereclib-readyscores``, we provide the verification scores for all of these systems, so that you can reproduce the plots in the paper. They are organized in two subdirectories: ``baseline`` containing the scores of the baseline verification algorithms before fusion, and ``fvas_fused`` containing the scores after fusion.

The face verificaiton scores in ``facereclib-readyscores`` are generated using `FaceRecLib <https://pypi.python.org/pypi/facereclib>`_. The anti-spoofing scores are generated using the `LBP <https://pypi.python.org/pypi/antispoofing.lbp>`_, `LBP-TOP <https://pypi.python.org/pypi/antispoofing.lbptop>`_ and `MOTION <https://pypi.python.org/pypi/antispoofing.motion>`_ satellite packages. The fused scores are generated using the `fusion <https://pypi.python.org/pypi/antispoofing.fusion_faceverif>`_ satellite package.

If you want to use the scripts explained below for OTHER systems, you need to modify them accordingly.:

1. **Comparing verification systems w.r.t. the baseline verification algorithm**

  You can compare verification systems using the script ``./bin/plot_faceverif_comparison.py``. You can compare baseline verification systems before fusion with anti-spoofing system, or fused systems. Note that, since the plots are 2D, you need to specify the name of the varying parameter (omega or beta) using the ``--vp`` argument, as well as the one or more values of the fixed parameter using the ``--fp`` argument. You can plot EPSC showing WER or SFAR, depending on the ``-i`` option. 
  
  To compare baseline verification algorithms using the WER of the systems on an EPSC curve (with the default ``--vp`` and ``--fp`` options), call::
  
    $ ./bin/plot_faceverif_comparison.py --bf facereclib-readyscores/baselines/ --baseline -c eer -i 1
    
  If you want to compare fused systems by the baseline verification algorithm they use, first you need to precise the antispoofing algorithm used in the fusion (``--as`` option, possible values: LBP, LBP-TOP, MOTION and ALL) and the fusion algorithm (``--fu`` option, possible values: SUM, LLR and PLR). For example, to compare systems fused with LBP-TOP counter-measure with PLR fusion, using the WER of the systems on an EPSC curve (with the default ``--vp`` and ``--fp`` options), call::
  
    $ ./bin/plot_faceverif_comparison.py --bf facereclib-readyscores/baselines/ -c eer --as LBP-TOP --fu PLR --ba facereclib-readyscores/fusion-fvas/ -o output.pdf -i 1
  
  Type ``--help`` after the command to see all its options.
  
2. **Comparing fused verification systems w.r.t. the anti-spoofing system that protects them**

  This comparison can be made using the script ``./bin/plot_countermeasures_comparison.py``. You need to precise the face verification algorithm (``--fv`` option, possible values: GMM, LGBPHS, GJet and ISV) and the fusion algorithm (``--fu`` option, possible values: SUM, LLR and PLR). For example, to compare ISV baseline fused with different anti-spoofing methods using PLR fusion, using WER on EPSC (with the default ``--vp`` and ``--fp`` options) call::
  
    $ ./bin/plot_countermeasures_comparison.py --fu PLR --fv ISV --bf facereclib-readyscores/baselines/ --ba facereclib-readyscores/fusion-fvas/ -c eer -o output.pdf -i 1

  Type ``--help`` after the command to see all its options.
  
3. **Comparing fused verification systems w.r.t. the fusion method**
  
  This comparison can be made using the script ``./bin/plot_fusionmethods_comparison.py``. You need to precise the face verification algorithm (``--fv`` option, possible values: GMM, LGBPHS, GJet and ISV) and the antispoofing algorithm used in the fusion (``--as`` option, possible values: LBP, LBP-TOP, MOTION and ALL). For example, to compare ISV baseline fused with different anti-spoofing methods using PLR fusion, using WER on EPSC (with the default ``--vp`` and ``--fp`` options) call::
  
    $ ./bin/plot_fusionmethods_comparison.py --as LBP-TOP --fv ISV --bf facereclib-readyscores/baselines/ --ba facereclib-readyscores/fusion-fvas/ -c eer -o output.pdf -i 1
    
  Type ``--help`` after the command to see all its options.
  
Note that, for each of the above commands, it is possible to change the varying parameter of the EPSC (omega or beta) with the ``--vp`` option, and the value of the fixed parameter with the ``--fp`` option.


.. [#] Contact ivana.chingovska@idiap.ch
.. [#] The verification scores that we distribute on request will be situated in a directory ``facereclib-readyscores``. They will be are organized in two subdirectories: ``baseline`` containing the scores of the baseline verification algorithms before fusion, and ``fvas_fused`` containing the scores after fusion.
