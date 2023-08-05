#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Dec  7 12:33:37 CET 2012

"""Utility functions for computation of EPSC curve and related measurement"""

import os
import sys
import bob.measure
import numpy
import argparse

def calc_pass_rate(threshold, attacks):
  """Calculates the rate of successful spoofing attacks
  
  Keyword parameters: 
  
    - threshold - the threshold used for classification
    - attack: numpy with the scores of the spoofing attacks
  """
  return sum(1 for i in attacks if i >= threshold)/float(attacks.size)
  
def epc(dev_negatives, dev_positives, test_negatives, test_positives, points):
  """Reproduces the bob.measure.epc() functionality, but also returns the
  thresholds on the 3rd column of the input data.
  
  Keyword parameters:
  
    - dev_negatives - numpy.array with scores of the negative samples of the dev set
    - dev_positives - numpy.array with scores of the positive samples of the dev set
    - test_negatives - numpy.array with scores of the negative samples of the test set
    - test_positives - numpy.array with scores of the positive samples of the test set
    - points - the number of points to be considered for the weight parameter
  """
  
  retval = numpy.ndarray((points, 3), 'float64')
  step = 1./(float(points)-1.) # step for the weight parameter

  for i in range(points):
    retval[i,0] = i*step # weight parameter
    retval[i,2] = bob.measure.min_weighted_error_rate_threshold(dev_negatives,
        dev_positives, retval[i,0]) # threshold (dev set)
    retval[i,1] = sum(bob.measure.farfrr(test_negatives, test_positives, retval[i,2]))/2. # HTER error rate (test set)

  return retval  


def weighted_neg_error_rate_criteria(data, weight, thres, beta=0.5, criteria='eer'): 
  """Given the single value for the weight parameter balancing between impostors and spoofing attacks and a threshold, calculates the error rates and their relationship depending on the criteria (difference in case of 'eer', hter in case of 'hter' criteria) 

    Keyword parameters:
      
      - data - the development data used to determine the threshold. List on 4 numpy.arrays containing: negatives (licit), positives (licit), negatives (spoof), positivies (spoof)
      - weight - the weight parameter balancing between impostors and spoofing attacks
      - thres - the given threshold
      - beta - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks). Note that this parameter will be overriden and not considered if the selected criteria is 'hter'.
      - criteria - 'eer', 'wer' or 'hter' criteria for decision threshold 
  """

  licit_neg = data[0]; licit_pos = data[1]; spoof_neg=data[2]; spoof_pos=data[3] # unpacking the data
  farfrr_licit = bob.measure.farfrr(licit_neg, licit_pos, thres)
  farfrr_spoof = bob.measure.farfrr(spoof_neg, spoof_pos, thres)
  
  frr = farfrr_licit[1] # farfrr_spoof[1] should have the same value
  far_i = farfrr_licit[0]
  far_s = farfrr_spoof[0]
  
  far_w = (1-weight) * far_i + weight * far_s 

  if criteria == 'eer':
    if beta == 0.5:
      return abs(far_w - frr)
    else:
      #return abs(far_w - frr)
      return abs((1-beta) * frr - beta * far_w)
       
  elif criteria == 'hter':
    return (far_w + frr) / 2
    
  else:  
    return (1-beta) * frr + beta * far_w


def recursive_thr_search(data, span_min, span_max, weight, beta=0.5, criteria='eer'): 
  """Recursive search for the optimal threshold given a criteria. It evaluates the full range of thresholds at 100 points, and computes the one which optimizes the threshold. In the next search iteration, it examines the region around the point that optimizes the threshold. The procedure stops when the search range is smaller then 1e-10.
  
  Keyword arguments:
    - data - the development data used to determine the threshold. List on 4 numpy.arrays containing: negatives (licit), positives (licit), negatives (spoof), positivies (spoof)
    - span_min - the minimum of the search range
    - span_max - the maximum of the search range
    - weight - the weight parameter balancing between impostors and spoofing attacks
    - beta - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks). Note that methods called within this function will override this parameter and not considered if the selected criteria is 'hter'.
    - criteria - the decision threshold criteria ('eer' for EER, 'wer' for Minimum WER or 'hter' for Minimum HTER criteria).
  """

  quit_thr = 1e-10
  steps = 100
  if abs((span_max - span_min)/span_max) < quit_thr:
    return span_max # or span_min, it doesn't matter
  else:
    step_size = (span_max - span_min) / steps
    thresholds = numpy.array([(i * step_size) + span_min for i in range(steps+1)])
    weighted_error_rates = numpy.array([weighted_neg_error_rate_criteria(data, weight, thr, beta, criteria) for thr in thresholds])
    selected_thres = thresholds[numpy.where(weighted_error_rates==min(weighted_error_rates))] # all the thresholds which have minimum weighted error rate
    thr = selected_thres[selected_thres.size/2] # choose the centrally positioned threshold
    return recursive_thr_search(data, thr-step_size, thr+step_size, weight, beta, criteria)


