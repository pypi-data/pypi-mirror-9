#! /usr/bin/env python

"""
keres specification
====================

  The most general usage will be

    1. + take the template file and modify the format strings
       to have values passed in through a dictionary
    2. + change to tmp directory 
    3. + a: run copasi with modified template file
    4. + b: read the copasi output file and convert to data
    5. + determine time point at which F > 0
    6. + c: apply B{detector noise} if any
    7. + determine lag time with all algorithms being tested
    8. + store the time point and lag times
    9. + loop back to 1 a number of times to
       create B{stochasticity noise}
    10. - change default values for template file 
        according to the testing we want to do
        to create B{scaling noise} (e.g. quantification error)
    11. - loop back to 1 a number of times
    12. - collect stats for 9 -> 1 loops
    13. - analyze stats
"""

import os
import sys
import popen2
import re
import operator
import math
from itertools import izip
import functools
import logging
import Tkinter as Tk

import numpy
import scipy
from scipy import stats
from scipy import polyfit
from scipy import optimize
from configobj import ConfigObj
import rpy2.robjects as robjects

from _signal import replicate_noise
from _signal import noise_std_corr
from _signal import paretocorr
from _signal import paretocorr_avg
from _signal import try_corr
from _signal import DEFAULTS as BAYESIAN_DEFAULTS

import pygmyplot

MARKER_OPEN = "{{"
MARKER_CLOSE = "}}"
ENCLOSURES = (MARKER_OPEN, MARKER_CLOSE)
MARKER_RE = re.compile(r'{{%\(.*?\)[EeFfGgsdis]}}')

class KeresError(Exception):
  """
  Base Exception for the keres package.
  """
  pass

class CopasiError(KeresError):
  """
  Raised if an error happens when runnning copasi.
  """
  pass

class TemplateFileError(KeresError):
  """
  Raised if the template file can not be interpreted
  or formatted to a correct .cps file.
  """
  pass

class FractionError(KeresError):
  """
  Raised when a fraction falls outside of 0 and 1.
  """
  pass

class ProgressError(Exception):
  pass

class SubprogressError(ProgressError):
  """
  Raised when a subprogress() is called on a Progressor
  instance that has not been called.
  """
  pass

class Progressor(object):
  def __init__(self, aslice, progress,
                     begin=0.0, end=1.0, context=None):
    """
    progress is a callable that takes as arguments
    (msg, frac, context).
    tmplt should be formattable with (number on, total, percent).
    if that fails, it will remain unformatted.
    last, first, and step is not like ranges and slices (ints).
    last is the last index, *not* the total number.
    first, if given, is the first index.
    For example, if iterating over range(10), and this the loop
    is on the third iteration, idx=2, last=9, step=1, and first=0.
    end and start should be floats between 0 and 1, inclusive.
    """
    stop = int(aslice.stop)
    if aslice.start is None:
      start = 0
    else:
      start = int(aslice.start)
    if aslice.step is None:
      step = 1
    else:
      step = int(aslice.step)
    end = float(end)
    begin = float(begin)
    steps = int(math.ceil((stop - start) / float(step)))
    if steps < 0:
      steps = 0
    if ((end <= 0 or end > 1) or 
        (begin < 0 or begin >= 1) or
        (begin >= end)):
      tmplt = "Limits of Progressor not valid. Got:" + " %s" * 5
      msg = tmplt % (start, stop, step, begin, end)
      raise ProgressError, msg
    self.progress = progress
    self.slc = aslice
    self.start = start
    self.stop = start + (step * (steps - 1))
    self.step = step
    self.begin = begin
    self.end = end
    self.context = context
    self.frac = begin
    self.steps = steps
    if self.steps > 0:
      self.spent = False
    else:
      self.spent = True
    self.index = start
    self.m = None
  def __repr__(self):
    atup = (self.slc, self.progress.__name__,
            self.begin, self.end, self.context)
    return """Progressor(%s, %s, %s, %s, %s)""" % atup
  def __iter__(self):
    while True:
      n = self.next()
      if n is not None:
        yield n
      else:
        break
  def __contains__(self, index):
    try:
      m = float(index - self.start) / self.step
      is_in = ((0 <= m < self.steps) and (m == int(m)))
    except TypeError:
      is_in = False
    return is_in
  def next(self):
    if self.index == self.start:
      self.m = 0
    if self.spent == True:
      raise StopIteration
    else:
      rval = self.do()
      if self.index == None:
        self.spent = True
        raise StopIteration
      else:
        index = self.index + self.step
        if index in self:
          self.set(self.index + self.step)
        else:
          self.set(None)
      return rval
  def iterate(self, sequence):
    for i in self:
      if i is not None:
        try:
          v = sequence[i]
        except IndexError:
          pass
        else:
          yield i, v
  def take(self, sequence):
    return list(v for (i,v) in self.iterate(sequence))
  def reset(self):
    self.set(self.start)
    self.m = None
  def set(self, index):
    steps = self.steps
    if index is not None:
      if steps == 0:
        msg = "Can't set index to `%s` because of 0 steps." % index
        raise ProgressError, msg
      else:
        m = float(index - self.start) / self.step
        if (0 <= m < self.steps) and (m == int(m)):
          if m == steps:
            index = None
        else:
          msg = "Index `%s` not in Progressor()." % index
          raise ProgressError, msg
    if index is None:
      self.frac = self.end
      m = steps
    else:
      p = (self.end - self.begin) * m / steps
      self.frac = self.begin + p
      m = int(m)
    self.index = index
    self.spent = False
    if index == self.start:
      self.m = None
    else:
      self.m = m
  def do(self):
    """
    index is the index the loop is on.
    if None is given for index, then self.progress is called
    with self.end as the fraction complete
    """
    if self.m is None:
      raise ProgressError, "Can not do() a reset Progressor()."
    else:
      self.progress(self)
      return self.index
  def finish(self):
    self.set(None)
    self.do()
  def subprogress(self, aslice, progress=None):
    """
    Creates a new Progressor instance that starts and ends
    between one 
    """
    if self.m is None:
      raise ProgressError, "Can't subprogress() a reset Progressor()."
    if self.spent:
      msg = "Can't subprogress() a spent Progressor()."
      raise ProgressError, msg
    begin = self.frac - (1.0 / self.steps)
    if progress is None:
      progress = self.progress
    return Progressor(aslice, progress, begin, self.frac, self.context)

