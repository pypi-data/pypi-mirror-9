import numpy as np
import statsmodels.api as sm
import scipy.optimize
from pyhmc import hmc
from unittest.case import SkipTest

from msmbuilder.cluster import NDGrid
from msmbuilder.example_datasets import load_quadwell
from msmbuilder.msm import ContinuousTimeMSM, BayesianContinuousTimeMSM
from msmbuilder.msm._ratematrix import loglikelihood, ldirichlet_softmax
from msmbuilder.msm._ratematrix import lexponential
from msmbuilder.msm.bayes_ratematrix import _log_posterior


def test_1():
    try:
        from matplotlib import pyplot as pp
    except ImportError:
        raise SkipTest('Not making QQ plot')

    # check that ldirichlet_softmax_pdf is actually giving a dirichlet
    # distribution, by comparing a QQ plot with np.random.dirichlet
    alpha = np.array([1, 2, 3], dtype=float)

    def logprob(x, alpha):
        grad = np.zeros_like(x)
        logp = ldirichlet_softmax(x, alpha, grad=grad)
        return logp, grad
    samples, diag = hmc(logprob, x0=np.random.normal(size=(3,)), n_samples=1000,
                        args=(alpha,), n_steps=10, return_diagnostics=True)

    expx = np.exp(samples)
    pi1 = expx / np.sum(expx, 1, keepdims=True)
    pi2 = np.random.dirichlet(alpha=alpha, size=1000)

    sm.qqplot_2samples(pi1[:, 0], pi2[:, 0], line='45')
    pp.savefig('bayes_ratematrix-test-1.png')


def test_2():
    # check that the gradient of ldirichlet_softmax_pdf is correct
    alpha = np.array([1, 2, 3], dtype=float)

    def func(x):
        return ldirichlet_softmax(x, alpha)

    def grad(x):
        grad = np.zeros_like(x)
        ldirichlet_softmax(x, alpha, grad=grad)
        return grad

    n_trials = 100
    random = np.random.RandomState(0)
    x0 = random.randn(n_trials, 3)
    for i in range(n_trials):
        value = scipy.optimize.check_grad(func, grad, x0[i])
        assert value < 1e-6


def test_3():
    n = 4
    beta = np.array([1, 2, 3, 4], dtype=float)

    def func(x):
        return lexponential(x, beta)

    def grad(x):
        grad = np.zeros_like(x)
        lexponential(x, beta, grad=grad)
        return grad

    n_trials = 100
    random = np.random.RandomState(0)
    x0 = random.randn(n_trials, n)
    for i in range(n_trials):
        value = scipy.optimize.check_grad(func, grad, x0[i])
        assert value < 1e-6


def test_4():
    n = 4
    n_params = scipy.misc.comb(n+1, 2, exact=True)
    alpha = np.ones(n)
    beta = (np.arange(n_params - n) + 1).astype(np.float)
    counts = np.array([
        [10, 2, 0,  0],
        [1,  8, 2,  0],
        [0,  4, 10, 1],
        [0,  0, 2,  8]
    ]).astype(float)

    def log_posterior(theta):
        return _log_posterior(theta, counts, alpha, beta, n)

    # theta = np.random.randn(n_params)
    # log_posterior(theta)
    n_trials = 100
    random = np.random.RandomState(0)
    x0 = random.rand(n_trials, n_params)
    for i in range(n_trials):
        value = scipy.optimize.check_grad(
            lambda x: log_posterior(x)[0],
            lambda x: log_posterior(x)[1],
        x0[i])
        assert value < 1e-4


def test_5():
    grid = NDGrid(n_bins_per_feature=2)
    seqs = grid.fit_transform(load_quadwell(random_state=0)['trajectories'])

    model2 = BayesianContinuousTimeMSM(n_samples=100).fit(seqs)

    print(model2.summarize())