def weighted_negatives_threshold(licit_neg, licit_pos, spoof_neg, spoof_pos, weight, beta=0.5, criteria='eer'):
  """Calculates the threshold for achieving the given criteria between the FAR_w and the FRR, given the single value for the weight parameter balancing between impostors and spoofing attacks and a single value for the parameter beta balancing between the real accesses and the negatives (impostors and spoofing attacks)
  
  Keyword parameters:
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - weight - the weight parameter balancing between impostors and spoofing attacks
    - beta - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks). Note that methods called within this function will override this parameter and not considered if the selected criteria is 'hter'.
    - criteria - the decision threshold criteria ('eer' for EER, 'wer' for Minimum WER or 'hter' for Minimum HTER criteria). 
  """
  span_min = min(numpy.append(licit_neg, spoof_neg)) # the min of the span where we will search for the threshold
  span_max = max(numpy.append(licit_pos, spoof_pos)) # the max of the span where we will search for the threshold
  data = (licit_neg, licit_pos, spoof_neg, spoof_pos) # pack the data into a single list
  return recursive_thr_search(data, span_min, span_max, weight, beta, criteria)


def epsc_weights(licit_neg, licit_pos, spoof_neg, spoof_pos, points=100):
  """Returns the weights for EPSC
  
  Keyword arguments:

    - points - number of points to calculate EPSC
  """
  step_size = 1 / float(points)
  weights = numpy.array([(i * step_size) for i in range(points+1)])
  return weights

  
  
def epsc_thresholds(licit_neg, licit_pos, spoof_neg, spoof_pos, points=100, criteria='eer', omega=None, beta=None):
  """Calculates the optimal thresholds for EPSC, for a range of the weight parameter balancing between impostors and spoofing attacks, and for a range of the beta parameter balancing between real accesses and all the negatives (impostors and spoofing attacks)
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - points - number of points to calculate EPSC
    - criteria - the decision threshold criteria ('eer', 'wer' or 'hter')
    - omega - the value of the parameter omega, balancing between impostors and spoofing attacks. If None, it is going to span the full range [0,1]. Otherwise, can be set to a fixed value or a list of values. 
    - beta - the value of the parameter beta, balancing between real accesses and all the negatives (zero-effort impostors and spoofing attacks). If None, it is going to span the full range [0,1]. Otherwise, can be set to a fixed value or a list of values. 

  """
  step_size = 1 / float(points)
  
  if omega == None:
    omega = numpy.array([(i * step_size) for i in range(points+1)])
  elif not isinstance(omega, list) and not isinstance(omega, tuple) and not isinstance(omega, numpy.ndarray):
    omega = numpy.array([omega])
  else:
    omega = numpy.array(omega)  
      
  if beta == None:
    beta = numpy.array([(i * step_size) for i in range(points+1)])
  elif not isinstance(beta, list) and not isinstance(beta, tuple) and not isinstance(beta, numpy.ndarray):
    beta = numpy.array([beta])    
  else:
    beta = numpy.array(beta)  
      
  thresholds = numpy.ndarray([beta.size, omega.size], 'float64') 
  for bindex, b in enumerate(beta):
    thresholds[bindex,:] = numpy.array([weighted_negatives_threshold(licit_neg, licit_pos, spoof_neg, spoof_pos, w, b, criteria = criteria) for w in omega], 'float64')
    
  return omega, beta, thresholds  

  

def weighted_err(error_1, error_2, weight):
  """Calculates the weighted error rate between the two input parameters
  
  Keyword arguments:
    - error_1 - the first input error rate (FAR for zero effort impostors usually)
    - error_2 - the second input error rate (SFAR)
    - weight - the given weight
  """
  return (1-weight) * error_1 + weight * error_2


def error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, omega, threshold, beta=0.5): 
  """Calculates several error rates: FRR, FAR (zero-effort impostors), SFAR, FAR_w, HTER_w for a given value of w. It returns the calculated threshold as a last argument
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - threshold - the given threshold
    - omega - the omega parameter balancing between impostors and spoofing attacks
    - beta - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks).
  """
    
  farfrr_licit = bob.measure.farfrr(licit_neg, licit_pos, threshold) # calculate test frr @ threshold (licit scenario)
  farfrr_spoof = bob.measure.farfrr(spoof_neg, spoof_pos, threshold) # calculate test frr @ threshold (spoof scenario)

  frr = farfrr_licit[1] # we can take this value from farfrr_spoof as well, it doesn't matter
  far = farfrr_licit[0]
  sfar = farfrr_spoof[0]

  far_w = weighted_err(far, sfar, omega)
  hter_w = (far_w + frr) / 2
  wer_wb = weighted_err(frr, far_w, beta)

  return (frr, far, sfar, far_w, wer_wb, hter_w, threshold)
  
 

  
  