def progressor_print(p):
  print "Step %s of %s (%6.2f%%)." % (p.m, p.steps, p.frac * 100)

def print_progress(msg, frac, context):
  prog = msg + " :  " + str(frac * 100) + "%"
  print prog

def log_info(msg, frac, context):
  prog = msg + " :  " + str(frac * 100) + "%"
  logging.info(prog)

def log_debug(msg, frac, context):
  prog = msg + " :  " + str(frac * 100) + "%"
  logging.debug(prog)


def make_copasi(tmplt, params):
  """
  takes markers, the params dictionary, and non_markers,
  formats and processes the markers, joins the formatted 
  markers with the non_markers part of the template,
  and returns the formatted copasi document as a string

  markers have this pattern::

     "{{formatting-marker}}"

  where '{formatting-marker' is a valid python string
  formatting marker used with dictionaries and the
  """
  markers, non_markers = tmplt
  marker_open, marker_close = ENCLOSURES
  new_markers = []
  for marker in markers:
    new_marker = marker % params
    new_marker = new_marker.replace(marker_open, '')
    new_marker = new_marker.replace(marker_close, '')
    new_markers.append(new_marker)
  zipped = []
  for atup in zip(non_markers, new_markers):
    zipped.extend(atup)
  zipped.append(non_markers[-1])
  copasi_document = "".join(zipped)
  return copasi_document

def split_template(tmplt_name, markerRE):
  """
  Takes the file named I{tmplt_name} and split it
  into markers and intervening portions based on
  the I{markerRE}. Returns the markers and intervening
  portions as a two-tuple with the markers first.

  Format of the Template File
  ===========================

     The template file is a modified copasi xml file
     (http://www.copasi.org/static/schema.xsd) wherein
     templating markers are designated by opening
     with "{{" and closed with "}}". The markers are
     standard python dictionary based markers. E.g.::

       <Constant key="Parameter_86" name="k1" value="{{%(k3)f}}"/>

     The exact regular expression and enclosures for the
     formatting markers a tunable.

  @param tmplt_name: file name of the copasi template file
  @param markerRE: regex that describes the formatting markers
  """
  # could do the next three lines with an idiomatic slurp:
  #    template = open(tmplt_name).read()
  template_file = open(tmplt_name)
  template = template_file.read()
  template_file.close()

  non_markers = markerRE.split(template)
  markers = markerRE.findall(template)
  return (markers, non_markers)


def run_copasi(general, params, tmplt):
  """
  Takes the path to the copasi executable, I{copasi_exec},
  and the path to the copasi .cps file, I{cps_file},
  and runs copasi with the .cps file. Checks on stderr
  whether a problem with the execution occured and
  raises a CopasiError if it has, otherwise None is
  returned.
  """
  if os.path.exists(params['result_file']):
    os.remove(params['result_file'])
  cps_doc = make_copasi(tmplt, params)
  open(general['tmp_cps'], 'w').write(cps_doc)
  copasi_exec = general['copasise']
  cps_file = general['tmp_cps']
  command = " ".join([copasi_exec, cps_file])
  copin, copout, coperr = popen2.popen3(command)
  err_msg = coperr.read()
  if err_msg:
    raise CopasiError(err_msg)
  ary = read_output(params['result_file'])
  magnitude = numpy.max(ary[1])
  return ary, magnitude

def run_copasi_biphasic(general, params, tmplt):
  ary, magnitude = run_copasi(general,params,tmplt)
  times, values = ary
  maxdex = values.searchsorted(magnitude, side='left')
  real_idx = values.searchsorted(0, side='right')
  phase1_times, phase1 = ary[:,:maxdex+1]
  phase2 = values[real_idx:]
  phase2 = phase2 * general['amp_phase_2']
  phase2 = phase2 + magnitude
  new_values = numpy.concatenate((phase1, phase2))
  delta_time = numpy.mean(times[1:] - times[:-1])
  phase2_times = ((numpy.arange(phase2.size) * delta_time) +
                  phase1_times[-1])
  times = numpy.concatenate((phase1_times, phase2_times))
  return numpy.array([times, new_values]), magnitude



def read_output(out_name):
  """
  The I{out_name} should have a format where

     - first line is two tab delimited headings
     - the headings are (1) time and (2) concentration of
       product
     - second and later lines are tab delimited values
       for time and concentration in that order

  Returns 2xN numpy float array with the first row as time
  and the second as concentration.
  """
  outfile = open(out_name)
  outfile.next()
  times = []
  concs = []
  for aline in outfile:
    atime, aconc = aline.split()
    atime = float(atime)
    aconc = float(aconc)
    times.append(atime)
    concs.append(aconc)
  tc = numpy.array([times, concs])
  return tc


