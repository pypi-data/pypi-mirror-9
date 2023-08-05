#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue Feb  4 15:33:15 CET 2014

"""Plots different types of EPSC plots as demanded by the user for faceverif and anti-spoofing systems fused using AND fusion (i.e. parallel ones). The numbers of the plots to be plotted are given as a command line argument. Note that the dev score files need to be under different protocol then the test score files: dev score files are generated with opt3, while test score files are generated with opt2 of the script antispoofing.fusion-faceverif/and_decision_fusion_to4col.py"""

import os
import sys
from matplotlib import rc
rc('text',usetex=1)
import matplotlib.pyplot as mpl
import bob.measure
import numpy as np
import argparse

import matplotlib.font_manager as fm

from ..utils import error_utils


def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('baseline_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (development set)')
  parser.add_argument('baseline_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, LICIT scenario (test set)')
  parser.add_argument('overlay_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; development set)')
  parser.add_argument('overlay_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the verification system, SPOOF scenario (spoofing attacks; test set)')
  parser.add_argument('-c', '--criteria', metavar='STR', type=str,
      dest='criteria', default="hter", help='Criteria for threshold selection', choices=('eer', 'hter', 'wer'))
  parser.add_argument('-b', '--beta', metavar='STR', type=float,
      dest='beta', default=0.5, help='Beta parameter for balancing between real accesses and all negatives (impostors and spoofing attacks). Note that this parameter will be ignored if the chosen criteria is "hter". ', nargs='+')    
      
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('--norealdata', action='store_true',help='If True, will annotate the plots hypothetically, instead of with real data values of the calculated error rates.')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - HTER_w curves; 2 - WER_wb curves; 3 - SFAR curves', nargs='+')

  args = parser.parse_args()

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  color_mapping = {0:'green', 1:'blue', 2:'red', 3:'magenta', 4:'cyan'}

  # Plot 1: EPSC - WER-w (in the past, this option was used to compute HTER_w)
  # -------------------------------------------------
  
  if 1 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta = args.beta)

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_wb, hter_w
    
      mpl.rcParams.update({'font.size': 18})
    
    for bindex, b in enumerate(args.beta):
      mpl.plot(omega, 100. * errors[4][bindex,:], color=color_mapping[bindex], label = r"$\beta$=%.1f" % b, linewidth=4)
      
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"WER$_{\omega,\beta}$ (\%)")

    #mpl.title(r"EPSC with %s criteria: WER$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    #mpl.legend(prop=fm.FontProperties(size=18), loc = 4)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
   
  # Plot 2: EPSC - HTER
  # -------------------------------------------------
  if 2 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta = args.beta)

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_wb, hter_w
    
    mpl.rcParams.update({'font.size': 18})
    
    for bindex, b in enumerate(args.beta):
      mpl.plot(omega, 100. * errors[5][bindex,:], color=color_mapping[bindex], label = r"$\beta$=%.1f" % b, linewidth=4)
      
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"HTER$_{\omega,\beta}$ (\%)")

    mpl.title(r"EPSC with %s criteria: HTER$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
   
   
  # Plot 3: EPSC - SFAR
  # -------------------------------------------------
  if 3 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta = args.beta)

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_wb, hter_w
    
    mpl.rcParams.update({'font.size': 18})
    
    for bindex, b in enumerate(args.beta):
      mpl.plot(omega, 100. * errors[2][bindex,:], color=color_mapping[bindex], label = r"$\beta$=%.1f" % b, linewidth=4)
      
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"SFAR$_{\omega,\beta}$ (\%)")

    #mpl.title(r"EPSC with %s criteria: SFAR$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    #mpl.legend(prop=fm.FontProperties(size=18), loc=4)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
  
  
  # Plot 10: Dummy legend for several curves, each of which is for different value of \beta
  # -------------------------------------------------
  
  if 10 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta = args.beta)

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_wb, hter_w
    
    mpl.rcParams.update({'font.size': 18})
    
    for bindex, b in enumerate(args.beta):
      mpl.plot(omega, 100. * errors[4][bindex,:], color=color_mapping[bindex], label = r"$\beta$=%.1f" % b, linewidth=4)
      
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"WER$_{\omega,\beta}$ (\%)")

    #mpl.title(r"EPSC with %s criteria: WER$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    #mpl.legend(prop=fm.FontProperties(size=18), loc = 4)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    mpl.grid()  

    pp.savefig() 
  
  
    
  pp.close() # close multi-page PDF writer
 

if __name__ == '__main__':
  main()
