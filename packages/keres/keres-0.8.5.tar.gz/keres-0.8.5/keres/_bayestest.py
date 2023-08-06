#! /usr/bin/env python

"""
This is the testing module for the recursive Bayesian algorithm.

It uses copasi to create the simulations.
"""

import os
import sys
from optparse import OptionParser
import Tkinter as Tk
from ScrolledText import ScrolledText
import tkMessageBox
import math
import logging
import time
import pickle
import copy
import bz2

import numpy
from numpy import polyfit

if sys.platform == 'darwin':
  _h = "/Library/Frameworks/R.framework/Versions/Current/Resources/"
  os.environ['R_HOME'] = _h
import rpy2.robjects as robjects

import _keres

import pygmyplot

DEBUG = True

DEFAULTS = dict(
  #####################################################################
  # empirical constants of the algorithm
  #####################################################################
  # the following values cap our certainty about events in the world
  # they are mostly empirical, but qualitatively make sense
  # all values are log base 10 and are hard coded to save cpus
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

def header(width=70):
  hline = "=" * width
  print hline
  print "bayestest".center(width)
  print hline

def usage(parser, msg=None, width=70, master=None):
  err = ' ERROR '.center(width, '#')
  errbar = '#' * width
  hline = '=' * width
  if msg is not None:
     print '\n'.join(('', err, msg, errbar, ''))
  print hline
  print
  print parser.format_help()
  if master is not None:
    master.destroy()
  sys.exit(0)

def noise_progress(p):
  if p.index is not None:
    noise = p.context.settings['noise_increment'] * (p.index + 1)
    args = (noise, p.m, p.steps)
    tmplt = "Doing Noise Level %s. Step %s of %s is Done."
    msg = tmplt % args
  else:
    noise = p.context.settings['noise_increment'] * p.steps
    args = (noise, p.steps, p.steps)
    tmplt = "Done with Noise Level %s. Step %s of %s is Done."
    msg = tmplt % args
  logging.info(msg)
  p.context.status['text'] = msg

def scaling_progress(p):
  if p.index is not None:
    pct = p.frac * 100
    args = (p.m, p.steps, pct)
    tmplt = "Done scaling step %s of %s. | %6.2f%% Overall."
    msg = tmplt % args
  else:
    pct = p.end * 100
    args = (p.steps, p.steps, pct)
    tmplt = "Done scaling step %s of %s. | %6.2f%% Overall."
    msg = tmplt % args
  logging.debug(msg)
  p.context.subprog['text'] = msg

def doopts():
  usage = 'usage: bayestet configfile'
  parser = OptionParser(usage)
  return parser

def write_acr(results, filename):
  open(filename, "wb").write(bz2.compress(pickle.dumps(results)))

def docalcs(master):
  run_time = time.time()
  header()
  parser = doopts()
  (options, args) = parser.parse_args()
  try:
    cfg_file = args[0]
  except IndexError:
    usage(parser, msg='No configfile specified.',
                  master=master)
  general, params, tmplt = _keres.setup(cfg_file)
  configuration = {'general' : copy.deepcopy(general),
                   'copasi params' : copy.deepcopy(params),
                   'copasi template' : tmplt
                  }

  
  master.settings = general
  corr_func_name = general.get("corr_func", "paretocorr_avg")
  master.info['text'] = 'BayesTest - %s' % corr_func_name
  logger = logging.getLogger()
  if general['debugging']:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)
    robjects.r("options(warn=-1)")
  defaults = DEFAULTS.copy()
  def identity(values, history):
    return 0
  corr_funcs = { None : None,
                 'None' : None,
                 'paretocorr' : _keres.paretocorr,
                 'paretocorr_avg' : _keres.paretocorr_avg,
                 'try_corr' : _keres.try_corr
               }
  corr_func = corr_funcs[corr_func_name]
  def bayesian_pickup(ary):
    return _keres.replicate_noise(ary, defaults, corr_func)
  algorithms = [_keres.algorithm_10, _keres.algorithm_50,
                bayesian_pickup]

  if general['biphasic']:
    simulator = _keres.run_copasi_biphasic
    master.info['text'] = master.info['text'] + ' - biphasic'
  else:
    simulator = _keres.run_copasi

  ### loop over noise
  ### every time in loop
  ###  100/num_noises ==> fractional increments
  max_noise = general['max_noise']
  increment = general['noise_increment']
  num_noises = int(round(max_noise / increment))
  report_n = general['report_n']
  report_every = _keres.do_every(report_n, num_noises)
  noiselist = []
  pvarlist = []
  pvar1050list = []
  pavgdifflist = []
  variationlist = []
  ksnormlist = []
  # devlist = []

  # aggregate list of all the ks exp on noisey
  kslist = []

  # probably RETURN
  ksreallist = []
  # RETURN
  real_times_list = []
  # RETURN
  real10list = []
  # RETRUN
  real50list = []

  # RETURN - normalized by p_real
  ksexp10 = []
  # RETURN - normalized by p_real
  ksexp50 = []
  # RETURN - normalized by p_real
  ksexpbayes = []

  devlist = []

  # RETURN (but want to tweak calc_early_sig())
  #           result from calc_early_sig()
  #           (approx val @ hard cutoff / std of noise)
  meansig = []
  # adding to get spread of times
  spreadlist = []
  real_spread = []

  # false negatives by ks test exp
  # false_negatives = []

  lag_times = []

  p = _keres.Progressor(slice(num_noises), noise_progress,
                       context=master)
  for i in p:
    general['stoch_noise'] = (i + 1) * increment
    subp = p.subprogress(slice(general['scaling_n']), scaling_progress)
    rslt = _keres.lag_time_loop_det_ksed(general, params, tmplt,
                                        algorithms, simulator,
                                        progressor=subp)
    (signoises, real_times, stoch_times,
     history, variance, mean, real10, real50, stddev) = rslt
    # stoch_times shape should be
    #          (number of algos, scaling_n, stochastic_n)
    lag_times.append(stoch_times)
    subp.finish()

    # mean is currently returning a new sig - noise calculation
    # for testing (from calc_early_sig())
    real_times_list.append(real_times)
    real10list.append(real10)
    real50list.append(real50)
    meansig.append(mean)
    p_exps = _keres.apply_ks(stoch_times, _keres.ks_test_r_exp)
    p_norms = _keres.apply_ks(stoch_times, _keres.ks_test_r_norm)
    p_reals = _keres.apply_ks_real(real_times, _keres.ks_test_r_exp)

    ksexp10.append(p_exps[0]/p_reals)
    ksexp50.append(p_exps[1]/p_reals)
    ksexpbayes.append(p_exps[2]/p_reals)

    # ks_cutoff = general.get("ks_cutoff", 0.05)
    # negatives = _keres.false_negative_rate(stoch_times,
    #                                       _keres.ks_test_r_exp,
    #                                       ks_cutoff)
    # false_negatives.append(negatives)

    p_vars = _keres.norm_test_var(real_times, stoch_times)
    p_var1050 = _keres.norm_test_var1050(real_times, stoch_times,
                                        real10, real50)
    p_diff = _keres.find_avg_diff(real_times, stoch_times)
    spread = _keres.find_spread_times(stoch_times)
    spreadlist.append(spread)
    real_spread.append(numpy.std(real_times))

    kslist.append(p_exps)
    ksreallist.append(p_reals)
    pvarlist.append(p_vars)
    pvar1050list.append(p_var1050)
    ksnormlist.append(p_norms)
    pavgdifflist.append(p_diff)
    variationlist.append(variance)
    noiselist.append(general['stoch_noise'])
    devlist.append(stddev)
    if ((report_every is not None) and
        (i % report_every == 0)):
      hline = "="*55
      ip = master.info_pane
      ip.insert(Tk.END, "\n\n" + hline + "\n")
      ip.insert(Tk.END, " Noise: %s" % general['stoch_noise'] + "\n")
      times = stoch_times.mean(axis=2)
      rt_2d = real_times.reshape((real_times.size, 1))
      bayes_difs = times[2] - real_times.astype(numpy.int)
      difs_2d = bayes_difs.reshape((bayes_difs.size, 1))
      ary4col = numpy.hstack((rt_2d, times.transpose(), difs_2d))
      ary4avg = ary4col.mean(axis=0)
      heading_names = ("real", "tenth", "half", "bayes", "diff")
      headings = " " + "%6s" * 5 % heading_names
      ip.insert(Tk.END, hline + "\n")
      ip.insert(Tk.END, headings + "\n")
      ip.insert(Tk.END, hline + "\n")
      for arow in ary4col.astype(numpy.int):
         ttt = (" " + "%6d" * arow.size) % tuple(arow)
         ip.insert(Tk.END, ttt + '\n')
      ip.insert(Tk.END, hline + "\n")
      arow = ary4avg.astype(numpy.int)
      ttt = (" " + "%6d" * arow.size) % tuple(arow)
      ip.insert(Tk.END, ttt + '\n')

      algorithm_names = "10% 50% Bayesian".split()
      ip.insert(Tk.END, '\n' + hline + '\n')
      atup = (general['scaling_n'], general['stochastic_n'])
      ttt = "   Scaling N: %s,  Stocastic n: %s" % atup
      ip.insert(Tk.END, ttt + '\n')
      atup = (general['timepoints'], general['stoch_noise'])
      ttt = "   Length: %s,  Noise: %s" % atup
      ip.insert(Tk.END, ttt + '\n' + hline + '\n')
      ttt = "|".join("%12s" % s for s in algorithm_names)
      ip.insert(Tk.END, ttt + '\n' + hline + '\n')
      # ks for exponential distribution
      fs_p_exps = "|".join([("%12.8f" % float(_p)) for _p in p_exps])
      # ks for normal distribution
      # fs_p_norms = [("%12.2f" % float(p)) for p in p_norms]
      # variances compared to appropriate times (e.g. tenth to tenth, etc.)
      report_vars = numpy.append(p_var1050[:2], p_vars[2])
      fs_vars = "|".join([("%12.6f" % float(_v)) for _v in report_vars])
      ip.insert(Tk.END, fs_p_exps + " | KS p(Exponential)\n")
      ip.insert(Tk.END, fs_vars + " | MSD\n")
      logging.debug(fs_p_exps + " | KS P(Exponential)\n")
      logging.debug(fs_vars + " | MSD\n")
      ip.insert(Tk.END, hline + '\n\n')
  
  noise_array = numpy.array(noiselist)
  lag_times = numpy.array(lag_times).swapaxes(0, 1)
  algos = [_f.__name__ for _f in algorithms]

  real10_array = numpy.array(real10list)
  real50_array = numpy.array(real50list)
  real_times_array = numpy.array([real10_array,
                                  real50_array,
                                  real_times_list])
  pavgarray = numpy.array(pavgdifflist)
  pvararray = numpy.array(pvarlist)
  pvar1050array = numpy.array(pvar1050list)
  ksnormarray = numpy.array(ksnormlist)
  ksarray = numpy.array(kslist).transpose()
  ksrealarray = numpy.array(ksreallist)
  spreadarray = numpy.array(spreadlist)
  # false_negatives = numpy.array(false_negatives).transpose()

  mean_sq_diffs = numpy.array([ pvar1050array[:, 0],
                                pvar1050array[:, 1],
                                pvararray[:, 2]
                              ])

  # returning signoises for testing purposes, will work only
  to_dump = {'run time' : time.ctime(run_time),
             'results name' : general['acr_name'],
             'configuration' : configuration,
             'noise levels' : noise_array,
             'real times' : real_times_array,
             'lag times' : lag_times,
             'algorithms' : algos,
             'real ks-exp' : ksrealarray,
             'algorithmic ks-exp' : ksarray,
             'mean square differences' : mean_sq_diffs,
             'lag times dimensions' :
                ("algorithms", "noises", "scaling_n", "stochastic_n")}

  # within 1 noise level, same for avg diff here
  logging.info("=" * 60)
  logging.info(" Some Results from BayesTest")
  logging.info("=" * 60)
  logging.info("signoise calc new")
  logging.info(signoises)
  logging.info("avg diffs new")
  v_norms = stoch_times - real_times.reshape((real_times.size, 1))
  bayes_v_norms = numpy.array(v_norms[:,2])
  bayes_v_norms = bayes_v_norms.flatten()
  logging.info(bayes_v_norms.tolist())
  logging.info("calculated noise")
  logging.info(repr(variationlist))
  logging.info("real time ks results")
  logging.info(ksrealarray)
  logging.info("avg diff for 10%")
  logging.info(pavgarray[:,0])
  logging.info("variances compared to 10% run on noiseless data")
  logging.info(repr(pvar1050array[:, 0]))
  logging.info("kstest exponential for 10%")
  logging.info(repr(ksarray[0]))
  logging.info("normalized ks exps for 10%")
  logging.info(ksexp10)
  logging.info("kstest normal for 10%")
  logging.info(ksnormarray[:,0])
  logging.info("spread for 10%")
  logging.info(spreadarray[:,0])
  logging.info("avg diff for 50%")
  logging.info(pavgarray[:,1])
  # logging.info("variation for 50%")
  # logging.info(pvararray[:,1])
  logging.info("variances compared to 50% run on noiseless data")
  logging.info(repr(pvar1050array[:, 1]))
  logging.info("kstest exp for 50%")
  logging.info(repr(ksarray[1]))
  logging.info("normalized ks exp for 50%")
  logging.info(ksexp50)
  logging.info("kstest normal for 50%")
  logging.info(ksnormarray[:,1])
  logging.info("spreads for 50%")
  logging.info(spreadarray[:,1])
  logging.info("avg diff for Bayesian")
  pnewavg = pavgarray[:,2]
  pnewavg.flatten()
  logging.info(pnewavg.tolist())
  # logging.info(pavgarray[:,2])
  logging.info("variances for Bayesian")
  logging.info(repr(pvararray[:,2]))
  logging.info("variances for bayesian using other func")
  logging.info(repr(pvar1050array[:, 2]))
  logging.info("kstest exp for Bayesian")
  logging.info(repr(ksarray[2]))
  logging.info("normalized ks exp for Bayesian")
  logging.info(ksexpbayes)
  logging.info("kstest normal for Bayesian")
  logging.info(ksnormarray[:,2])
  logging.info("dev list")
  logging.info(devlist)
  logging.info("spreads for Bayesian")
  logging.info(spreadarray[:,2])
  logging.info("spreads of real times")
  logging.info(real_spread)
  logging.info("noise")
  logging.info(noiselist)
  logging.info("new calculation for bayesian correction")
  logging.info(meansig)
  # chart a record of the noise levels
  # plot = pygmyplot.MyXYPlot(title)
  # plot.plot(noiselist, pvararray[:,2])
  # log false negatives
  # logging.info("*False Negative Rates")
  # for i, algo in enumerate(['10', '50', 'bayes']):
  #   logging.info("algorithm: %s" % algo
  #   logging.info(repr(false_negatives[i])
  master.status['text'] = "Compressing results and writing file."
  master.subprog['text'] = "This may take a minute or two..."
  results_name = str(run_time) + "." + general['acr_name']
  write_acr(to_dump, results_name)
  msg = "Results saved to '%s'." % results_name
  logging.info(msg)
  master.status['text'] = msg
  master.subprog['text'] = "All Done."