def take_n(ary, new_size):
  """
  I{ary} is a 2-d array of and I{newr_size} is the desired
  new size. If new_size doesn't go evenly into ary, a
  close approximation is used to keep most of ary.
  """
  new_size = int(new_size)
  old_size = ary[0].size
  bin_size = old_size/new_size
  new_size = old_size/bin_size
  old_resized = new_size * bin_size
  idxs = numpy.arange(0, old_resized, bin_size)
  return ary[:,idxs]

def take_avgs(ary, bin_size):
  """  
  Takes a 2-D array and averages the points in each interval
  of size I{bin_size} and creates a new array with 
  averages.
  """
  rows, cols = ary.shape
  bry = numpy.reshape(ary, (rows, cols/bin_size, bin_size))
  return bry.mean(2)

def find_pickup(ary, cutoff):
  """
  Goes through a numpy array consisting of time (I{times}
  and concentrations (I{concs}) finds the first
  concentration that is greater than the I{cutoff}
  and returns the corresponding time.
  """
  times, concs = ary
  idx = concs.searchsorted(cutoff, side="right")
  if idx == len(times):
    idx = len(times) - 1
  return times[idx]

def fitfunc(p, x):
   return  p[0] + p[1]/(p[2] + math.e **(p[3] -x)) 
   
def errfunc(p, x, y):
  return fitfunc(p, x) - y

def fit_sigmoid(ary):
  p = [1, 1, 1, 1]
  times, concs = ary
  p2, success = optimize.leastsq(errfunc, p[:], args=(times, concs))
  d = p2[3]
  i = int(d+200)
  i = max(0, i)
  idx = min(i, len(times)-1)
  return(times[idx], concs[idx]), []

def interpolfmax(idx, times, values, maxval):
  if idx == 0:
    newtime = times[0]
  else:
    x1 = times[idx-1]
    x2 = times[idx]
    y1 = values[idx-1]
    y2 = values[idx]
    m = (y2-y1)/(x2-x1)
    newtime = (maxval - y1)/m + x1
  return (newtime, maxval)


def algorithm_fmax(ary, frac):
  """
  Will find the first point that is I{frac} (0 to 1) fraction
  of the maximum value in the array.
  """
  if not (0 <= frac <= 1):
    tmplt = "Fractions should be between 0 and 1, not %s."
    msg = tmplt % frac
    raise FractionError, msg
  times, concs = ary
  bumped = bump(concs)
  difference = concs[0] - bumped[0]
  maxval = (frac * max(bumped)) + difference
  passed = (concs >= maxval)
  idx = passed.nonzero()[0][0]
  newtime, maxval = interpolfmax(idx, times, concs, maxval)
  # changes so it doesn't return less than 0
  if newtime < 0:
    newtime = times[0]
  #  return (times[idx], concs[idx])
  return newtime, maxval

def algorithm_50(ary):
  return algorithm_fmax(ary, 0.5), None, None

def algorithm_10(ary):
  return algorithm_fmax(ary, 0.1), None, None


def make_stoch_noise(general, params, tmplt,
                     algorithms, a_dist, ary, magnitude,
                     op=operator.add, progress=None):
  """
  Takes the distribution function I{a_dist} and a list
  of algorithms and generates a list of pickup times
  for the number of 'stochastic_n' iterations specified
  in general for each algorithm. Also returns the "real"
  pickup time. The returned value is the 2-tuple of the
  "real" pickup time and the list of lists of stochastic
  times for the algorithms.
`
  @param general: these are the general settings for the run
  @param params: parameter dictionary for run
  @param tmplt: 2-tuple with markers and non-markers
  @param a_dist: a random distribution, takes optional size arg
  @param algorithms: a list of callables that decides when the
                     pickup is for noisy data
  """
  msg_tplt = "  On stochastic %s of %s"
  real_time = find_pickup(ary, 0)
  stoch_times = [[] for algo in algorithms]
  stochastic_n = general['stochastic_n']
  do_graph = True
  for anum in xrange(stochastic_n):
    noisy_ary, bumpsize = apply_noise(ary, magnitude, a_dist, op)
    title_tup = (general['stoch_noise'], real_time)
    options = {'figsize':general['figsize'],
               'title':"noise: %5.2f | real: %s s" % title_tup}
    do_progress(anum, stochastic_n, msg_tplt, progress, None)
    for times, algo in izip(stoch_times, algorithms):
      (time, value), history, signoise = algo(noisy_ary)
      times.append(time)
      delta = abs(real_time - time)
      do_history = ( ( (
                         (general['plot_history_cutoff'] is not None) and
                         (delta > general['plot_history_cutoff']) 
                       ) or
                       (general['do_progress_plot'] and do_graph)
                     ) and
                     history
                   )
      do_history = bool(do_history)
      logging.debug("---------------------------")
      logging.debug("  algorithm: %s" % algo.__name__)
      logging.debug("----------- real time: %s " % real_time)
      logging.debug("                 time: %s " % time)
      logging.debug("delta: %s" % delta)
      logging.debug("plot_history_cutoff: %s" %
                    general['plot_history_cutoff'])
      logging.debug("do_history: %s" % do_history)
      
      if do_history:
        general['plot_history_cutoff'] = delta
        if general['plot_noiseless']:
          noiseless = ary + bumpsize
        else:
          noiseless = None
        plot_history(history, noisy_ary, noiseless, real_time, time, options)
      # adding plot_for_figs here, better place somewhere else
      #        plot_for_figs(general, noisy_ary)
      elif (time is numpy.NaN) and (general['plot_nans'] > 0):
        general['plot_nans'] -= 1
        plot_history(history, noisy_ary, real_time, time, options)
    do_graph = False
  return real_time, numpy.array(stoch_times), history, signoise

