import math
import operator
import logging

import numpy
from scipy import special, polyfit, optimize


from itertools import izip, product

from radialx import signals

floor = math.floor
ceil = math.ceil

DEBUG = 1

DEFAULTS = dict(
  #####################################################################
  # empirical constants of the algorithm
  #####################################################################
  # the following vlaues cap our certainty about events in the world
  # they are mostly empirical, but qualitatively make sense
  # all values are log base 10
  #####################################################################
  # the prior
  pH = 0.0005,
  # you can never be more than 99.99% sure of being in the
  # noise:
  MAX_pH = math.log10(0.9999),
  # you can never be more than 99.99% sure about spurious data
  #      math.log10(0.0001) = -4.0
  MIN_pEgivenH = -4.0,
  # we want to be 99.99999999% sure we are out of the noise
  HARD_CUTOFF = -10,
  # HARD_CUTOFF**10
  E_HARD_CUTOFF = 1e-10,
  # we want to be 99 % sure we were out of the noise in
  # hindsight
  SOFT_CUTOFF = -1,
  )

class SignalibError(Exception):
  pass

def apply_drift(i, v, mean, err):
  # here
  slope_factor = 15
  if v > mean:
    stds = (v - mean) / err
    # here
    correction = slope_factor / stds**2
    correction = min(correction, slope_factor) 
    idx = i - correction
  else:
    idx = i
  return idx

def prob_intercept(idxs, probs):
  m, b = polyfit(idxs, probs, 1)
  xint = (-b)/m
  new_x_index = max(0, int(xint))
  return new_x_index   

def apply_drift_lkg(i, v, stds):
  slope_factor = 15
  if v > mean:
    stds = (v - mean) / err
    correction = slope_factor / stds**2
    correction = min(correction, slope_factor)
    idx = i - correction
  else:
    idx = i
  return idx

def noise_std_corr(values, history):
  indexes = []
  for (index, prob) in history:
    indexes.append(index)
  last_index = indexes[-1]
  last_val = values[-1]
  noise_vals = values[0:last_index]
  val = last_val/(numpy.std(noise_vals))
  overshoot = 200 * 1/(val**2) + 7
  return overshoot

def paretocorr(values, history, start, constants):
  ALPHA = 0.9
  CHI = 362.0
  DELTA = 7.0
  last_index = history[-1][0]
  last_val = values[-1]
  noise_vals = values[:last_index]
  stddev = numpy.std(noise_vals)
  val = last_val / stddev
  overshoot = ALPHA * (CHI**ALPHA) / (val**(ALPHA + 1)) + DELTA
  return overshoot


def paretocorr_avg(values, history, start, constants):
  ALPHA = 0.9
  CHI = 362.0
  DELTA = 7.0
  SAMPLE_WIDTH = 7
  # really want to make sure that this is integer division
  sig_end_idx = history[-1][0] + 1
  for (i,p) in reversed(history):
    if p > -10**constants['MIN_pEgivenH']:
      break
  sig_start_idx = i + 1
  # calculate the noise stddev
  noise_std = values[start:sig_start_idx].std()
  # calculate the sample mean in the signal
  hw = SAMPLE_WIDTH // 2
  sample_start_idx = sig_end_idx - hw
  sample_end_idx = sig_end_idx + SAMPLE_WIDTH - hw
  sample_mean = values[sample_start_idx:sample_end_idx].mean()
  # val
  val = sample_mean / noise_std
  overshoot = ALPHA * (CHI**ALPHA) / (val**(ALPHA + 1)) + DELTA
  return overshoot


def identity(x):
  return x

def prob_variance_drift(idxs, probs, i, values, corr=0):
  xint = prob_intercept(idxs, probs)
  erradd = 0
  for n in xrange(len(idxs)):
    yn = m * idxs[n] + b
    erradd = erradd + ((yn - probs[n]) ** 2)
  var = erradd/len(idxs)
  new_index = int(xint - corr)
  new_index = min(i, new_index)
  return new_index

def backtrack(idxs, probs, i, times, values, corr=0):
  xint = prob_intercept(idxs, probs)
  new_index = xint - corr
  new_index = signals.bound(new_index, 0, i)
  newtime = signals.interpolate2(new_index, times)
  newval = signals.interpolate2(new_index, values)
  return new_index, newtime, newval

"""
Working on new correction using earlier signal to
noise calculation
"""

def try_corr(values, history):
# correction based on a fit to a square root function
# using the avg diff and the std of the noise values
# works well (for 100 run at .45, 171 var)
  last_index = history[-1][0]
  noise_vals = values[:last_index]
  stddev = numpy.std(noise_vals)
  overshoot = 3.3 * 10**3 * stddev**.5 + 1.5
  return overshoot

