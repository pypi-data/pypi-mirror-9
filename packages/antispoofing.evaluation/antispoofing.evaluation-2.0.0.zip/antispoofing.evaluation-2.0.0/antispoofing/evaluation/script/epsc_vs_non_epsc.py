#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue Feb 11 14:39:49 CET 2014

"""Plot HTER_w and SFAR for a system using EPSC and not using EPSC (i.e. using Methodology 2).
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
  parser.add_argument('-b', '--beta', metavar='STR', type=float,
      dest='beta', default=0.5, help='Beta parameter for balancing between real accesses and all negatives (impostors and spoofing attacks). Note that this parameter will be ignored if the chose criteria is "hter". ')    
      
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('--norealdata', action='store_true',help='If True, will annotate the plots hypothetically, instead of with real data values of the calculated error rates.')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - HTER_w; 2 - SFAR', nargs='+')

  args = parser.parse_args()

  if args.criteria == 'eer':
    report_text = "EER"
  else:
    report_text = "Min.HTER"

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  # setting up the color and style-schemes
  if args.nocolor: # plot in grey-scale
    color_scheme = {'genuine':'black', 'impostors':'black', 'spoofs':'white', 'line':'black'}
    linestyle_scheme = {'line1':'-', 'line2':'dotted'}
    linecolor_scheme = {'line1':'black', 'line2':'black'}
    alpha_scheme = {'genuine':0.4, 'impostors':0.8, 'spoofs':0.6}
    hatch_scheme = {'genuine':None, 'impostors':None, 'spoofs':'//'} 
  else: # plot in color  
    color_scheme = {'genuine':'blue', 'impostors':'red', 'spoofs':'black', 'line':'green'}
    linestyle_scheme = {'line1':'-', 'line2':'-'}
    linecolor_scheme = {'line1':'blue', 'line2':'red'}
    alpha_scheme = {'genuine':0.6, 'impostors':0.8, 'spoofs':0.4}
    hatch_scheme = {'genuine':None, 'impostors':None, 'spoofs':None}    


  # Plot 1: EPSC - WER-w (in the past, this option was used to compute HTER_w)
  # -------------------------------------------------
  
  if 1 in args.demandedplot:
    points = 10
    criteria = args.criteria
    fig = mpl.figure()
   
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.beta)

    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_w
    
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    hter_w_epsc = errors[4].flatten()
    frr_nonepsc = errors[0][0,0]; far_nonepsc = errors[1][0,0]; sfar_nonepsc = errors[2][0,0];
    far_w_nonepsc = [error_utils.weighted_err(far_nonepsc, sfar_nonepsc, w) for w in omega]
    hter_w_nonepsc = np.array([error_utils.weighted_err(frr_nonepsc, i, args.beta) for i in far_w_nonepsc])
    
    mpl.plot(omega, 100. * hter_w_epsc, color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = "EPSC threshold criteria",linewidth=4)
    mpl.plot(omega, 100. * hter_w_nonepsc, color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label = "Methodology 2 threshold criteria",linewidth=4)
    
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel(r"HTER$_{\omega}$ (\%)")

    #mpl.title("EPSC with %s, beta = %.2f" % (criteria, args.beta) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16), loc=2)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
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
    omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.beta)
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: frr, far, sfar, far_w, wer_w
    mpl.rcParams.update({'font.size': 18})
     
    ax1 = mpl.subplot(111) # EPC like curves for FVAS fused scores for weighted error rates between the negatives (impostors and spoofing attacks)
    
    sfar_epsc = errors[2].flatten()
    sfar_nonepsc = np.array([errors[2][0,0]] * (points + 1))
    
    mpl.plot(omega, 100. * sfar_epsc, color=linecolor_scheme['line1'], linestyle=linestyle_scheme['line1'], label = 'EPSC threshold criteria', linewidth=4)
    mpl.plot(omega, 100. * sfar_nonepsc, color=linecolor_scheme['line2'], linestyle=linestyle_scheme['line2'], label = "Methodology 2 threshold criteria",linewidth=4)
    
    mpl.xlabel("Weight $\omega$")
    mpl.ylabel("SFAR (\%)")

    #mpl.title("EPSC with %s, beta = %.2f" % (criteria, args.beta) if args.title == "" else args.title)

    mpl.legend(prop=fm.FontProperties(size=16), loc=3)
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    mpl.grid()  

    pp.savefig()    
  
  
  
    
  pp.close() # close multi-page PDF writer
 

if __name__ == '__main__':
  main()