def epsc_error_rates(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds, omega, beta):
  """Calculates several error rates: FAR_w and WER_wb for the given weights (omega and beta) and thresholds (the thresholds need to be computed first using the method: epsc_thresholds() before passing to this method)
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - thresholds - numpy.ndarray with threshold values
    - omega - numpy.array of the omega parameter balancing between impostors and spoofing attacks
    - beta - numpy.array of the beta parameter balancing between real accesses and all negatives (impostors and spoofing attacks)
  """
  
  if not isinstance(omega, list) and not isinstance(omega, tuple) and not isinstance(omega, numpy.ndarray):
    omega = numpy.array([omega]) 
  else:
    omega = numpy.array(omega)  
  
  if not isinstance(beta, list) and not isinstance(beta, tuple) and not isinstance(beta, numpy.ndarray):
    beta = numpy.array([beta]) 
  else:
    beta = numpy.array(beta)  
  
  far_w_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  wer_wb_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  
  for bindex, b in enumerate(beta):
    errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, w, thresholds[bindex, windex], b) for windex, w in enumerate(omega)]
    far_w_errors[bindex,:] = [errors[i][3] for i in range(len(errors))]
    wer_wb_errors[bindex,:] = [errors[i][4] for i in range(len(errors))]

  return far_w_errors, wer_wb_errors
   
   



  
  
def all_error_rates(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds, omega, beta):
  """Calculates several error rates: FAR_w and HTER_w for the given weights (omega and beta) and thresholds (the thresholds need to be computed first using the method: epsc_thresholds() before passing to this method)
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - thresholds - numpy.array with threshold values
    - omega - numpy.array of the omega parameter balancing between impostors and spoofing attacks
    - beta - numpy.array of the beta parameter balancing between real accesses and all negatives (impostors and spoofing attacks)
  """
  
  if not isinstance(omega, list) and not isinstance(omega, tuple) and not isinstance(omega, numpy.ndarray):
    omega = numpy.array([omega]) 
  else:
    omega = numpy.array(omega)  
  
  if not isinstance(beta, list) and not isinstance(beta, tuple) and not isinstance(beta, numpy.ndarray):
    beta = numpy.array([beta]) 
  else:
    beta = numpy.array(beta)   
  
  frr_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  far_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  sfar_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  far_w_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  wer_wb_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  hter_wb_errors = numpy.ndarray((beta.size, omega.size), 'float64')
  
  for bindex, b in enumerate(beta):
    errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, w, thresholds[bindex, windex], b) for windex, w in enumerate(omega)]
    frr_errors[bindex,:] = [errors[i][0] for i in range(len(errors))]
    far_errors[bindex,:] = [errors[i][1] for i in range(len(errors))]
    sfar_errors[bindex,:] = [errors[i][2] for i in range(len(errors))]
    far_w_errors[bindex,:] = [errors[i][3] for i in range(len(errors))]
    wer_wb_errors[bindex,:] = [errors[i][4] for i in range(len(errors))]
    hter_wb_errors[bindex,:] = [errors[i][5] for i in range(len(errors))]

  return frr_errors, far_errors, sfar_errors, far_w_errors, wer_wb_errors, hter_wb_errors



def calc_aue(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds, omega, beta, l_bound=0, h_bound=1, var_param='omega'):
  """Calculates AUE of EPSC for the given thresholds and weights
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - l_bound - lower bound of integration
    - h_bound - higher bound of integration
    - points - number of points to calculate EPSC
    - criteria - the decision threshold criteria ('eer', 'wer' or 'hter')
    - var_param - name of the parameter which is varied on the abscissa ('omega' or 'beta')
  """

  from scipy import integrate
  
  if var_param == 'omega':
    errors = all_error_rates(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds, omega, beta)  
    weights = omega # setting the weights to the varying parameter
  else:
    errors = all_error_rates(licit_neg, licit_pos, spoof_neg, spoof_pos, thresholds, omega, beta)  
    weights = beta # setting the weights to the varying parameter
  
  wer_errors = errors[4].reshape(1, errors[4].size)
    
  l_ind = numpy.where(weights >= l_bound)[0][0]
  h_ind = numpy.where(weights <= h_bound)[0][-1]
  aue = integrate.cumtrapz(wer_errors, weights)
  aue = numpy.append([0], aue) # for indexing purposes, aue is cumulative integration
  aue = aue[h_ind] - aue[l_ind]
      
  return aue
  
  