def norm_test_p(ary_1d):
  d, p_norm = stats.normaltest(ary_1d)
  return p_norm

def find_avg_diff(real_times, stoch_times):
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  v_norms = stoch_times - real_times.reshape((real_times.size, 1))
  return v_norms.mean(axis=2).mean(axis=1)

def find_spread_times(stoch_times):
  """
  Calculates the mean standard deviation for all stochastic times
  measured from a single lag time.
  """
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  spreads = numpy.apply_along_axis(numpy.std, 2, stoch_times)
  return spreads.mean(axis=1)



def norm_test_var(real_times, stoch_times):
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  v_norms = stoch_times - real_times.reshape((real_times.size, 1))
  v_norms = v_norms**2
  return v_norms.mean(axis=2).mean(axis=1)


def norm_test_var1050(real_times, stoch_times,
                      real10list, real50list):
  """
  this new version will work for stochastic_n > 1
  """
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  times = numpy.array([real10list, real50list, real_times])
  # times shape should be
  #          (number of algos, scaling_n, 1)
  times = times.reshape(times.shape + (1,))
  diffsq = (stoch_times - times)**2
  return diffsq.mean(axis=2).mean(axis=1)


def do_every(do_n, total):
  if do_n > 0:
    do_ev, _r = divmod(total, do_n)
  else:
    do_ev = None
  if do_ev == 0:
    do_ev = 1
  return do_ev

def ks_test_r_exp(times):
  """
  returns a single value from r of the probability for exp
  """
  try:
    times = times.tolist()
  except AttributeError:
    pass
  logging.debug("*****************************************************")
  logging.debug(" ################## ks_test_r_exp ##################")
  logging.debug("*****************************************************")
  logging.debug(str(numpy.array(times)))
  robjects.globalenv['tth'] = times
  ks_test = robjects.r(
    """
    tth <- as.vector(tth, mode = 'numeric')
    tthdf <- ecdf(tth)
    tth1 <- tthdf(tth)
    tth_fit1 <- nls(tth1 ~ (0.5 *
                            ((sign(1-exp(-(tth-dt)/sd(tth))) *
                                  (1-exp(-(tth-dt)/sd(tth)))) +
                             (1-exp(-(tth-dt)/sd(tth))))),
                    data=as.list(tth),
                    start=list(dt=mean(tth)-sd(tth)),
                    trace=FALSE, algorithm="port")
    summary(tth_fit1)
    ks.test(tth - coef(tth_fit1)[1], "pexp",
            rate=1/sd(tth), exact = FALSE)
    """)
  robjects.r['rm']('tth')
  logging.debug('ks test for exp: %s' % str(ks_test[1]))
  logging.debug("####################################################")
  # ks_test[1] is a single value list from R
  return ks_test[1][0]

def apply_ks_forgiving(stoch_times, func):
  """
  this new version will work for stochastin_n > 1
  """
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  def _ks_forgiving(ary):
    try:
      rval = func(ary)
    except robjects.rinterface.RRuntimeError, e:
      logging.debug(str(e))
      rval = 0.0
    return rval
  return numpy.apply_along_axis(_ks_forgiving, 1, stoch_times)

def apply_ks(stoch_times, func):
  """
  Finds the mean of the KS-test for the stoch times measured
  for each lag time.
  """
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  ks_probs = apply_ks_forgiving(stoch_times, func)
  return ks_probs.mean(axis=1)

def false_negative_rate(stoch_times, func, cutoff):
  # stoch_times shape should be
  #          (number of algos, scaling_n, stochastic_n)
  probs = apply_ks_forgiving(stoch_times, func)
  fails = probs < cutoff
  return fails.mean(axis=1)


def apply_ks_real(real_times, func):
  real_times = numpy.array(real_times)
  real_times = real_times.tolist()
  pval = func(real_times)
  return pval  


def ks_test_r_norm(times):
  """
  returns a single value from r of the probability for norm
  """
  try:
    times = times.tolist()
  except AttributeError:
    pass
  logging.debug("*****************************************************")
  logging.debug(" ################# ks_test_r_norm ##################")
  logging.debug("*****************************************************")
  logging.debug(str(numpy.array(times)))
  robjects.globalenv['tth'] = times
  ks_test = robjects.r(
    """
    tth <- as.vector(tth, mode = 'numeric')
    tthdf <- ecdf(tth)
    tth1 <- tthdf(tth)
    tth_fit1 <- nls(tth1 ~ (0.5 *
                            ((sign(1-exp(-(tth-dt)/sd(tth))) *
                             (1-exp(-(tth-dt)/sd(tth)))) +
                            (1-exp(-(tth-dt)/sd(tth))))),
                    data=as.list(tth),
                    start=list(dt=mean(tth)-sd(tth)),
                    trace=FALSE,
                    algorithm="port")
    summary(tth_fit1)
    ks.test(tth, "pnorm",
            mean=mean(tth), sd=sd(tth), exact=FALSE)
    """)
  robjects.r['rm']('tth')
  logging.debug('ks test for norm: %s' % str(ks_test[1]))
  logging.debug("####################################################")
  # ks_test[1] is a single value list from R
  return ks_test[1][0]

