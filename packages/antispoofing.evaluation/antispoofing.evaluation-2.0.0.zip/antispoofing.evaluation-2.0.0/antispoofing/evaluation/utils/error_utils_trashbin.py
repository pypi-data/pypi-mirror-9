
def epsc_thresholds_beta(licit_neg, licit_pos, spoof_neg, spoof_pos, points=100, beta=0.5, criteria='eer'):
  """Calculates the optimal thresholds for EPSC, for the full range of the weight parameter balancing between impostors and spoofing attacks and fixed beta
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - points - number of points to calculate EPSC
    - beta - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks). Note that methods called within this function will override this parameter and not consider it if the selected criteria is 'hter'.
    - criteria - the decision threshold criteria ('eer', 'wer' or 'hter')
  """
  
  step_size = 1 / float(points)
  weights = numpy.array([(i * step_size) for i in range(points+1)])
  thresholds = numpy.array([weighted_negatives_threshold(licit_neg, licit_pos, spoof_neg, spoof_pos, w, beta, criteria = criteria) for w in weights])
  return weights, thresholds


def epsc_thresholds_omega(licit_neg, licit_pos, spoof_neg, spoof_pos, points=100, omega=0.5, criteria='eer'): ### NEW!!!
  """Calculates the optimal thresholds for EPSC, for the full range of the weight parameter beta balancing between real accesses and the negative class (impostors and spoofing attacks) and fixed omega
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - points - number of points to calculate EPSC
    - omega - the weight parameter balancing between real accesses and all the negative samples (impostors and spoofing attacks). Note that methods called within this function will override this parameter and not consider it if the selected criteria is 'hter'.
    - criteria - the decision threshold criteria ('eer', 'wer')
  """
  
  if criteria == 'hter':
    raise Exception("HTER criteria is not possible if beta varies.")
    
  step_size = 1 / float(points)
  weights_beta = numpy.array([(i * step_size) for i in range(points+1)])
  thresholds = numpy.array([weighted_negatives_threshold(licit_neg, licit_pos, spoof_neg, spoof_pos, omega, beta=b, criteria = criteria) for b in weights_beta])
  return weights_beta, thresholds


def all_error_rates_beta(licit_neg, licit_pos, spoof_neg, spoof_pos, weights, thresholds, beta=0.5): ### MODIFIED!!!
  """Calculates several error rates: FAR_w and HTER_w for the given weights (calculates the optimal thresholds first)
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - weights - numpy.array of the weight parameter balancing between impostors and spoofing attacks
    - thresholds - numpy.array with threshold values
    - beta - beta parameter balancing between real accesses and all negatives (impostors and spoofing attacks)
  """
  retval = numpy.ndarray((numpy.array(weights).size, 6), 'float64')
  
  errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, weights[i], thresholds[i], beta) for i in range(len(weights))]
  
  frr = [errors[i][0] for i in range(len(errors))]
  far = [errors[i][1] for i in range(len(errors))]
  sfar = [errors[i][2] for i in range(len(errors))]
  far_w = [errors[i][3] for i in range(len(errors))]
  wer_wb = [errors[i][4] for i in range(len(errors))]
  hter_w = [errors[i][5] for i in range(len(errors))]

  retval[:,0] = numpy.array(frr[:])
  retval[:,1] = numpy.array(far[:])
  retval[:,2] = numpy.array(sfar[:])
  retval[:,3] = numpy.array(far_w[:])
  retval[:,4] = numpy.array(wer_wb[:])
  retval[:,5] = numpy.array(hter_w[:])

  return retval 
  
def all_error_rates_omega(licit_neg, licit_pos, spoof_neg, spoof_pos, weights_beta, thresholds, omega=0.5): ### NEW!!!
  """Calculates several error rates: FAR_w and HTER_w for the given weights (calculates the optimal thresholds first)
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - weights_beta - numpy.array of the weight parameter balancing between the real accesses and all the engatives (zero-effort impostors and spoofing attacks)
    - thresholds - numpy.array with threshold values
    - omega - parameter balancing between impostors and spoofing attacks
  """
  retval = numpy.ndarray((numpy.array(weights).size, 6), 'float64')
  
  errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, omega, thresholds[i], weights_beta[i]) for i in range(len(weights_beta))]
  
  frr = [errors[i][0] for i in range(len(errors))]
  far = [errors[i][1] for i in range(len(errors))]
  sfar = [errors[i][2] for i in range(len(errors))]
  far_w = [errors[i][3] for i in range(len(errors))]
  wer_wb = [errors[i][4] for i in range(len(errors))]
  hter_w = [errors[i][5] for i in range(len(errors))]

  retval[:,0] = numpy.array(frr[:])
  retval[:,1] = numpy.array(far[:])
  retval[:,2] = numpy.array(sfar[:])
  retval[:,3] = numpy.array(far_w[:])
  retval[:,4] = numpy.array(wer_wb[:])
  retval[:,5] = numpy.array(hter_w[:])

  return retval 
  
  
def epsc_error_rates_beta(licit_neg, licit_pos, spoof_neg, spoof_pos, weights, thresholds, beta=0.5): ### MODIFIED!!!
  """Calculates several error rates: FAR_w and HTER_w for the given weights and thresholds (the thresholds need to be computed first using the method: epsc_thresholds().) The parameter beta is fixed.
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - weights - numpy.array of the weight parameter balancing between impostors and spoofing attacks
    - thresholds - numpy.array with threshold values
    - beta - beta parameter balancing between real accesses and all negatives (impostors and spoofing attacks)
  """
  retval = numpy.ndarray((numpy.array(weights).size, 3), 'float64')
  
  errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, weights[i], thresholds[i], beta) for i in range(len(weights))]
  
  far_w = [errors[i][3] for i in range(len(errors))]
  wer_wb = [errors[i][4] for i in range(len(errors))]
  hter_w = [errors[i][5] for i in range(len(errors))]

  retval[:,0] = numpy.array(far_w[:])
  retval[:,1] = numpy.array(wer_wb[:])
  retval[:,2] = numpy.array(hter_w[:])

  return retval 
  
def epsc_error_rates_omega(licit_neg, licit_pos, spoof_neg, spoof_pos, weights_beta, thresholds, omega=0.5): ### NEW!!!
  """Calculates several error rates: FAR_w and HTER_w for the given weights_beta and thresholds (the thresholds need to be computed first using the method: epsc_thresholds().) The parameter omega is fixed
  
  Keyword arguments:
  
    - licit_neg - numpy.array of scores for the negatives (licit scenario)
    - licit_pos - numpy.array of scores for the positives (licit scenario)
    - spoof_neg - numpy.array of scores for the negatives (spoof scenario)
    - spoof_pos - numpy.array of scores for the positives (spoof scenario)
    - weights_beta - numpy.array of the weight parameter balancing between real accesses and all negatives (zero-effort impostors and spoofing attacks)
    - thresholds - numpy.array with threshold values
    - omega - parameter balancing between impostors and spoofing attacks
  """
  retval = numpy.ndarray((numpy.array(weights).size, 3), 'float64')
  
  errors = [error_rates_at_weight(licit_neg, licit_pos, spoof_neg, spoof_pos, omega, thresholds[i], weights_beta[i]) for i in range(len(weights_beta))]
  
  far_w = [errors[i][3] for i in range(len(errors))]
  wer_wb = [errors[i][4] for i in range(len(errors))]
  hter_w = [errors[i][5] for i in range(len(errors))]

  retval[:,0] = numpy.array(far_w[:])
  retval[:,1] = numpy.array(wer_wb[:])
  retval[:,2] = numpy.array(hter_w[:])

  return retval        