# unused: not dependable because tkinter is not thread safe
def make_stopper(master):
  def _quit(master=master):
    stop = True
    if hasattr(master, "threads"):
      for t in master.threads:
        if t.is_alive():
          if not tkMessageBox.askyesno("Running Calculations",
                   "Calculations are still running. Quit anyway?"):
            stop = False
          break
    if stop:
      sys.exit(0)
  return _quit

def _bayestest():
  logging.basicConfig(level=logging.INFO,
                      stream=sys.stdout)
  logging.basicConfig(level=logging.DEBUG,
                      stream=sys.stdout)
  logging.root.level = 30
  tk = Tk.Tk()
  tk.title('BayesTest')
  stopper = make_stopper(tk)
  tk.protocol("WM_DELETE_WINDOW", stopper)
  tk.info = Tk.Label(tk, text="BayesTest Main Window")
  tk.info.pack(expand=Tk.NO, fill=Tk.BOTH)
  time.sleep(0.1)
  ip = ScrolledText(tk, relief=Tk.SUNKEN, border=2)
  ip.pack(expand=Tk.YES, fill=Tk.BOTH)
  tk.info_pane = ip
  tk.status = Tk.Label(tk, text="...")
  tk.status.pack(expand=Tk.NO, fill=Tk.BOTH)
  tk.subprog = Tk.Label(tk, text="")
  tk.subprog.pack(expand=Tk.NO, fill=Tk.BOTH)
  Tk.Button(tk, text="Quit", command=stopper).pack()
  docalcs(tk)
  tk.tkraise()
  tk.update_idletasks()
  tk.mainloop()

if __name__ == "__main__":
  bayestest()
