#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Jul 26 18:29:31 CEST 2013

"""Plot EPSC plots to compare 4 fusion methods (AND, SUM, LR and PLR) for a fusing given face verification and anti-spoofing systems
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob.measure
import numpy
import argparse
from matplotlib import rc
rc('text',usetex=1)
from matplotlib.ticker import FormatStrFormatter

import matplotlib.font_manager as fm

from ..utils import error_utils



def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('--as', '--antispoof', metavar='STR', type=str, dest='antispoofingalg', default="", help='The antispoofing system', choices=('LBP', 'LBP-TOP','MOTION'))
  parser.add_argument('--fv', '--faceverif', metavar='STR', type=str, dest='faceverifalg', default="", help='The face-verification system', choices=('GMM','LGBPHS','GJet','ISV'))
  parser.add_argument('--bf', '--basedir_faceverif', metavar='STR', type=str, dest='basedir_faceverif', default="", help='The base directory for the baseline face verification algorithms score files')
  parser.add_argument('--ba', '--basedir_fvas', metavar='STR', type=str, dest='basedir_fvas', default="", help='The base directory of the fused scores')

  parser.add_argument('-c', '--criteria', metavar='STR', type=str,
      dest='criteria', default="eer", help='Criteria for threshold selection', choices=('eer', 'hter', 'wer'))   
  parser.add_argument('--vp', '--var_param', metavar='STR', type=str,
      dest='var_param', default='omega', help='Name of the varying parameter', choices=('omega','beta'))    
  parser.add_argument('--fp', '--fixed_param', metavar='STR', type=float,
      dest='fixed_param', default=(0.5,) , help='Value of the fixed parameter', nargs='+')     
      
  parser.add_argument('-t', '--title', metavar='STR', type=str, dest='title', default="", help='Plot title')
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('-o', '--output', metavar='FILE', type=str, default='plots.pdf', dest='output', help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('--iand', '--input_and', metavar='FILE', type=str, default='toplot_and.hdf5', dest='input_and', help=argparse.SUPPRESS) #The name of na input hdf5file containing the values that need to be plotted and which are precomputed for AND decision level fusion
  
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - for EPSC for HTER_w; 2 - for EPSC for SFAR.')

  args = parser.parse_args()
  
  faceverif_dict = {'GMM':'ubmgmm', 'LGBPHS':'lgbphs', 'GJet':'ebgm', 'ISV':'isv'}
  antispoofing_dict = {'LBP':'LBP', 'LBP-TOP':'LBP-TOP-1', 'MOTION':'MOTION', 'ALL':'ALL'}
  
  faceverifalg = faceverif_dict[args.faceverifalg]
  antispoofingalg = antispoofing_dict[args.antispoofingalg]

  # Reading the score files for the baseline systems
  base_dev_file = os.path.join(args.basedir_faceverif, faceverifalg, 'licit/scores-dev')
  over_dev_file = os.path.join(args.basedir_faceverif, faceverifalg, 'spoof/scores-dev')
  base_test_file = os.path.join(args.basedir_faceverif, faceverifalg, 'licit/scores-eval')
  over_test_file = os.path.join(args.basedir_faceverif, faceverifalg, 'spoof/scores-eval')

  [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
  [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in gray-scale
    color_mapping = {'baseline':'#000000', 'AND':'#4c4c4c', 'SUM':'#4c4c4c', 'LLR':'#999999', 'LLR_P':'#000000'}
    linestyle_mapping = {'baseline':'-', 'AND':'-', 'SUM':'--', 'LLR':'-.', 'LLR_P':':'}
    width=4
    
  else: # plot in color
    color_mapping = {'baseline':'blue', 'SUM':'red', 'LLR':'green', 'LLR_P':'#ff9933', 'AND':'#570c83'}
    linestyle_mapping = {'baseline':'-', 'AND':'-', 'SUM':'-', 'LLR':'-', 'LLR_P':'-'}
    width=4

  fusion_label_dict = {'AND':'AND fusion', 'SUM':'SUM fusion', 'LLR':'LR fusion', 'LLR_P':'PLR fusion'}
      
  # Plot 1: EPSC - HTER(comparison between baseline and fused counter measures)
  # -----------
  if args.demandedplot == 1:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    ax1 = mpl.subplot(111) 
      
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
    errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: far_w, hter_w
    
    # plotting the baseline scores
    if args.var_param == 'omega':
      mpl.plot(omega, 100. * errors[1].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=width, label = 'baseline')
    else:  
      mpl.plot(beta, 100. * errors[1].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=width, label = 'baseline')
      
    # Now we are iterating over all the fusion methods that need to be plotted on the plot
    for fusionalg in ('SUM', 'LLR', 'LLR_P'):

      base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-dev')
      over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-dev')
      base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-eval')
      over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-eval')
      
      [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
      [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
      [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
      [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

      if args.var_param == 'omega':
        omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, beta=args.fixed_param)
      else:
        omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, omega=args.fixed_param)
        
      errors_cm = error_utils.epsc_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, thrs_cm, omega, beta) # error rates are returned in a list in the following order: far_w, hter_w

      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors_cm[1].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
        mpl.xlabel(r"Weight $\omega$");
      else:
        mpl.plot(beta, 100. * errors_cm[1].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
        mpl.xlabel(r"Weight $\beta$");
      
    # plotting pre-computed scores for AND decision fusion  
    #f = bob.io.HDF5File(args.input_and)  
    #error_hter_and = f.read('hter_w')
    #mpl.plot(omega, 100. * error_hter_and, color=color_mapping['AND'], linestyle=linestyle_mapping['AND'], linewidth=width, label = fusion_label_dict['AND'])
      
    mpl.ylabel(r"HTER$_{\omega}$ (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode=r"expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.grid()
    pp.savefig()
      
  # Plot 2: EPSC - SFAR (comparison between baseline and fused counter measures)
  # -----------
  if args.demandedplot == 2:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18})
    ax1 = mpl.subplot(111) 
      
    if args.var_param == 'omega':
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
    else:
      omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
    errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, hter_w
    # plotting the baseline scores
    if args.var_param == 'omega':
      mpl.plot(omega, 100. * errors[2].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=4, label = 'baseline')
    else:  
      mpl.plot(beta, 100. * errors[2].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=4, label = 'baseline')
      
    # Now we are iterating over all the fusion methods that need to be plotted on the plot
    for fusionalg in ('SUM', 'LLR', 'LLR_P'):

      base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-dev')
      over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-dev')
      base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-eval')
      over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-eval')
  
      [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
      [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
      [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
      [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

      if args.var_param == 'omega':
        omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, beta=args.fixed_param)
      else:  
        omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, omega=args.fixed_param)
        
      errors_cm = error_utils.all_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, thrs_cm, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, hter_w

      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors_cm[2].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
        mpl.xlabel(r"Weight $\omega$");
      else:  
        mpl.plot(beta, 100. * errors_cm[2].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
        mpl.xlabel(r"Weight $\beta$");
      
    # plotting pre-computed scores for AND decision fusion  
    #f = bob.io.HDF5File(args.input_and)  
    #error_sfar_and = f.read('sfar')
    #mpl.plot(omega, 100. * error_sfar_and, color=color_mapping['AND'], linestyle=linestyle_mapping['AND'], linewidth=width, label = fusion_label_dict['AND'])  
      
    mpl.ylabel(r"SFAR (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode=r"expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.grid()
    pp.savefig()
    
    
  # Plot 10: Dummy legend for EPSC plot (doesn't print usefull plot, only there to generate a legend)
  # -------------------------------------------------------------------------------------------------
  if args.demandedplot == 10:
    for antispoofingalg in ('LBP',):
      points = 100
      criteria = args.criteria
      fig = mpl.figure()
      mpl.rcParams.update({'font.size': 18})
      ax1 = mpl.subplot(111) 
      if args.var_param == 'omega':
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
      else:
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
      errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a numpy.ndarrat in the following order: far_w, hter_w
    
      # plotting the baseline scores
      if args.var_param == 'omega':
        mpl.plot(omega, 100. * errors[1].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=width, label = 'baseline')
      else:  
        mpl.plot(beta, 100. * errors[1].flatten(), color=color_mapping['baseline'], linestyle=linestyle_mapping['baseline'], linewidth=width, label = 'baseline')

      # Now we are iterating over all the fusion methods that need to be plotted on the plot
      for fusionalg in ('AND', 'SUM','LLR', 'LLR_P'):

        base_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-dev')
        over_dev_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-dev')
        base_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'licit/scores-eval')
        over_test_cm_file = os.path.join(args.basedir_fvas, fusionalg, faceverifalg, antispoofingalg, 'spoof/scores-eval')
  
        [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(base_test_cm_file)
        [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(over_test_cm_file)
        [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(base_dev_cm_file)
        [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(over_dev_cm_file)

        if args.var_param == 'omega':
          omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, beta=args.fixed_param)
        else:
          omega, beta, thrs_cm = error_utils.epsc_thresholds(base_neg_dev_cm, base_pos_dev_cm, over_neg_dev_cm, over_pos_dev_cm, points=points, criteria=criteria, omega=args.fixed_param)
        
        errors_cm = error_utils.epsc_error_rates(base_neg_cm, base_pos_cm, over_neg_cm, over_pos_cm, thrs_cm, omega, beta) # error rates are returned in a list in the following order: far_w, hter_w

        if args.var_param == 'omega':
          mpl.plot(omega, 100. * errors_cm[1].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
          mpl.xlabel(r"Weight $\omega$");
        else:
          mpl.plot(beta, 100. * errors_cm[1].flatten(), color=color_mapping[fusionalg], linestyle=linestyle_mapping[fusionalg], linewidth=width, label = fusion_label_dict[fusionalg])
          mpl.xlabel(r"Weight $\beta$");
      
      mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=14))
      mpl.grid()
      pp.savefig()    
  
  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
  