def p_kstest(ary, cdf):
  d, p = stats.kstest(ary, cdf)
  return p


def do_progress(idx, tot, prog_tmplt, progress, context):
  if progress is not None:
    _args = (idx+1, tot)
    _frac = float(idx)/tot
    msg = prog_tmplt % _args
    progress(msg, _frac, context)

def plot_from_context(context):
  do_plot, x, y, options, p = context
  if do_plot:
    if p is None:
      master = options.pop('master', None)
      title = options.pop('title', '')
      if master is None:
        master = Tk.Toplevel()
        master.title(title)
      figsize = options.pop('figsize', None)
      if x is None:
        p = pygmyplot.xy_plot(y, master=master, figsize=figsize)
      else:
        p = pygmyplot.xy_plot(x, y, master=master, figsize=figsize)
      options['figsize'] = figsize
      options['title'] = title
      options['master'] = master
    else:
      # xlim = p.axes.get_xlim()
      # ylim = p.axes.get_ylim()
      p.plot(x, y)
      # p.axes.set_xlim(*xlim)
      # p.axes.set_ylim(*ylim)
      # p.refresh()
      p.zoom_all()
      p.refresh()
    if 'label' in options:
      p.axes.legend()
    xlim = options.pop('xlim', None)
    if xlim is None:
      xlim = p.axes.get_xlim()
    p.axes.set_xlim(xlim)
    # trying to change number font
    p.canvas.show()
    options['xlim'] = xlim
    return p
     

def plot_history(history, noisy_ary, noiseless, real_time, time, options):
  if history:
    label = "%s : %s" % (real_time, time)
    options['title'] = str(options['title']) + " " + label
    context = True, noisy_ary[0], noisy_ary[1], options, None
    p = plot_from_context(context)
    options['marker'] ='x'
    # options['xlim'] = (0, noisy_ary[0].size - 1)
    x, y = [numpy.array(a) for a in zip(*history)]
    context = True, x, y, options, None
    plot_from_context(context)
    if noiseless is not None:
      context = True, noiseless[0], noiseless[1], options, p
      plot_from_context(context)

def make_plot_progress(progress):
  def _plot_progress(msg, _frac, context):
    if progress is not None:
      progress(msg, _frac, None)
    plot_from_context(context)
  return _plot_progress
   
def plot_variance_and_lag(history):
  # for bayesian, sqrt of variance of entire history probs treated
  # as a unit divided by slope of line fit (plot_variance_and_lag)
  if history is not None:
    index = []
    problist = []
    avgvar = []
    for (idxs, probs) in history:
      index.append(idxs)
      problist.append(probs)
    m, b = polyfit(index, problist, 1)
    varlist = []
    for i in xrange(len(index)):
      var = (((m * index[i] + b) - problist[i])**2)
      varlist.append(var)
    varlist = numpy.array(varlist)
    v = (math.sqrt(numpy.sum(varlist))/numpy.size(varlist))/m
  else:
    v = None
  return v

def generate_lags(lagn, expo_scale, times, cutoff, frac):
  count = 0
  test_lags = []
  fexp_lag = make_fexponential(expo_scale)
  t = int(frac * len(times))
  for anum in xrange(lagn):
    lag_len = int(fexp_lag(1)) + t
    test_lags.append(lag_len)
  old = numpy.array(test_lags)
  last = 0.0
  lags = None
  while lags is None:
    test_lag = int(fexp_lag(1)) + t
    rand_idx = numpy.random.randint(lagn)
    test_lags = old.copy()
    test_lags[rand_idx] = test_lag
    count += 1
    try:
      kslags = apply_ks_real(test_lags, ks_test_r_exp)
      if kslags > cutoff:
        msg = "ks of lag times (after %s tries): %s" % (count, kslags)
        logging.info(msg)
        lags = (test_lags, kslags)
      else:
        tmplt = "ks of lag times < %s (after %s tries): %s"
        msg = tmplt % (cutoff, count, kslags)
        logging.info(msg)
        logging.debug("ks of lags < %s" % cutoff)
        if kslags > last:
          old = test_lags
          last = kslags
    except robjects.rinterface.RRuntimeError, e:
      logging.debug(str(e))
  return lags

