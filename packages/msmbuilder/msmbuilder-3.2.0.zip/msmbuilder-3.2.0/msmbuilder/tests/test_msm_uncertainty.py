from __future__ import print_function
import numpy as np
import scipy.linalg
from scipy.linalg import eigvals
from scipy.optimize import approx_fprime
import scipy.stats
from msmbuilder.cluster import NDGrid
from msmbuilder.example_datasets import load_doublewell
from msmbuilder.msm import MarkovStateModel, ContinuousTimeMSM
from msmbuilder.msm.core import _solve_msm_eigensystem
import matplotlib.pyplot as pp


def test_0():
    # Verify that the partial derivatives of the ith eigenvalue of the
    # transition matrix with respect to the entries of the transition matrix
    # is given by the outer product of the left and right eigenvectors
    # corresponding to that eigenvalue.
    # \frac{\partial \lambda_k}{\partial T_{ij}} = U_{i,k} V_{j,k}

    X = load_doublewell(random_state=0)['trajectories']
    Y = NDGrid(n_bins_per_feature=10).fit_transform(X)
    model = MarkovStateModel(verbose=False).fit(Y)
    n = model.n_states_

    u, lv, rv = _solve_msm_eigensystem(model.transmat_, n)

    # first, compute forward difference numerical derivatives
    h = 1e-7
    dLambda_dP_numeric = np.zeros((n, n, n))
    # dLambda_dP_numeric[eigenvalue_index, i, j]
    for i in range(n):
        for j in range(n):
            # perturb the (i,j) entry of transmat
            H = np.zeros((n, n))
            H[i, j] = h
            u_perturbed = sorted(np.real(eigvals(model.transmat_ + H)), reverse=True)

            # compute the forward different approx. derivative of each
            # of the eigenvalues
            for k in range(n):
                # sort the eigenvalues of the perturbed matrix in descending
                # order, to be consistent w/ _solve_msm_eigensystem
                dLambda_dP_numeric[k, i, j] = (u_perturbed[k] - u[k]) / h

    for k in range(n):
        analytic = np.outer(lv[:, k], rv[:, k])
        np.testing.assert_almost_equal(dLambda_dP_numeric[k], analytic, decimal=5)


def test_1():
    X = load_doublewell(random_state=0)['trajectories']
    for i in range(3):
        Y = NDGrid(n_bins_per_feature=10).fit_transform([X[i]])
        model1 = MarkovStateModel(verbose=False).fit(Y)
        model2 = ContinuousTimeMSM().fit(Y)

        print('MSM uncertainty timescales:')
        print(model1.uncertainty_timescales())
        print('ContinuousTimeMSM uncertainty timescales:')
        print(model2.uncertainty_timescales())
        print()


def test_2():
    model = MarkovStateModel(verbose=False)
    C = np.array([
        [4380, 153,  15,   2,    0,    0],
        [211,  4788, 1,    0,    0,    0],
        [169,  1,    4604, 226,  0,    0],
        [3,    13,   158,  4823, 3,    0],
        [0,    0,    0,    4,    4978, 18],
        [7,    5,    0,    0,    62,   4926]], dtype=float)
    C = C + 1.0 / 6.0
    model.n_states_ = C.shape[0]
    model.countsmat_ = C
    model.transmat_, model.populations_ = model._fit_mle(C)

    n_trials = 5000
    random = np.random.RandomState(0)
    all_timescales = np.zeros((n_trials, model.n_states_ - 1))
    all_eigenvalues = np.zeros((n_trials, model.n_states_))
    for i in range(n_trials):
        T = np.vstack([random.dirichlet(C[i]) for i in range(C.shape[0])])
        u = _solve_msm_eigensystem(T, k=6)[0]
        all_eigenvalues[i] = u
        all_timescales[i] = -1 / np.log(u[1:])

    pp.figure(figsize=(12, 8))
    for i in range(3):
        pp.subplot(2,3,i+1)
        pp.title('Timescale %d' % i)
        kde = scipy.stats.gaussian_kde(all_timescales[:, i])
        xx = np.linspace(all_timescales[:,i].min(), all_timescales[:,i].max())
        r = scipy.stats.norm(loc=model.timescales_[i], scale=model.uncertainty_timescales()[i])
        pp.plot(xx, kde.evaluate(xx), c='r', label='Samples')
        pp.plot(xx, r.pdf(xx), c='b', label='Analytic')

    for i in range(1, 4):
        pp.subplot(2,3,3+i)
        pp.title('Eigenvalue %d' % i)
        kde = scipy.stats.gaussian_kde(all_eigenvalues[:, i])
        xx = np.linspace(all_eigenvalues[:,i].min(), all_eigenvalues[:,i].max())
        r = scipy.stats.norm(loc=model.eigenvalues_[i], scale=model.uncertainty_eigenvalues()[i])
        pp.plot(xx, kde.evaluate(xx), c='r', label='Samples')
        pp.plot(xx, r.pdf(xx), c='b', label='Analytic')

    pp.tight_layout()
    pp.legend(loc=4)
    pp.savefig('test_msm_uncertainty_plots.png')