def calc_early_sig(idxs, probs, times, values):
  """
  calculating with interpolated
  value corresponding to interpolated prob,
  and deviation calculated with noise values
  (until initial lag calculation)

  this will be better with an average around
  the hard cutoff point
  """

  Hard_Cutoff = DEFAULTS['HARD_CUTOFF']
  probs = numpy.array(probs)
  passed = (probs <= Hard_Cutoff)
  prob_idx = passed.nonzero()[-1][-1]
  val = values[prob_idx]
  x1 = times[prob_idx + 1]
  x2 = times[prob_idx]
  y1 = probs[prob_idx + 1]
  y2 = probs[prob_idx]
  m = (y2 - y1)/(x2 - x1)
  new_time = (Hard_Cutoff - y1)/m + x1
  v1 = values[prob_idx + 1]
  v2 = values[prob_idx]
  m2 = (v1 - v2)/(x2 -x1)
  val = m2*(new_time - x1) + v1
  last_index = idxs[-1]
  # noise should be defined as up to the soft cutoff
  # or better yet, the last point at the prob baseline (e.g. 10e-4)
  noise_vals = values[:last_index]
  sig = val/(numpy.std(noise_vals))
  return sig


def interpol_bayes(idx, times, values, probs, maxprob):
  x1 = times[idx-1]
  x2 = times[idx]
  p1 = probs[-2]
  p2 = probs[-1]
  y1 = values[idx-1]
  y2 = values[idx]
  mp = (p2 - p1)/(x2 - x1)
  newtime = (maxprob - p2)/mp + x2
  my = (y2-y1)/(x2-x1)
  newval = my * (newtime - x2) + y2
  return (newtime, newval)

def __debug_plot_history(i, history, values, start, j, noise):
  sig_idxs = numpy.arange(i, history[-1][0])
  signal_2d = sig_idxs, values[sig_idxs]
  noise_idxs = numpy.arange(start, j)
  noise_2d = numpy.arange(start, j), noise
  f_idx, _v = signals.intersect2ary(signal_2d, noise_2d)
  idx = int(round(f_idx))
  p = MyXYPlot()
  p.plot(numpy.arange(start,j), noise)
  p.plot(sig_idxs, values[sig_idxs])
  raw_input('Press Enter.')
  sys.exit()

def linear_backtrack(values, history, start, constants):
  sig_end_idx = history[-1][0] + 1
  for (i,p) in reversed(history):
    if p > -10**constants['MIN_pEgivenH']:
      break
  sig_start_idx = i + 1
  noise_b = values[start:sig_start_idx].mean()
  noise_m = 0.0
  sig_ys = values[sig_start_idx:sig_end_idx]
  sig_xs = numpy.arange(sig_start_idx, sig_end_idx)
  sig_m, sig_b = polyfit(sig_xs, sig_ys, 1)
  x, y = signals.intersect2(noise_m, noise_b, sig_m, sig_b)
  return int(x), y

