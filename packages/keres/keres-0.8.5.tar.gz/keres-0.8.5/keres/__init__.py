#! /usr/bin/env python

'''
keres: A Bayes filter and test suite for amyloid fluorimetry data
Copyright (c) 2014, James C. Stroud; All rights reserved.
'''

import _keres
import _bayestest

from _version import __version__

__all__ = ["BAYESIAN_DEFAULTS", "Progressor", "pareto",
           "bayesian_pickup", "algorithm_50", "algorithm_10",
           "ks_test_r_exp", "ks_test_r_norm", "take_n", "bump"]

BAYESIAN_DEFAULTS = _keres.BAYESIAN_DEFAULTS
Progressor = _keres.Progressor
bayesian_pickup = _keres.bayesian_pickup
algorithm_50 = _keres.algorithm_50
algorithm_10 = _keres.algorithm_10
ks_test_r_exp = _keres.ks_test_r_exp
ks_test_r_norm = _keres.ks_test_r_norm
pareto = _keres.paretocorr_avg

# array operations
take_n = _keres.take_n
bump = _keres.bump
