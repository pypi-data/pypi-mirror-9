# -*- coding: utf-8 -*-
from __future__ import print_function
from itertools import combinations

import numpy as np
from scipy import stats
import pandas as pd

from lifelines.utils import group_survival_table_from_events


def logrank_test(event_times_A, event_times_B, event_observed_A=None, event_observed_B=None,
                 alpha=0.95, t_0=-1, suppress_print=False, **kwargs):
    """
    Measures and reports on whether two intensity processes are different. That is, given two
    event series, determines whether the data generating processes are statistically different.
    The test-statistic is chi-squared under the null hypothesis.

    H_0: both event series are from the same generating processes
    H_A: the event series are from different generating processes.

    Pre lifelines 0.2.x: this returned a test statistic.
    Post lifelines 0.2.x: this returns the results of the entire test.

    See Survival and Event Analysis, page 108. This implicitly uses the log-rank weights. The R language
    equivilant in the `survival` package would use conf.type='log-log'.

    Parameters:
      event_times_foo: a (nx1) array of event durations (birth to death,...) for the population.
      censorship_bar: a (nx1) array of censorship flags, 1 if observed, 0 if not. Default assumes all observed.
      t_0: the period under observation, -1 for all time.
      alpha: the level of signifiance
      suppress_print: if True, do not print the summary. Default False.
      kwargs: add keywords and meta-data to the experiment summary

    Returns
      summary: a print-friendly string detailing the results of the test.
      p: the p-value
      test result: True if reject the null, (pendantically None if inconclusive)
    """

    event_times_A, event_times_B = np.array(event_times_A), np.array(event_times_B)
    if event_observed_A is None:
        event_observed_A = np.ones(event_times_A.shape[0])
    if event_observed_B is None:
        event_observed_B = np.ones(event_times_B.shape[0])

    event_times = np.r_[event_times_A, event_times_B]
    groups = np.r_[np.zeros(event_times_A.shape[0]), np.ones(event_times_B.shape[0])]
    event_observed = np.r_[event_observed_A, event_observed_B]
    return multivariate_logrank_test(event_times, groups, event_observed,
                                     alpha=alpha, t_0=t_0, suppress_print=suppress_print, **kwargs)


def pairwise_logrank_test(event_durations, groups, event_observed=None,
                          alpha=0.95, t_0=-1, bonferroni=True, suppress_print=False, **kwargs):
    """
    Perform the logrank test pairwise for all n>2 unique groups (use the more appropriate logrank_test for n=2).
    We have to be careful here: if there are n groups, then there are n*(n-1)/2 pairs -- so many pairs increase
    the chance that here will exist a significantly different pair purely by chance. For this reason, we use the
    Bonferroni correction (rewight the alpha value higher to accomidate the multiple tests).


    Parameters:
      event_durations: a (n,) numpy array the (partial) lifetimes of all individuals
      groups: a (n,) numpy array of unique group labels for each individual.
      event_observed: a (n,) numpy array of event_observed events: 1 if observed death, 0 if censored. Defaults
          to all observed.
      alpha: the level of signifiance desired.
      t_0: the final time to compare the series' up to. Defaults to all.
      bonferroni: If true, uses the Bonferroni correction to compare the M=n(n-1)/2 pairs, i.e alpha = alpha/M
            See (here)[http://en.wikipedia.org/wiki/Bonferroni_correction].
      suppress_print: if True, do not print the summary. Default False.
      kwargs: add keywords and meta-data to the experiment summary.

    Returns:
      S: a (n,n) dataframe of print-friendly test summaries (np.nan on the diagonal). Ex:
      P: a (n,n) dataframe of p-values (np.nan on the diagonal).
      T: a (n,n) dataframe of test results (True is significant, None if not) (np.nan on the diagonal).

    Example:
      P:
                a         b         c
      a       NaN  0.711136  0.401462
      b  0.711136       NaN  0.734605
      c  0.401462  0.734605       NaN

      T:
            a     b     c
      a   NaN  None  None
      b  None   NaN  None
      c  None  None   NaN

    """

    if event_observed is None:
        event_observed = np.ones((event_durations.shape[0], 1))

    n = max(event_durations.shape)
    assert n == max(event_durations.shape) == max(event_observed.shape), "inputs must be of the same length."
    groups, event_durations, event_observed = map(lambda x: pd.Series(np.reshape(x, (n,))), [groups, event_durations, event_observed])

    unique_groups = np.unique(groups)

    n = unique_groups.shape[0]

    if bonferroni:
        m = 0.5 * n * (n - 1)
        alpha = 1 - (1 - alpha) / m

    P = np.zeros((n, n), dtype=float)
    T = np.empty((n, n), dtype=object)
    S = np.empty((n, n), dtype=object)

    np.fill_diagonal(P, np.nan)
    np.fill_diagonal(T, np.nan)
    np.fill_diagonal(S, np.nan)

    for i1, i2 in combinations(np.arange(n), 2):
        g1, g2 = unique_groups[[i1, i2]]
        ix1, ix2 = (groups == g1), (groups == g2)
        test_name = str(g1) + " vs. " + str(g2)
        summary, p_value, result = logrank_test(event_durations.ix[ix1], event_durations.ix[ix2],
                                                event_observed.ix[ix1], event_observed.ix[ix2],
                                                alpha=alpha, t_0=t_0, use_bonferroni=bonferroni,
                                                test_name=test_name, suppress_print=suppress_print,
                                                **kwargs)
        T[i1, i2], T[i2, i1] = result, result
        P[i1, i2], P[i2, i1] = p_value, p_value
        S[i1, i2], S[i2, i1] = summary, summary

    return [pd.DataFrame(x, columns=unique_groups, index=unique_groups) for x in [S, P, T]]


