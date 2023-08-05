#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Jul 25 20:18:36 CEST 2013

"""Plot DET or EPSC plots to compare 4 face verification systems (GMM, LGBPHS, GJet and ISV) on one figure
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob
import numpy
import argparse
from matplotlib import rc
rc('text',usetex=1)
from matplotlib.ticker import FormatStrFormatter

import matplotlib.font_manager as fm

from ..utils import error_utils

def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  
  parser.add_argument('--as', '--antispoof', metavar='STR', type=str, dest='antispoofingalg', default="", help='The antispoofing system', choices=('ALL','LBP', 'LBP-TOP','MOTION'))
  parser.add_argument('--fu', '--fusion', metavar='STR', type=str, dest='fusionalg', default="", help='The fusion method', choices=('SUM','LLR','PLR'))
  parser.add_argument('--bf', '--basedir_faceverif', metavar='STR', type=str, dest='basedir_faceverif', default="", help='The base directory for the baseline face verification algorithms score files (if needed)')
  parser.add_argument('--ba', '--basedir_fvas', metavar='STR', type=str, dest='basedir_fvas', default="", help='The base directory of the fused scores (if needed)')
  parser.add_argument('--baseline', action='store_true', default=False, dest='baseline', help='If True, will plot only the baseline systems for comparison. Otherwise it will plot fused systems based on the specified fusion method')
  
  parser.add_argument('-c', '--criteria', metavar='STR', type=str,
      dest='criteria', default="eer", help='Criteria for threshold selection', choices=('eer', 'hter', 'wer'))   
  parser.add_argument('--vp', '--var_param', metavar='STR', type=str,
      dest='var_param', default='omega', help='Name of the varying parameter', choices=('omega','beta'))    
  parser.add_argument('--fp', '--fixed_param', metavar='STR', type=float,
      dest='fixed_param', default=(0.5,) , help='Value of the fixed parameter', nargs='+')     
         
  parser.add_argument('-t', '--title', metavar='STR', type=str, dest='title', default="", help='Plot title')
  parser.add_argument('--nocolor', action='store_true',help='If True, will generate all the plots in grayscale.')
  parser.add_argument('-o', '--output', metavar='FILE', type=str, default='plots.pdf', dest='output', help='Set the name of the output file (defaults to "%(default)s")')
  parser.add_argument('-i', '--demandedplot', metavar='STR', type=int, dest='demandedplot', default=1, help='The numbers of plot that needs to be plotted. Select: 1 - for EPSC for HTER_w; 2 - for EPSC for SFAR.')
  
  
  args = parser.parse_args()

  antispoofing_dict = {'LBP':'LBP', 'LBP-TOP':'LBP-TOP-1', 'MOTION':'MOTION', 'ALL':'ALL'}
  fusion_dict = {'SUM':'SUM', 'LLR':'LLR', 'PLR':'LLR_P'}
  
  if not args.baseline:
    antispoofingalg = antispoofing_dict[args.antispoofingalg]
    fusionalg = fusion_dict[args.fusionalg]

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  if args.nocolor: # plot in gray-scale
    color_mapping = {'ubmgmm':'#000000', 'lgbphs':'#000000', 'ebgm':'#4c4c4c', 'isv':'#999999'}
    marker_mapping = {'ubmgmm':None, 'lgbphs':None, 'ebgm':None, 'isv':None}   
    linestyle_mapping = {'ubmgmm':'--', 'lgbphs':':', 'ebgm':'-.', 'isv':'-'}
    width=4
  else: # plot in color
    color_mapping = {'ubmgmm':'blue', 'lgbphs':'green', 'ebgm':'#ff9933', 'isv':'red'}
    marker_mapping = {'ubmgmm':None, 'lgbphs':None, 'ebgm':None, 'isv':None}   
    linestyle_mapping = {'ubmgmm':'-', 'lgbphs':'-', 'ebgm':'-', 'isv':'-'}
    width=4

  legend_dict = {'ubmgmm':'GMM', 'lgbphs':'LGBPHS', 'ebgm':'GJet', 'isv':'ISV'} 
  
  #Plot 1: EPSC - HTER_w (comparison of baseline systems)
  # -----------
  if args.demandedplot == 1:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18}) 

    for faceverif in ('ubmgmm','lgbphs', 'ebgm', 'isv'):
      if args.baseline:
        base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
      else:
        base_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-eval')
    
      [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
      [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
      [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
      [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

      if args.var_param == 'omega':
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
      else:
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
      errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: far_w, hter_w
       
      if args.var_param == 'omega': 
        mpl.plot(omega, 100 * errors[1].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
        mpl.xlabel(r"Weight $\omega$")
      else:
        mpl.plot(beta, 100 * errors[1].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
        mpl.xlabel(r"Weight $\beta$")  
        
      ax1 = mpl.subplot(111);
     
    mpl.ylabel(r"HTER$_{\omega}$ (\%)") 
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%.1f')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.title("EPSC: comparison of face verification systems" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()  
  
  #Plot 2: EPSC - SFAR (comparison of baseline systems)
  # -----------
  if args.demandedplot == 2:
    points = 100
    criteria = args.criteria
    fig = mpl.figure()
    mpl.rcParams.update({'font.size': 18}) 

    for faceverif in ('ubmgmm', 'lgbphs', 'ebgm', 'isv'):
      if args.baseline:
        base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
      else:
        base_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-dev')
        over_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-dev')
        base_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-eval')
        over_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-eval')
    
      [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
      [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
      [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
      [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

      if args.var_param == 'omega':
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
      else:
        omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
      
      errors = error_utils.all_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: frr, far, sfar, far_w, hter_w
       
      if args.var_param == 'omega': 
        mpl.plot(omega, 100 * errors[2].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
        mpl.xlabel(r"Weight $\omega$")
      else:
        mpl.plot(beta, 100 * errors[2].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
        mpl.xlabel(r"Weight $\beta$")  
        
      ax1 = mpl.subplot(111);
     
    mpl.ylabel("SFAR (\%)")
    mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=12))
    
    fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
    ax1.set_xticklabels(ax1.get_xticks(), fontProperties)
    ax1.set_yticklabels(ax1.get_yticks(), fontProperties)
    majorFormatter = FormatStrFormatter('%d')
    ax1.yaxis.set_major_formatter(majorFormatter)
    mpl.title("EPSC: comparison of face verification systems" if args.title == "" else args.title)
    mpl.grid()
    pp.savefig()  
  
    
  # Plot 10: Dummy legend for EPSC plot (doesn't print usefull plot, only there to generate a legend)
  # -------------------------------------------------------------------------------------------------
  if args.demandedplot == 10:
    points = 100
    criteria = args.criteria
    for ff in ('SUM',):
      fig = mpl.figure()
      mpl.rcParams.update({'font.size': 18})
      ax1 = mpl.subplot(111) 
      # Now we are iterating over all the face verification algorithms that need to be plotted on the plot
      for faceverif in ('ubmgmm', 'lgbphs', 'ebgm', 'isv'):

        if args.baseline:
          base_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-dev')
          over_dev_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-dev')
          base_test_file = os.path.join(args.basedir_faceverif, faceverif, 'licit/scores-eval')
          over_test_file = os.path.join(args.basedir_faceverif, faceverif, 'spoof/scores-eval')
    
        else:
          base_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-dev')
          over_dev_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-dev')
          base_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'licit/scores-eval')
          over_test_file = os.path.join(args.basedir_fvas, fusionalg, faceverif, antispoofingalg, 'spoof/scores-eval')
    
        [base_neg, base_pos] = bob.measure.load.split_four_column(base_test_file)
        [over_neg, over_pos] = bob.measure.load.split_four_column(over_test_file)
        [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(base_dev_file)
        [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(over_dev_file)

        if args.var_param == 'omega':
          omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, beta=args.fixed_param) 
        else:
          omega, beta, thrs = error_utils.epsc_thresholds(base_neg_dev, base_pos_dev, over_neg_dev, over_pos_dev, points=points, criteria=criteria, omega=args.fixed_param) 
          
        errors = error_utils.epsc_error_rates(base_neg, base_pos, over_neg, over_pos, thrs, omega, beta) # error rates are returned in a list in the following order: far_w, hter_w
        if args.var_param == 'omega': 
          mpl.plot(omega, 100 * errors[1].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
          mpl.xlabel(r"Weight $\omega$")
        else:
          mpl.plot(beta, 100 * errors[1].flatten(), color=color_mapping[faceverif], marker=marker_mapping[faceverif], linestyle=linestyle_mapping[faceverif], markevery=10, label = legend_dict[faceverif], linewidth=width)
          mpl.xlabel(r"Weight $\beta$")  
        
      mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., prop=fm.FontProperties(size=18))
      mpl.grid()
      pp.savefig()
  
  
  
  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
  