def lag_time_loop_det_ksed(general, params, tmplt, algorithms,
                  simulator, progressor=None):
  """
  Runs the simulation and adds a deterministic phase, then random lag
  time and height variation to the data based on an exponential
  distribution, then k-s tests the lag times to get an exponential
  distribution with a p-val > exp_dist_stringency,
  and then adds stochastic noise based on a normal distribution,
  then stores the real pickup time in the list real_time, and the
  times the algorithms found in the array stoch_times.

  **This is the loop used by bayestest.**
  """
  prog_tmplt = "On stochastic %s of %s"
  ary, magnitude = simulator(general, params, tmplt)
  timepoints = general['timepoints']
  ary = take_n(ary, general['timepoints'])
  times, concs = ary
  lagn = general['scaling_n']
  expo_scale = int(timepoints * general['exponential_scale'])
  fnorm_height = make_fnorm(0, general['height_scale'])
  fnorm_stoch = make_fnorm(0, general['stoch_noise'])
  if general['plot_n'] > 0:
    plot_every, _r = divmod(lagn, general['plot_n'])
  else:
    plot_every = None
  if plot_every == 0:
    plot_every = 1
  # the real times for pick-up
  real_times = []
  # the real times at 10% max
  real10list = []
  # the real times at 50% max
  real50list = []
  # the algorithmically determined times
  # stoch_times shape should be
  #          (scaling_n, number of algos, stochastic_n)
  stoch_times = []
  # for bayesian, sqrt of variance of entire history probs treated
  # as a unit divided by slope of line fit (plot_variance_and_lag)
  varlist = []
  # std of the entire series treated as a unit
  stddevs = []
  # (value at the hard cutoff) / (std of the noise)
  vallist = []
  # (sig at hard cutoff) / (noise of "noise phase") for Bayesian
  signoises = []

  testlags, kslags = generate_lags(lagn, expo_scale, times,
                                   general['exp_dist_stringency'],
                                   general['det_frac'])
  # trying to generate lags in different loop   
  for anum in xrange(lagn):
    if plot_every is None:
      general['do_progress_plot'] = False
    else:
      general['do_progress_plot'] = (anum % plot_every == 0)

    lag_len = testlags[anum]
    if progressor is not None:
      progressor.next()
    # do_progress(anum, lagn, prog_tmplt, progress, None)
    heightvary = fnorm_height(1)
    lag_concs = numpy.zeros(lag_len, numpy.float)
    new_concs = numpy.append(lag_concs, (concs * (heightvary + 1)))
    new_times = numpy.arange(new_concs.size)
    ary = numpy.array([new_times, new_concs])
    # adding to collect 10% and 50% on noiseless data
    if algorithms[0] == algorithm_10:
      (time10, conc10), history, sig = algorithm_10(ary)
      real10list.append(time10)
    if algorithms[1] == algorithm_50:
      (time50, conc50), history, sig = algorithm_50(ary)
      real50list.append(time50)
    if general['scale_noise']:
      noise_op = scale_noise_to_data
    else:
      noise_op = add_frac_spread
    rslt = make_stoch_noise(general, params, tmplt,
                            algorithms, fnorm_stoch,
                            ary, magnitude,
                            op=noise_op,
                            progress=log_debug)
    # rl_t : real_time
    # stoch : array of n-algo arrays of stoch_times
    #         (algorithmically determined times)
    #         stoch shape is (algos, stochastic_n)
    # history : (index, probability) pairs
    # signoise : result from calc_early_sig
    #            (approx val @ hard cutoff / std of noise)
    rl_t, stoch, history, signoise = rslt
    # where i added scale_noise_to_data.
    # change back to add_frac_spread later
    real_times.append(rl_t)
    stoch_times.append(stoch)
    # (sig at hard cutoff) / (noise of "noise phase") for Bayesian
    signoises.append(signoise) 

    indexes = [index for (index, prob) in history]
    last_index = indexes[-1]
    last_val = new_concs[last_index]
    noise_vals = new_concs[:last_index]
    val = last_val/(numpy.std(noise_vals))
    # (value at the hard cutoff) / (std of the noise)
    vallist.append(val)

    dev = numpy.std(ary[1])
    stddevs.append(dev)
    # for bayesian, sqrt of variance of entire history probs treated
    # as a unit divided by slope of line fit (plot_variance_and_lag)
    var = plot_variance_and_lag(history)
    if var is not None:
      varlist.append(var)

  # for bayesian, sqrt of variance of entire history probs treated
  # as a unit divided by slope of line fit (plot_variance_and_lag)
  variation = numpy.mean(varlist)
  # std of the entire series treated as a unit
  stddev = numpy.mean(stddevs)
  # (value at the hard cutoff) / (std of the noise)
  value = numpy.mean(vallist)
  # (sig at hard cutoff) / (noise of "noise phase") for Bayesian
  #            result from calc_early_sig()
  #            (approx val @ hard cutoff / std of noise)
  signoisemean = numpy.mean(signoises)
  # real times
  real_times = numpy.array(real_times)
  # algorithmically determined times from noisey data
  stoch_times = numpy.array(stoch_times)
  # make shape (algos, scaling_n, stochastic_n)
  stoch_times = stoch_times.swapaxes(0, 1)
  #####################################################################
  # minimal return values:
  # return (real_times, real10list, real50list,
  #         stoch_times, value)
  #####################################################################
  # added signoises for correction testing purposes
  return (signoises, real_times, stoch_times,
          history, value, signoisemean,
          real10list, real50list, stddev)


