# Copyright 2011-2013 Kwant authors.
#
# This file is part of Kwant.  It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution and at
# http://kwant-project.org/license.  A list of Kwant authors can be found in
# the AUTHORS file at the top-level directory of this distribution and at
# http://kwant-project.org/authors.

import numpy as np
from scipy import stats
from nose.tools import assert_raises
from kwant import rmt
assert_allclose = np.testing.assert_allclose


def test_gaussian():
    np.random.seed(10)
    n = 8
    for sym in rmt.sym_list:
        if sym not in ('A', 'D', 'AI'):
            assert_raises(ValueError, rmt.gaussian, 5, sym)
        h = rmt.gaussian(n, sym)
        if rmt.t(sym):
            t_mat = np.array(rmt.h_t_matrix[sym])
            t_mat = np.kron(np.identity(n / len(t_mat)), t_mat)
            assert_allclose(h, np.dot(t_mat, np.dot(h.conj(), t_mat)),
                            err_msg='TRS broken in ' + sym)
        if rmt.p(sym):
            p_mat = np.array(rmt.h_p_matrix[sym])
            p_mat = np.kron(np.identity(n / len(p_mat)), p_mat)
            assert_allclose(h, -np.dot(p_mat, np.dot(h.conj(), p_mat)),
                            err_msg='PHS broken in ' + sym)
        if rmt.c(sym):
            sz = np.kron(np.identity(n / 2), np.diag([1, -1]))
            assert_allclose(h, -np.dot(sz, np.dot(h, sz)),
                            err_msg='SLS broken in ' + sym)

    for sym in rmt.sym_list:
        matrices = np.array([rmt.gaussian(n, sym)[-1, 0] for i in range(3000)])
        matrices = matrices.imag if sym in ('D', 'BDI') else matrices.real
        ks = stats.kstest(matrices, 'norm')
        assert (ks[1] > 0.1), (sym, ks)


def test_circular():
    np.random.seed(10)
    n = 6
    sy = np.kron(np.identity(n / 2), [[0, 1j], [-1j, 0]])
    for sym in rmt.sym_list:
        if rmt.t(sym) == -1 or rmt.p(sym) == -1:
            assert_raises(ValueError, rmt.circular, 5, sym)
        s = rmt.circular(n, sym)
        assert_allclose(np.dot(s, s.T.conj()), np.identity(n), atol=1e-9,
                        err_msg='Unitarity broken in ' + sym)
        if rmt.t(sym):
            s1 = np.copy(s.T if rmt.p(sym) != -1
                         else np.dot(sy, np.dot(s.T, sy)))
            s1 *= rmt.t(sym) * (-1 if rmt.p(sym) == -1 else 1)
            assert_allclose(s, s1, atol=1e-9, err_msg='TRS broken in ' + sym)
        if rmt.p(sym):
            s1 = np.copy(s.conj() if rmt.p(sym) != -1
                         else np.dot(sy, np.dot(s.conj(), sy)))
            if sym in ('DIII', 'CI'):
                s1 *= -1
            assert_allclose(s, s1, atol=1e-9, err_msg='PHS broken in ' + sym)
        if rmt.c(sym):
            assert_allclose(s, s.T.conj(), atol=1e-9,
                            err_msg='SLS broken in ' + sym)

    # Check for distribution properties if the ensemble is a symmetric group.
    f = lambda x: x[0] / np.linalg.norm(x)
    for sym in ('A', 'C'):
        sample_distr = np.apply_along_axis(f, 0, np.random.randn(2 * n, 1000))
        s_sample = np.array([rmt.circular(n, sym)
                             for i in range(1000)])
        assert stats.ks_2samp(sample_distr, s_sample[:, 0, 0].real)[1] > 0.1, \
                'Noncircular distribution in ' + sym
        assert stats.ks_2samp(sample_distr, s_sample[:, 3, 2].real)[1] > 0.1, \
                'Noncircular distribution in ' + sym
        assert stats.ks_2samp(sample_distr, s_sample[:, 1, 1].imag)[1] > 0.1, \
                'Noncircular distribution in ' + sym
        assert stats.ks_2samp(sample_distr, s_sample[:, 2, 3].imag)[1] > 0.1, \
                'Noncircular distribution in ' + sym

    sample_distr = np.apply_along_axis(f, 0, np.random.randn(n, 500))
    s_sample = np.array([rmt.circular(n, 'D') for i in range(500)])
    ks = stats.ks_2samp(sample_distr, s_sample[:, 0, 0])
    assert ks[1] > 0.1, 'Noncircular distribution in D ' + str(ks)
    ks = stats.ks_2samp(sample_distr, s_sample[:, 3, 2])
    assert ks[1] > 0.1, 'Noncircular distribution in D ' + str(ks)
