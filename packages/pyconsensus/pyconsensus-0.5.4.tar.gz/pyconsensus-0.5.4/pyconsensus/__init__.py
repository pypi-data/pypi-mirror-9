#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Consensus mechanism for Augur/Truthcoin.

pyconsensus is a Python implementation of the Augur/Truthcoin consensus
mechanism, described in detail at https://github.com/psztorc/Truthcoin.

Usage:

    from pyconsensus import Oracle

    # Example report matrix:
    #   - each row represents a reporter
    #   - each column represents an event in a prediction market
    my_reports = [[0.2, 0.7, -1, -1],
                  [0.3, 0.5, -1, -1],
                  [0.1, 0.7, -1, -1],
                  [0.5, 0.7,  1, -1],
                  [0.1, 0.2,  1,  1],
                  [0.1, 0.2,  1,  1]]
    my_event_bounds = [
        {"scaled": True, "min": 0.1, "max": 0.5},
        {"scaled": True, "min": 0.2, "max": 0.7},
        {"scaled": False, "min": -1, "max": 1},
        {"scaled": False, "min": -1, "max": 1},
    ]

    oracle = Oracle(reports=my_reports, event_bounds=my_event_bounds)
    oracle.consensus()

"""
from __future__ import division, absolute_import
import sys
import os
import getopt
import json
import warnings
from pprint import pprint
from copy import deepcopy
import numpy as np
import pandas as pd
from weightedstats import weighted_median
from six.moves import xrange as range

__title__      = "pyconsensus"
__version__    = "0.5.4"
__author__     = "Jack Peterson and Paul Sztorc"
__license__    = "GPL"
__maintainer__ = "Jack Peterson"
__email__      = "jack@tinybike.net"

pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
np.set_printoptions(linewidth=225,
                    suppress=True,
                    formatter={"float": "{: 0.6f}".format})

class Oracle(object):

    def __init__(self, reports=None, event_bounds=None, reputation=None,
                 catch_tolerance=0.1, alpha=0.1, beta=0.5, verbose=False,
                 aux=None, algorithm="fixed-variance", variance_threshold=0.9):
        """
        Args:
          reports (list-of-lists): reports matrix; rows = reporters, columns = Events.
          event_bounds (list): list of dicts for each Event
            {
              scaled (bool): True if scalar, False if binary (boolean)
              min (float): minimum allowed value (-1 if binary)
              max (float): maximum allowed value (1 if binary)
            }

        """
        self.reports = np.ma.masked_array(reports, np.isnan(reports))
        self.num_reporters = len(reports)
        self.num_events = len(reports[0])
        self.event_bounds = event_bounds
        self.catch_tolerance = catch_tolerance
        self.alpha = alpha  # reputation smoothing parameter
        self.beta = beta    # variance weight (for mixed algorithms)
        self.verbose = verbose
        self.algorithm = algorithm
        self.variance_threshold = variance_threshold
        self.num_components = -1
        self.convergence = False
        self.aux = aux
        if reputation is None:
            self.weighted = False
            self.total_rep = self.num_reporters
            self.reptokens = np.ones(self.num_reporters).astype(int)
            self.reputation = np.array([1 / float(self.num_reporters)] * self.num_reporters)
        else:
            self.weighted = True
            self.total_rep = sum(np.array(reputation).ravel())
            self.reptokens = np.array(reputation).ravel().astype(int)
            self.reputation = np.array([i / float(self.total_rep) for i in reputation])

    def normalize(self, v):
        """Proportional distance from zero."""
        v = abs(v)
        if np.sum(v) == 0:
            v += 1
        return v / np.sum(v)

    def catch(self, X):
        """Forces continuous values into bins at -1, 0, and 1."""
        center = 0
        if X < center - self.catch_tolerance:
            return -1
        elif X > center + self.catch_tolerance:
            return 1
        else:
            return 0

    def interpolate(self, reports):
        """Uses existing data and reputations to fill missing observations.
        Weighted average/median using all available (non-nan) data.

        """
        # Rescale scaled events
        if self.event_bounds is not None:
            for i in range(self.num_events):
                if self.event_bounds[i]["scaled"]:
                    reports[:,i] = (reports[:,i] - self.event_bounds[i]["min"]) / float(self.event_bounds[i]["max"] - self.event_bounds[i]["min"])

        # Interpolation to fill the missing observations
        for j in range(self.num_events):
            if reports[:,j].mask.any():
                total_active_reputation = 0
                active_reputation = []
                active_reports = []
                nan_indices = []
                num_present = 0
                for i in range(self.num_reporters):
                    if reports[i,j] != np.nan:
                        total_active_reputation += self.reputation[i]
                        active_reputation.append(self.reputation[i])
                        active_reports.append(reports[i,j])
                        num_present += 1
                    else:
                        nan_indices.append(i)
                if not self.event_bounds[j]["scaled"]:
                    guess = 0
                    for i in range(num_present):
                        active_reputation[i] /= total_active_reputation
                        guess += active_reputation[i] * active_reports[i]
                    guess = self.catch(guess)
                else:
                    for i in range(num_present):
                        active_reputation[i] /= total_active_reputation
                    guess = weighted_median(active_reports, weights=active_reputation)
                for nan_index in nan_indices:
                    reports[nan_index,j] = guess
        return reports

    def weighted_pca(self, reports_filled):
        """Calculates new reputations using a weighted Principal Component
        Analysis (PCA).

        Weights are the number of coins people start with, so the aim of this
        weighting is to count 1 report for each of their coins -- e.g., guy with 10
        coins effectively gets 10 reports, guy with 1 coin gets 1 report, etc.
        
        The reports matrix has reporters as rows and events as columns.

        """
        first_loading = np.ma.masked_array(np.zeros(self.num_events))
        first_score = np.ma.masked_array(np.zeros(self.num_reporters))

        # Use the largest eigenvector only
        if self.algorithm == "sztorc":
            
            # Compute the weighted mean (of all reporters) for each event
            weighted_mean = np.ma.average(reports_filled,
                                          axis=0,
                                          weights=self.reputation.tolist())

            # Each report's difference from the mean of its event (column)
            mean_deviation = np.matrix(reports_filled - weighted_mean)

            # Compute the unbiased weighted population covariance
            # (for uniform weights, equal to np.cov(reports_filled.T, bias=1))
            covariance_matrix = np.ma.multiply(mean_deviation.T, self.reputation).dot(mean_deviation) / float(1 - np.sum(self.reputation**2))

            # H is the un-normalized eigenvector matrix
            H = np.linalg.svd(covariance_matrix)[0]

            # Normalize loading by Euclidean distance
            first_loading = np.ma.masked_array(H[:,0] / np.sqrt(np.sum(H[:,0]**2)))
            first_score = np.dot(mean_deviation, first_loading)

            nc = self.nonconformity(first_score, reports_filled)

        # Fixed-variance threshold: eigenvalue-weighted sum of score vectors
        elif self.algorithm == "fixed-variance":

            # Compute the weighted mean (of all reporters) for each event
            weighted_mean = np.ma.average(reports_filled,
                                          axis=0,
                                          weights=self.reputation.tolist())

            # Each report's difference from the mean of its event (column)
            mean_deviation = np.matrix(reports_filled - weighted_mean)

            # Compute the unbiased weighted population covariance
            # (for uniform weights, equal to np.cov(reports_filled.T, bias=1))
            covariance_matrix = np.ma.multiply(mean_deviation.T, self.reputation).dot(mean_deviation) / float(1 - np.sum(self.reputation**2))

            # H is the un-normalized eigenvector matrix
            H = np.linalg.svd(covariance_matrix)[0]

            # Normalize loading by Euclidean distance
            first_loading = np.ma.masked_array(H[:,0] / np.sqrt(np.sum(H[:,0]**2)))
            first_score = np.dot(mean_deviation, first_loading)

            U, Sigma, Vt = np.linalg.svd(covariance_matrix)
            variance_explained = np.cumsum(Sigma / np.trace(covariance_matrix))
            for i, var_exp in enumerate(variance_explained):
                loading = U.T[i]
                score = np.dot(mean_deviation, loading)
                if i == 0:
                    net_score = Sigma[i] * score
                else:
                    net_score += Sigma[i] * score
                if var_exp > self.variance_threshold: break
            self.num_components = i
            nc = self.nonconformity(net_score, reports_filled)            

        # Sztorc algorithm with normalized absolute inverse scores
        elif self.algorithm == "inverse-scores":

            # Compute the weighted mean (of all reporters) for each event
            weighted_mean = np.ma.average(reports_filled,
                                          axis=0,
                                          weights=self.reputation.tolist())

            # Each report's difference from the mean of its event (column)
            mean_deviation = np.matrix(reports_filled - weighted_mean)

            # Compute the unbiased weighted population covariance
            # (for uniform weights, equal to np.cov(reports_filled.T, bias=1))
            covariance_matrix = np.ma.multiply(mean_deviation.T, self.reputation).dot(mean_deviation) / float(1 - np.sum(self.reputation**2))

            # H is the un-normalized eigenvector matrix
            H = np.linalg.svd(covariance_matrix)[0]

            # Normalize loading by Euclidean distance
            first_loading = np.ma.masked_array(H[:,0] / np.sqrt(np.sum(H[:,0]**2)))
            first_score = np.dot(mean_deviation, first_loading)

            principal_components = np.linalg.svd(covariance_matrix)[0]
            first_loading = principal_components[:,0]
            first_loading = np.ma.masked_array(first_loading / np.sqrt(np.sum(first_loading**2)))
            first_score = np.dot(mean_deviation, first_loading)
            nc = 1 / np.abs(first_score)
            nc /= np.sum(nc)

        # Sum over all events in the ballot; the ratio of this sum to
        # the total covariance (over all events, across all reporters)
        # is each reporter's contribution to the overall variability.
        elif self.algorithm == "covariance":
            row_mean = np.mean(reports_filled, axis=1)
            centered = np.zeros(reports_filled.shape)
            onesvect = np.ones(self.num_events)
            for i in range(self.num_reporters):
                centered[i,:] = reports_filled[i,:] - onesvect * row_mean[i]
            # Unweighted: np.dot(centered, centered.T) / self.num_events
            covmat = np.dot(centered, np.ma.multiply(centered.T, self.reputation)) / float(1 - np.sum(self.reputation**2))
            # Sum across columns of the (other) covariance matrix
            contrib = np.sum(covmat, 1)
            relative_contrib = contrib / np.sum(contrib)
            nc = self.nonconformity(relative_contrib, reports_filled)

        # Sum over all events in the ballot; the ratio of this sum to
        # the total coskewness is that reporter's contribution.
        elif self.algorithm == "coskewness":
            if self.aux is not None and "coskew" in self.aux:
                nc = self.nonconformity(self.aux["coskew"], reports_filled)

        # Sum over all events in the ballot; the ratio of this sum to
        # the total cokurtosis is that reporter's contribution.
        elif self.algorithm == "cokurtosis" or self.algorithm == "cokurtosis-old":
            if self.aux is not None and "cokurt" in self.aux:
                nc = self.nonconformity(self.aux["cokurt"], reports_filled)

        # Mixed strategy: fixed-variance threshold + cokurtosis
        elif self.algorithm == "FVT+cokurtosis":
                        # Compute the weighted mean (of all reporters) for each event
            weighted_mean = np.ma.average(reports_filled,
                                          axis=0,
                                          weights=self.reputation.tolist())

            # Each report's difference from the mean of its event (column)
            mean_deviation = np.matrix(reports_filled - weighted_mean)

            # Compute the unbiased weighted population covariance
            # (for uniform weights, equal to np.cov(reports_filled.T, bias=1))
            covariance_matrix = np.ma.multiply(mean_deviation.T, self.reputation).dot(mean_deviation) / float(1 - np.sum(self.reputation**2))

            # H is the un-normalized eigenvector matrix
            H = np.linalg.svd(covariance_matrix)[0]

            # Normalize loading by Euclidean distance
            first_loading = np.ma.masked_array(H[:,0] / np.sqrt(np.sum(H[:,0]**2)))
            first_score = np.dot(mean_deviation, first_loading)

            U, Sigma, Vt = np.linalg.svd(covariance_matrix)
            variance_explained = np.cumsum(Sigma / np.trace(covariance_matrix))
            for i, var_exp in enumerate(variance_explained):
                loading = U.T[i]
                score = np.dot(mean_deviation, loading)
                if i == 0:
                    net_score = Sigma[i] * score
                else:
                    net_score += Sigma[i] * score
                if var_exp > self.variance_threshold: break
            self.num_components = i
            nc_FVT = self.nonconformity(net_score, reports_filled)
            if self.aux is not None and "cokurt" in self.aux:
                nc_cokurt = self.nonconformity(self.aux["cokurt"], reports_filled)
                nc = self.beta*nc_FVT + (1 - self.beta)*nc_cokurt

        # Use adjusted nonconformity scores to update Reputation fractions
        this_rep = self.normalize(
            nc * (self.reputation / np.mean(self.reputation)).T
        )
        return {
            "first_loading": first_loading,
            "old_rep": self.reputation.T,
            "this_rep": this_rep,
            "smooth_rep": self.alpha*this_rep + (1-self.alpha)*self.reputation.T,
        }

    def nonconformity(self, scores, reports):
        """Adjusted nonconformity scores for Reputation redistribution"""
        set1 = scores + np.abs(np.min(scores))
        set2 = scores - np.max(scores)
        old = np.dot(self.reputation.T, reports)
        new1 = np.dot(self.normalize(set1), reports)
        new2 = np.dot(self.normalize(set2), reports)
        ref_ind = np.sum((new1 - old)**2) - np.sum((new2 - old)**2)
        self.convergence = True
        nc = set1 if ref_ind <= 0 else set2
        return nc

    def consensus(self):
        # Handle missing values
        reports_filled = self.interpolate(self.reports)

        # Consensus - Row Players
        player_info = self.weighted_pca(reports_filled)

        # Column Players (The Event Creators)
        outcomes_raw = np.dot(player_info['smooth_rep'], reports_filled).squeeze()

        # Discriminate Based on Contract Type
        if self.event_bounds is not None:
            for i in range(reports_filled.shape[1]):

                # Our Current best-guess for this Scaled Event (weighted median)
                if self.event_bounds[i]["scaled"]:
                    outcomes_raw[i] = weighted_median(
                        reports_filled[:,i].data,
                        weights=player_info["smooth_rep"].ravel().data,
                    )

        # The Outcome (Discriminate Based on Contract Type)
        outcomes_adj = []
        for i, raw in enumerate(outcomes_raw):
            if self.event_bounds is not None and self.event_bounds[i]["scaled"]:
                outcomes_adj.append(raw)
            else:
                outcomes_adj.append(self.catch(raw))

        outcomes_final = []
        for i, raw in enumerate(outcomes_raw):
            outcomes_final.append(outcomes_adj[i])
            if self.event_bounds is not None and self.event_bounds[i]["scaled"]:
                outcomes_final[i] *= self.event_bounds[i]["max"] - self.event_bounds[i]["min"]
                outcomes_final[i] += self.event_bounds[i]["min"]

        certainty = []
        for i, adj in enumerate(outcomes_adj):
            certainty.append(sum(player_info["smooth_rep"][reports_filled[:,i] == adj]))

        certainty = np.array(certainty)
        consensus_reward = self.normalize(certainty)
        avg_certainty = np.mean(certainty)

        # Participation: information about missing values
        na_mat = self.reports * 0
        na_mat[na_mat.mask] = 1  # indicator matrix for missing

        # Participation Within Events (Columns)
        # % of reputation that answered each Event
        participation_columns = 1 - np.dot(player_info['smooth_rep'], na_mat)

        # Participation Within Agents (Rows)
        # Democracy Option - all Events treated equally.
        participation_rows = 1 - na_mat.sum(axis=1) / na_mat.shape[1]

        # General Participation
        percent_na = 1 - np.mean(participation_columns)

        # Possibly integrate two functions of participation? Chicken and egg problem...
        if self.verbose:
            print('*Participation Information*')
            print('Voter Turnout by question')
            print(participation_columns)
            print('Voter Turnout across questions')
            print(participation_rows)

        # Combine Information
        # Row
        na_bonus_reporters = self.normalize(participation_rows)
        reporter_bonus = na_bonus_reporters * percent_na + player_info['smooth_rep'] * (1 - percent_na)

        # Column
        na_bonus_events = self.normalize(participation_columns)
        author_bonus = na_bonus_events * percent_na + consensus_reward * (1 - percent_na)

        return {
            'original': self.reports.data,
            'filled': reports_filled.data,
            'agents': {
                'old_rep': player_info['old_rep'],
                'this_rep': player_info['this_rep'],
                'smooth_rep': player_info['smooth_rep'],
                'na_row': na_mat.sum(axis=1).data.tolist(),
                'participation_rows': participation_rows.data.tolist(),
                'relative_part': na_bonus_reporters.data.tolist(),
                'reporter_bonus': reporter_bonus.data.tolist(),
                },
            'events': {
                'adj_first_loadings': player_info['first_loading'].data.tolist(),
                'outcomes_raw': outcomes_raw.data.tolist(),
                'consensus_reward': consensus_reward,
                'certainty': certainty,
                'NAs Filled': na_mat.sum(axis=0).data.tolist(),
                'participation_columns': participation_columns.data.tolist(),
                'author_bonus': author_bonus.data.tolist(),
                'outcomes_adjusted': outcomes_adj,
                'outcomes_final': outcomes_final,
                },
            'participation': 1 - percent_na,
            'avg_certainty': avg_certainty,
            'convergence': self.convergence,
            'components': self.num_components,
        }

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        short_opts = 'hxms'
        long_opts = ['help', 'example', 'missing', 'scaled']
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            return 0
        elif opt in ('-x', '--example'):
            # # new: true=1, false=-1, indeterminate=0.5, no response=0
            reports = np.array([[  1,  1, -1, -1],
                                [  1, -1, -1, -1],
                                [  1,  1, -1, -1],
                                [  1,  1,  1, -1],
                                [ -1, -1,  1,  1],
                                [ -1, -1,  1,  1]])
            reputation = [2, 10, 4, 2, 7, 1]
            oracle = Oracle(reports=reports,
                            reputation=reputation,
                            algorithm="sztorc")
            # oracle = Oracle(reports=reports, run_ica=True)
            A = oracle.consensus()
            print(pd.DataFrame(A["events"]))
            print(pd.DataFrame(A["agents"]))
        elif opt in ('-m', '--missing'):
            # true=1, false=-1, indeterminate=0.5, no response=np.nan
            reports = np.array([[      1,  1, -1, np.nan],
                                [      1, -1, -1,     -1],
                                [      1,  1, -1,     -1],
                                [      1,  1,  1,     -1],
                                [ np.nan, -1,  1,      1],
                                [     -1, -1,  1,      1]])
            reputation = [2, 10, 4, 2, 7, 1]
            oracle = Oracle(reports=reports,
                            reputation=reputation,
                            algorithm="sztorc")
            A = oracle.consensus()
            print(pd.DataFrame(A["events"]))
            print(pd.DataFrame(A["agents"]))
        elif opt in ('-s', '--scaled'):
            reports = np.array([[ 1,  1, -1, -1, 233, 16027.59],
                                [ 1, -1, -1, -1, 199,   np.nan],
                                [ 1,  1, -1, -1, 233, 16027.59],
                                [ 1,  1,  1, -1, 250,   np.nan],
                                [-1, -1,  1,  1, 435,  8001.00],
                                [-1, -1,  1,  1, 435, 19999.00]])
            event_bounds = [
                { "scaled": False, "min": -1,   "max": 1 },
                { "scaled": False, "min": -1,   "max": 1 },
                { "scaled": False, "min": -1,   "max": 1 },
                { "scaled": False, "min": -1,   "max": 1 },
                { "scaled": True,  "min":  0,   "max": 435 },
                { "scaled": True,  "min": 8000, "max": 20000 },
            ]
            oracle = Oracle(reports=reports, event_bounds=event_bounds)
            A = oracle.consensus()
            print(pd.DataFrame(A["events"]))
            print(pd.DataFrame(A["agents"]))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