def lag_time_loop_det(general, params, tmplt, algorithms,
                      simulator, progress=None):
  """
  Runs the simulation and adds a deterministic phase, then
  random lag time and height variation to the data based on
  an exponential distribution and then adds stochastic
  noise based on a normal distribution, then stores the
  real pickup time in the list real_time, and the times the
  algorithms found in the array stoch_times. 
  """
  prog_tmplt = "On stochastic %s of %s"
  ary, magnitude = simulator(general, params, tmplt)
  timepoints = general['timepoints']
  ary = take_n(ary, general['timepoints'])
  times, concs = ary
  lagn = general['scaling_n']
  expo_scale = int(timepoints * general['exponential_scale'])
  fexp_lag = make_fexponential(expo_scale)
  fnorm_height = make_fnorm(0, general['height_scale'])
  fnorm_stoch = make_fnorm(0, general['stoch_noise'])
  real_times = []
  stoch_times = []
  if general['plot_n'] > 0:
    plot_every, _r = divmod(lagn, general['plot_n'])
  else:
    plot_every = None
  if plot_every == 0:
    plot_every = 1
  varlist = []
  stddevs = []
  vallist = []
  real10list = []
  real50list = []
  for anum in xrange(lagn):
    if plot_every is None:
      general['do_progress_plot'] = False
    else:
      general['do_progress_plot'] = (anum % plot_every == 0)
    lag_len = int(fexp_lag(1)) + .1*len(times)
    testlags.append(lag_len)
    do_progress(anum, lagn, prog_tmplt, progress, None)
    heightvary = fnorm_height(1)
    lag_concs = numpy.zeros(lag_len, numpy.float)
    new_concs = numpy.append(lag_concs, (concs * (heightvary + 1)))
    new_times = numpy.arange(new_concs.size)
    ary = numpy.array([new_times, new_concs])
    # adding to collect 10% and 50% on noiseless data
    if algorithms[0] == algorithm_10:
      (time10, conc10), history = algorithm_10(ary)
      real10list.append(time10)
    if algorithms[1] == algorithm_50:
      (time50, conc50), history = algorithm_50(ary)
      real50list.append(time50)
    rslt = make_stoch_noise(general, params, tmplt,
                            algorithms, fnorm_stoch, ary, magnitude,
                            op=add_frac_spread,
                            progress=progress)
    rl_t, stoch, history = rslt
    # where i added scale_noise_to_data
    # change back to add_frac_spread later`
    real_times.append(rl_t)
    stoch_times.append(stoch)

    indexes = []
    for (index, prob) in history:
      indexes.append(index)
    last_index = indexes[-1]
    last_val = new_concs[last_index]
    noise_vals = new_concs[0:last_index]
    val = last_val/(numpy.std(noise_vals))
    vallist.append(val)

    dev = numpy.std(ary[1])
    stddevs.append(dev)

    var = plot_variance_and_lag(history)
    if var is not None:
      varlist.append(var)

  variation = numpy.mean(varlist)
  stddev = numpy.mean(stddevs)
  value = numpy.mean(vallist)
  real_times = numpy.array(real_times)
  stoch_times = numpy.array(stoch_times)
  return (real_times, stoch_times, history,
          value, real10list, real50list)

def lag_time_loop(general, params, tmplt, algorithms,
                  simulator, progressor=None):
  """
  Runs the simulation and adds a random lag time and height variation 
  to the data based on an exponential distribution and then adds
  stochastic noise based on a normal distribution, then stores
  the real pickup time in the list real_time, and the times the
  algorithms found in the array stoch_times. 
  """
  prog_tmplt = "On stochastic %s of %s"
  ary, magnitude = simulator(general, params, tmplt)
  timepoints = general['timepoints']
  ary = take_n(ary, general['timepoints'])
  times, concs = ary
  lagn = general['scaling_n']
  expo_scale = int(timepoints * general['exponential_scale'])
  fnorm_height = make_fnorm(0, general['height_scale'])
  fnorm_stoch = make_fnorm(0, general['stoch_noise'])
  if general['plot_n'] > 0:
    plot_every, _r = divmod(lagn, general['plot_n'])
  else:
    plot_every = None
  if plot_every == 0:
    plot_every = 1
  real_times = []
  real10list = []
  real50list = []
  stoch_times = []
  varlist = []
  stddevs = []
  vallist = []
  signoises = []
  testlags, kslags = generate_lags(lagn, expo_scale, times,
                                   general['exp_dist_stringency'],
                                   general['det_frac'])
  for anum in xrange(lagn):
    if plot_every is None:
      general['do_progress_plot'] = False
    else:
      general['do_progress_plot'] = (anum % plot_every == 0)

    lag_len = testlags[anum]
    if progressor is not None:
      progressor.next()
    # do_progress(anum, lagn, prog_tmplt, progress, None)
    heightvary = fnorm_height(1)
    lag_concs = numpy.zeros(lag_len, numpy.float)
    new_concs = numpy.append(lag_concs, (concs * (heightvary + 1)))
    new_times = numpy.arange(new_concs.size)
    ary = numpy.array([new_times, new_concs])
    if algorithms[0] == algorithm_10:
      (time10, conc10), history, sig = algorithm_10(ary)
      real10list.append(time10)
    if algorithms[1] == algorithm_50:
      (time50, conc50), history, sig = algorithm_50(ary)
      real50list.append(time50)
    rslt = make_stoch_noise(general, params, tmplt,
                            algorithms, fnorm_stoch, ary, magnitude,
                            op=add_frac_spread,
                            progress=log_debug)
    rl_t, stoch, history, signoise = rslt
    # where i added scale_noise_to_data
    # change back to add_frac_spread later`
    real_times.append(rl_t)
    stoch_times.append(stoch)
    signoises.append(signoise)
 
    indexes = []
    for (index, prob) in history:
      indexes.append(index)
    last_index = indexes[-1]
    last_val = new_concs[last_index]
    noise_vals = new_concs[0:last_index]
    val = last_val/(numpy.std(noise_vals))
    vallist.append(val)
  
    dev = numpy.std(ary[1])
    stddevs.append(dev)

    var = plot_variance_and_lag(history)
    if var is not None:
      varlist.append(var)

  variation = numpy.mean(varlist)
  stddev = numpy.mean(stddevs)
  value = numpy.mean(vallist)
  signoisemean = numpy.mean(signoises)
  logging.debug('signaoisecalc: %s' % signoisemean)
  real_times = numpy.array(real_times)
  stoch_times = numpy.array(stoch_times)
  return (real_times, stoch_times, history, value,
          signoisemean, real10list, real50list, stddev)


 