def replicate_noise(ary, constants, corr_func=None):
  """
  # param pH: probability of hypothesis (in the noise)
  """
  pH = constants['pH']
  MAX_pH = constants['MAX_pH']
  MIN_pEgivenH = constants['MIN_pEgivenH']
  HARD_CUTOFF = constants['HARD_CUTOFF']
  E_HARD_CUTOFF = constants['E_HARD_CUTOFF']
  SOFT_CUTOFF = constants['SOFT_CUTOFF']
  #####################################################################
  # first signal starts at 3rd value (index of 2)
  # for noise, the 1st value (index of 0) is uninformative by itself
  #####################################################################
  first_sig = 2
  #####################################################################
  # the posterior must decay or the algorithm breaks down
  # in other words: forgetfulness is critical to be objective
  # the decay is a function of pE and is, in effect, applied to pH
  #####################################################################
  e_decay_factor = math.e
  decay_factor = math.log10(e_decay_factor)

  #####################################################################
  # process the function parameters
  #####################################################################
  times, values = ary
  pH = math.log10(pH)
  prior = pH
  # the series is also called a "replicate"

  #####################################################################
  # these are used for some types of pE calculations
  #####################################################################
  # s_values = numpy.sort(values)
  # rep_mean = numpy.mean(values)
  # rep_std = numpy.std(values)

  
  #####################################################################
  # a fundamental assumption is that we start in the noise
  # we precalculate some values we will need in the loop
  #####################################################################
  noise = values[:first_sig]
  mean = numpy.mean(noise)
  err = numpy.std(noise)
  len_noise = first_sig

  history = []
  found_signal = False
  # start of the noise: this may change as the series evolves
  start = 0
  len_rep = len(values)
  # the index of the last value of the series (replicate)
  rep_last = len_rep - 1
  for i in xrange(first_sig , rep_last):

    # start == this i (last j) when the baseline drops significantly
    if i == start:
      continue
    j = i + 1

    value = values[i]

    last_mean = mean
    last_err = err

    ###################################################################
    # our hypothesis is that the signal starts at values[j]
    ###################################################################
    # but we want to cap the length of the noise to avoid
    # misinterpreting signal as baseline drift to improve sensitivity
    ###################################################################
    noise = values[start:j]
    logging.debug(noise)
    signal = values[j:]
    len_sig = len(signal)
    # len_noise = len(noise)
    # mean = numpy.mean(noise)
    # err = numpy.std(noise)
    _accepts, _rejects = signals.chauvenet_keeplow(noise)
    noise_chvn = noise[_accepts]
    len_noise = len(noise_chvn)
    if len_noise < 7:
      continue
    mean = numpy.mean(noise_chvn)
    err = numpy.std(noise_chvn)

    ###################################################################
    # if no error then we must still be in noise--won't waste cpus
    ###################################################################
    if err == 0.0:
      continue

    diff = value - mean
    stds = diff / err

    ###################################################################
    # this corrects the hypothesis for a falling baseline
    ###################################################################
    if ((last_mean - last_err) > mean) and ((j-start) > 7):
      msg = 'mean dropped too much, starting over: %s %s' % (i, j)
      logging.info(msg)
      start = j
      pH = prior

    ###################################################################
    # calculating the probabilities
    ###################################################################
    # we want to cap the probability that we are in noise to something
    # reasonable--this helps, for instance, if intensity deteriorates
    pH = min(pH, MAX_pH)
    # integrate from -inf over normal prob-dens gives pEgivenH
    EgivenH = special.ndtr(-stds)
    # using log odds so we don't overflow the data types

    # this avoids math domain errors
    if EgivenH <= 1e-15:
      EgivenH = 1e-15

    pEgivenH = math.log10(EgivenH)
    
    # want to floor probability that we are in the signal regime
    # to something reasonable--e.g. decreasing intensity
    pEgivenH = max(pEgivenH, MIN_pEgivenH)

    ###################################################################
    # pE
    ###################################################################
    # this way limits the estimations to a realm of experience
    # it gives both signal and noise regimes equivalent weight
    # it is a modification of using the normal cdf on the full series
    ###################################################################
    win_last = j + len_noise
    win_end = min(rep_last, win_last)
    win_first = (j - len_sig)
    win_start = max(start, win_first)
    win_mean = numpy.mean(values[win_start:win_end])
    win_std = numpy.std(values[win_start:win_end])
    win_diff = value - win_mean
    win_stds = win_diff / win_std
    pE = special.ndtr(win_stds)

    ###################################################################
    # take the log of pE of course, cap pE at E_HARD_CUTOFF
    ###################################################################
    if pE <= E_HARD_CUTOFF:
      pE = HARD_CUTOFF
    else:
      pE = math.log10(pE)

    ###################################################################
    # Bayes Theorem: p(H|E) = p(E|H)*p(H)/p(E) = pHgivenE
    ###################################################################
    pHgivenE = (pEgivenH + pH) - pE

    ###################################################################
    # about to update posterior, so update history first
    ###################################################################
    history.append((i, pH))

    ###################################################################
    # checking the exit condition
    ###################################################################
    if pHgivenE <= HARD_CUTOFF:
      #################################################################
      # make sure that signal is really signal
      # if tests true, then the experiment probably failed anyway
      #################################################################
      err_of_mean = err / math.sqrt(len_noise)
      sigmean = numpy.mean(signal)
      if sigmean > (mean + err_of_mean):
        found_signal = True
      else:
        logging.info("Found it but can't trust it.")
      #################################################################
      # need to put this last posterior into the history for i+1 (j)
      #################################################################
      history.append((j, pHgivenE))
      break
    else:
      #################################################################
      # update our prior and decay it sensibly
      # our decay function is the simplest one possible
      #################################################################
      pH = pHgivenE + decay_factor

  #####################################################################
  # now we need to backtrack to a more reasonable certainty 
  # to get closer to the "true" pickup time
  #####################################################################
  if found_signal:
    idxs = []
    probs = []
    for (i,p) in reversed(history):
      if p >= SOFT_CUTOFF:
        break
      else:
        idxs.append(i)
        probs.append(p)
    if corr_func is None:
      corr = 0
    else:
      # corr = corr_func(values, history)
      logging.debug("correction function: %s" % corr_func.__name__)
      corr = corr_func(values, history, start, constants)

    idx, sig_time, sig_value = backtrack(idxs, probs, i,
                                         times, values, corr)

    sig_time = times[idx]

    new_sig_calc = calc_early_sig(idxs, probs, times, values)

    if DEBUG == 4: 
      __debug_plot_history(i, history, values, start, j, noise)

  else:
    logging.info
    delta_mean = values[-7:].mean() - values[:7].mean()
    sig_end = values[-7:].std() / math.sqrt(7)
    if delta_mean > sig_end:
      sig_time = times[0]
      sig_value = values[0]
      new_sig_calc = times[0]
    else:
      logging.debug('bayes algorithm failed')
      sig_time = numpy.NaN
      sig_value = numpy.NaN
      new_sig_calc = numpy.NaN
# added new_sig_calc for new correction testing
  return (sig_time, sig_value), history, new_sig_calc

def bayesian_pickup(ary):
  return replicate_noise(ary, DEFAULTS)
