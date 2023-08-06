# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from nose.tools import assert_almost_equal, eq_, assert_raises

import numpy as np
from numpy.testing import assert_allclose, assert_equal
import scipy.stats

from eelbrain import datasets
from eelbrain._stats import stats
from eelbrain._stats.permutation import permute_order


def test_confidence_interval():
    "Test confidence_interval()"
    from rpy2.robjects import r

    ds = datasets.get_loftus_masson_1994()
    y = ds['n_recalled'].x[:, None]
    x = ds['exposure'].as_factor()
    subject = ds['subject']
    ds.to_r('ds')

    # simple confidence interval of the mean
    ci = stats.confidence_interval(y)[0]
    r("s <- sd(ds$n_recalled)")
    r("n <- length(ds$n_recalled)")
    ci_r = r("qt(0.975, df=n-1) * s / sqrt(n)")[0]
    eq_(ci, ci_r)

    # pooled variance
    ci = stats.confidence_interval(y, x)[0]
    assert_almost_equal(ci, 3.85, delta=0.01)
    assert_raises(NotImplementedError, stats.confidence_interval, y[1:], x[1:])

    # within subject confidence interval
    ci = stats.confidence_interval(y, x, subject)[0]
    assert_almost_equal(ci, 0.52, 2)


def test_corr():
    "Test stats.corr"
    ds = datasets.get_uts()
    y = ds.eval("uts.x[:,:3]")
    x = ds.eval('Y.x')
    n_cases = len(y)
    df = n_cases - 2

    corr = stats.corr(y, x)
    p = stats.rtest_p(corr, df)
    for i in xrange(len(corr)):
        r_sp, p_sp = scipy.stats.pearsonr(y[:, i], x)
        assert_almost_equal(corr[i], r_sp)
        assert_almost_equal(p[i], p_sp)

    # NaN
    r = stats.corr(np.arange(10), np.zeros(10))
    eq_(r, 0)

    # perm
    y_perm = np.empty_like(y)
    for perm in permute_order(n_cases, 2):
        y_perm[perm] = y
        stats.corr(y, x, corr, perm)
        for i in xrange(len(corr)):
            r_sp, _ = scipy.stats.pearsonr(y_perm[:, i], x)
            assert_almost_equal(corr[i], r_sp)


def test_lm():
    "Test linear model function against scipy lstsq"
    ds = datasets.get_uts(True)
    uts = ds['uts']
    utsnd = ds['utsnd']
    x = ds.eval("A*B")
    n = ds.n_cases

    # 1d betas
    betas = stats.betas(uts.x, x)
    sp_betas = scipy.linalg.lstsq(x.full, uts.x.reshape((n, -1)))[0]
    # sp_betas = sp_betas.reshape((x.df,) + uts.shape[1:])
    assert_allclose(betas, sp_betas)

    # 2d betas
    betas = stats.betas(utsnd.x, x)
    sp_betas = scipy.linalg.lstsq(x.full, utsnd.x.reshape((n, -1)))[0]
    sp_betas = sp_betas.reshape((x.df,) + utsnd.shape[1:])
    assert_allclose(betas, sp_betas)


def test_sem_and_variability():
    "Test variability() and standard_error_of_the_mean() functions"
    ds = datasets.get_loftus_masson_1994()
    y = ds['n_recalled'].x
    x = ds['exposure'].as_factor()
    match = ds['subject']

    # invalid spec
    assert_raises(ValueError, stats.variability, y, 0, 0, '1mile', 0)
    assert_raises(ValueError, stats.variability, y, 0, 0, 'ci7ci', 0)

    # standard error
    target = scipy.stats.sem(y, 0, 1)
    e = stats.variability(y, None, None, 'sem', False)
    assert_almost_equal(e, target)
    e = stats.variability(y, None, None, '2sem', False)
    assert_almost_equal(e, 2 * target)

    target = np.array([scipy.stats.sem(y[x == cell], 0, 1) for cell in x.cells])
    es = stats.variability(y, x, None, 'sem', False)
    assert_allclose(es, target)

    stats.variability(y, x, None, 'sem', True)

    # confidence intervals
    stats.variability(y, None, None, '95%ci', False)
    stats.variability(y, x, None, '95%ci', True)
    stats.variability(y, x, match, '95%ci', True)


def test_t_1samp():
    "Test 1-sample t-test"
    ds = datasets.get_uts(True)

    y = ds['uts'].x
    t = scipy.stats.ttest_1samp(y, 0, 0)[0]
    assert_allclose(stats.t_1samp(y), t, 10)

    y = ds['utsnd'].x
    t = scipy.stats.ttest_1samp(y, 0, 0)[0]
    assert_allclose(stats.t_1samp(y), t, 10)


def test_t_ind():
    "Test independent samples t-test"
    ds = datasets.get_uts(True)
    y = ds.eval("utsnd.x")
    n_cases = len(y)
    n = n_cases / 2

    t = stats.t_ind(y, n, n)
    p = stats.ttest_p(t, n_cases - 2)
    t_sp, p_sp = scipy.stats.ttest_ind(y[:n], y[n:])
    assert_equal(t, t_sp)
    assert_equal(p, p_sp)
    assert_allclose(stats.ttest_t(p, n_cases - 2), np.abs(t))

    # permutation
    y_perm = np.empty_like(y)
    for perm in permute_order(n_cases, 2):
        stats.t_ind(y, n, n, out=t, perm=perm)
        y_perm[perm] = y
        t_sp, _ = scipy.stats.ttest_ind(y_perm[:n], y_perm[n:])
        assert_allclose(t, t_sp)