def apply_scaling_noise(general, params):
  """
  Will create a I{new_params} dictionary by adding a random
  value generated by I{adist} to the original concentration
  of reactant A  specified in the I{params} dictionary to 
  create scaling noise in the measurements.
  """
  new_params = params.copy()
  for idx, key in enumerate(general['scale_keys']):
    fnorm = make_fnorm(0, general['scaling_noises'][idx])
    randval = fnorm()
    new_params[key] = params[key] * (1 + randval)
  return new_params

def make_exp_cdf(lam):
  """
  Makes the cdf function for the exponential
  with the scale of I{lam}.
  """
  lam = float(lam)
  def _cdf(x):
    return 1 - math.e**((-1/lam)*x)
  return _cdf

def make_fnorm(loc, scale):
  """
  Returns the numpy.random.normal() function as a partial
  function with the loc and scale parameters set to
  I{loc} and I{scale}. The returned function is called
  like this (assuming its named "fnorm()")::

     fnorm(size)

  Where I{size} has the same meaning as in numpy.random.normal().
  """
  return functools.partial(numpy.random.normal, loc, scale)

def make_fexponential(scale):
  """
  Returns the numpy.random.exponential() funtion as a partial
  function with the scale parameter set to I{scale}. The
  returned function is called like this (assuming it's named
  "fexponential()")::
      fexponential(size)
  Where I{size} has the same meaning as in numpy.random.exponential().
  """
  return functools.partial(numpy.random.exponential, scale)

def make_fbinomial(n,p):
  """
  Returns the numpy.random.binomial() function as a partial
  function with the n parameter and the p paramater set to
  I{n} and I{p}. The returned function is called like this
  (assuming it's named "fbinomial()")::
      fbinomial(size)
  Where I{size} has the same meaning as in numpy.random.binomial().
  """
  return functools.partial(numpy.random.binomial, n, p)

def add_frac_spread(ary, magnitude, randvals):
  spread = magnitude - ary.min()
  randvals = randvals * spread
  return ary + randvals

def scale_noise_to_data(ary, magnitude, randvals):
  noisy = add_frac_spread(ary, magnitude, randvals)
  noise = numpy.random.standard_normal(noisy.shape)
  noise = noise - noise.min()
  noise = noise/noise.max()
  return noisy*noise

def bump(ary):
  return ary - ary.min()
 
def apply_noise(ary, magnitude, some_dist, op):
  """
  Returns a new numpy.array with the noise from the distribution
  defined by I{some_dist} added to the values from I{ary}.

  The I{some_dist} function takes only one argument, namely
  its size, which will be the length of I{ary}.
  """
  times, concs = ary
  length = concs.size
  randvals = some_dist(length)
  unbumped = op(concs, magnitude, randvals)
  bumped = bump(unbumped)
  bumpsize = -unbumped.min()
  new_ary = numpy.array([times, bumped])
  return new_ary, bumpsize

def scale_noise_to_signal(some_dist, magnitude, ary):
  """
  Will return an array with noise from the distribution I{some_dist}
  scaled to the values in I{ary} so the noise gets bigger as the
  values do.
  """
  times, concs = ary
  length = concs.size
  randvals = some_dist(length)
  new_concs = conc * (1 + randval)
  return numpy.vstack(times, new_concs) 

def make_ecdf(V):
  sorted_vals = numpy.sort(V)
  cdf_vals = []
  for i in range(len(sorted_vals)):
    if i == 0:
      cdf = 0
    elif sorted_vals[i] == sorted_vals[i-1]:
      cdf = cdf_vals[i-1]
    else:
      cdf = float(i)/float(len(sorted_vals))
    cdf_vals.append(cdf)
  return cdf_vals

def fit_stoch_lag(V, maxfev=10000):
  E = make_ecdf(V)
  std_V = numpy.std(V)
  v0 = [numpy.mean(V) - std_V]
  v, success = scipy.optimize.leastsq(e, v0,
                                      args=(V, E), maxfev=maxfev)
  return v

def fp(v, x):
  std_V =  numpy.std(v)
  chi_i = 1 - numpy.exp((v-x)/std_V)
  return 0.5 * ((numpy.sign(chi_i) * chi_i) + chi_i)

def errdif(v, x, y):
  return fp(v, x) - y

def make_exp_cdf(lam):
  def cdf(x):
    return 1 - math.e**((-1/lam)*x)
  return cdf


def make_norm_cdf(mean, dev):
  def cdf(x):
    return 1/2*(1 + scipy.special.erf((x-mean)/(dev*math.sqrt(2))))
  return cdf


def interpolate(ary):
  times, values = ary
  newvals = []
  newtimes = []
  for i in xrange(len(times)-1):
    x1 = times[i]
    x2 = times[i+1]
    newtimes.append((x2-x1)/2.0 + x1)
    y1 = values[i]
    y2 = values[i+1]
    newy = (y2-y1)/2.0 + y1
    newvals.append(newy)
  addedtimes = []
  addedvals = []
  for i in xrange(len(newtimes)):
    addedtimes.append(times[i])
    addedvals.append(values[i])
    addedtimes.append(newtimes[i])
    addedvals.append(newvals[i])
  addedtimes.append(times[-1])
  addedvals.append(values[-1]) 
  return addedtimes, addedvals  



def setup(cfg_file):
  settings = ConfigObj(cfg_file, unrepr=True)
  general = settings['general']
  params = settings['copasi-params']
  tmplt_name = general['tmplt_file']
  tmplt = split_template(tmplt_name, MARKER_RE)
  return general, params, tmplt

def bayesian_pickup(ary):
  return replicate_noise(ary, BAYESIAN_DEFAULTS, paretocorr_avg)