def multivariate_logrank_test(event_durations, groups, event_observed=None,
                              alpha=0.95, t_0=-1, suppress_print=False, **kwargs):
    """
    This test is a generalization of the logrank_test: it can deal with n>2 populations (and should
      be equal when n=2):

    H_0: all event series are from the same generating processes
    H_A: there exist atleast one group that differs from the other.

    Parameters:
      event_durations: a (n,) numpy array the (partial) lifetimes of all individuals
      groups: a (n,) numpy array of unique group labels for each individual.
      event_observed: a (n,) numpy array of event observations: 1 if observed death, 0 if censored. Defaults
          to all observed.
      alpha: the level of significance desired.
      t_0: the final time to compare the series' up to. Defaults to all.
      suppress_print: if True, do not print the summary. Default False.
      kwargs: add keywords and meta-data to the experiment summary.

    Returns:
      summary: a print-friendly summary of the statistical test
      p_value: the p-value
      test_result: True if reject the null, (pendantically) None if we can't reject the null.

    """
    if event_observed is None:
        event_observed = np.ones((event_durations.shape[0], 1))

    n = max(event_durations.shape)
    assert n == max(event_durations.shape) == max(event_observed.shape), "inputs must be of the same length."
    groups, event_durations, event_observed = map(lambda x: pd.Series(np.reshape(x, (n,))), [groups, event_durations, event_observed])

    unique_groups, rm, obs, _ = group_survival_table_from_events(groups, event_durations, event_observed, np.zeros_like(event_durations), t_0)
    n_groups = unique_groups.shape[0]

    # compute the factors needed
    N_j = obs.sum(0).values
    n_ij = (rm.sum(0).values - rm.cumsum(0).shift(1).fillna(0))
    d_i = obs.sum(1)
    n_i = rm.values.sum() - rm.sum(1).cumsum().shift(1).fillna(0)
    ev = n_ij.mul(d_i / n_i, axis='index').sum(0)

    # vector of observed minus expected
    Z_j = N_j - ev

    assert abs(Z_j.sum()) < 10e-8, "Sum is not zero."  # this should move to a test eventually.

    # compute covariance matrix
    V_ = n_ij.mul(np.sqrt(d_i) / n_i, axis='index').fillna(1)
    V = -np.dot(V_.T, V_)
    ix = np.arange(n_groups)
    V[ix, ix] = V[ix, ix] + ev

    # take the first n-1 groups
    U = Z_j.ix[:-1].dot(np.linalg.pinv(V[:-1, :-1]).dot(Z_j.ix[:-1]))  # Z.T*inv(V)*Z

    # compute the p-values and tests
    test_result, p_value = chisq_test(U, n_groups - 1, alpha)
    summary = pretty_print_summary(test_result, p_value, U, t_0=t_0, test='logrank',
                                   alpha=alpha, null_distribution='chi squared',
                                   df=n_groups - 1, **kwargs)

    if not suppress_print:
        print(summary)
    return summary, p_value, test_result


def chisq_test(U, degrees_freedom, alpha):
    p_value = stats.chi2.sf(U, degrees_freedom)
    if p_value < 1 - alpha:
        return True, p_value
    else:
        return None, p_value


def two_sided_z_test(Z, alpha):
    p_value = 1 - max(stats.norm.cdf(Z), 1 - stats.norm.cdf(Z))
    if p_value < 1 - alpha / 2.:
        return True, p_value
    else:
        return False, p_value


def pretty_print_summary(test_results, p_value, test_statistic, **kwargs):
    """
    kwargs are experiment meta-data.
    """
    HEADER = "   __ p-value ___|__ test statistic __|__ test results __"
    s = "Results\n"
    meta_data = pretty_print_meta_data(kwargs)
    s += meta_data + "\n"
    s += HEADER + "\n"
    s += "         %.5f |              %.3f |     %s   " % (p_value, test_statistic, test_results)
    return s


def pretty_print_meta_data(dictionary):
    s = ""
    for k, v in dictionary.items():
        s = s + "   " + k.__str__().replace('_', ' ') + ": " + v.__str__() + "\n"
    return s
