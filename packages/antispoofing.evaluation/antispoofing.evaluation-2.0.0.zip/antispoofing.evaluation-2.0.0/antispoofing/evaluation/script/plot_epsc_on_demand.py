#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Sun Jan 26 20:23:05 CET 2014
"""Plots different types of EPSC plots (WER_wb or SFAR) as demanded by the user, parameterized by one of the parameters. The other parameter is fixed to one or more values given as command line argument. 
"""

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
      dest='criteria', default="eer", help='Criteria for threshold selection', choices=('eer', 'hter', 'wer'))  
   
  parser.add_argument('--vp', '--var_param', metavar='STR', type=str,
      dest='var_param', default='omega', help='Name of the varying parameter', choices=('omega','beta'))    
  parser.add_argument('--fp', '--fixed_param', metavar='STR', type=float,
      dest='fixed_param', default=(0.5,) , help='Value of the fixed parameter', nargs='+')     
      
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('--norealdata', action='store_true',help='If True, will annotate the plots hypothetically, instead of with real data values of the calculated error rates.')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - WER_wb curves; 2 - SFAR curves', nargs='+')

  args = parser.parse_args()

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in grey-scale
    color_mapping = {0:'black', 1:'black', 2:'black', 3:'black', 4:'black'}
    line_mapping = {0:'--', 1:'-', 2:':', 3:'-.', 4:' '}
  else:  
    color_mapping = {0:'green', 1:'blue', 2:'red', 3:'magenta', 4:'cyan'}
    line_mapping = {0:'-', 1:'-', 2:'-', 3:'-', 4:'-'}

  # Plot 1: EPSC - WER-w (in the past, this option was used to compute HTER_w)
  # -------------------------------------------------
  
  if 1 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list as 2D numpy.ndarrays in the following order: frr, far, sfar, far_w, wer_wb, hter_wb
    
    for index, i in enumerate(args.fixed_param):
      mpl.rcParams.update({'font.size': 18})
    
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[4][index,:], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\beta$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\omega$")
      else:  
        mpl.plot(beta, 100. * errors[4][:,index], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\omega$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\beta$")    
            
    mpl.ylabel(r"WER$_{\omega,\beta}$ (\%)")

    mpl.title(r"EPSC with %s criteria: WER$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=18), loc = 4)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
   
  # Plot 2: EPSC - SFAR
  # -------------------------------------------------
  if 2 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
       
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list as 2D numpy.ndarrays in the following order: frr, far, sfar, far_w, wer_wb, hter_wb
    
    for index, i in enumerate(args.fixed_param):
      mpl.rcParams.update({'font.size': 18})
    
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[2][index,:], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\beta$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\omega$")
      else:  
        mpl.plot(beta, 100. * errors[2][:,index], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\omega$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\beta$")  
      
    mpl.ylabel("SFAR (\%)")

    #mpl.title(r"EPSC with %s criteria: SFAR" % (criteria.upper()) if args.title == "" else args.title)

    #mpl.legend(prop=fm.FontProperties(size=18), loc = 4)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
  
  
  # Plot 10: Dummy legend for several curves, each of which is for different value of the fixed parameter
  # -------------------------------------------------
  
  if 10 in args.demandedplot:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list as 2D numpy.ndarrays in the following order: frr, far, sfar, far_w, wer_wb, hter_wb
    
    for index, i in enumerate(args.fixed_param):
      mpl.rcParams.update({'font.size': 18})
      
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[4][index,:], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\beta$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\omega$")
      else:  
        mpl.plot(beta, 100. * errors[4][:,index], color=color_mapping[index], linestyle=line_mapping[index], label = r"$\omega$=%.1f" % i, linewidth=4)
        mpl.xlabel(r"Weight $\beta$")    
            
    mpl.ylabel(r"WER$_{\omega,\beta}$ (\%)")

    mpl.title(r"EPSC with %s criteria: WER$_{\omega,\beta}$" % (criteria.upper()) if args.title == "" else args.title)

    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=len(args.fixed_param), mode="expand", borderaxespad=0., prop=fm.FontProperties(size=18))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()  
  
  
    
  pp.close() # close multi-page PDF writer
 

if __name__ == '__main__':
  main()
