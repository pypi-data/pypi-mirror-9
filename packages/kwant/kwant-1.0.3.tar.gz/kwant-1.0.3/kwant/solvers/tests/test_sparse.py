# Copyright 2011-2013 Kwant authors.
#
# This file is part of Kwant.  It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution and at
# http://kwant-project.org/license.  A list of Kwant authors can be found in
# the AUTHORS file at the top-level directory of this distribution and at
# http://kwant-project.org/authors.

from nose.plugins.skip import Skip, SkipTest
from  kwant.solvers.sparse import smatrix, greens_function, ldos, wave_function
import kwant.solvers.sparse
import _test_sparse

def test_output():
    _test_sparse.test_output(smatrix)


def test_one_lead():
    _test_sparse.test_one_lead(smatrix)


def test_smatrix_shape():
    _test_sparse.test_smatrix_shape(smatrix)


def test_two_equal_leads():
    _test_sparse.test_two_equal_leads(smatrix)


def test_graph_system():
    _test_sparse.test_graph_system(smatrix)


def test_singular_graph_system():
    _test_sparse.test_singular_graph_system(smatrix)


def test_tricky_singular_hopping():
    _test_sparse.test_tricky_singular_hopping(smatrix)


def test_selfenergy():
    _test_sparse.test_selfenergy(greens_function, smatrix)


def test_selfenergy_reflection():
    _test_sparse.test_selfenergy_reflection(greens_function, smatrix)


def test_very_singular_leads():
    _test_sparse.test_very_singular_leads(smatrix)


def test_umfpack_del():
    if kwant.solvers.sparse.uses_umfpack:
        assert hasattr(kwant.solvers.sparse.umfpack.UmfpackContext,
                       '__del__')
    else:
        raise SkipTest


def test_ldos():
    _test_sparse.test_ldos(ldos)


def test_wavefunc_ldos_consistency():
    _test_sparse.test_wavefunc_ldos_consistency(wave_function, ldos)
