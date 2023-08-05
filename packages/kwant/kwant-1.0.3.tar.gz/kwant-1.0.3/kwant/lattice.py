# Copyright 2011-2013 Kwant authors.
#
# This file is part of Kwant.  It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution and at
# http://kwant-project.org/license.  A list of Kwant authors can be found in
# the AUTHORS file at the top-level directory of this distribution and at
# http://kwant-project.org/authors.

from __future__ import division

__all__ = ['TranslationalSymmetry', 'general', 'Polyatomic', 'Monatomic',
           'chain', 'square', 'triangular', 'honeycomb', 'kagome']

from math import sqrt
from itertools import product
import numpy as np
import tinyarray as ta
from . import builder
from .linalg import lll


def general(prim_vecs, basis=None, name=''):
    """
    Create a Bravais lattice of any dimensionality, with any number of sites.

    Parameters
    ----------
    prim_vecs : sequence of sequences of floats
        The primitive vectors of the Bravais lattice.
    basis : sequence of floats
        The coordinates of the basis sites inside the unit cell.
    name : string or sequence of strings
        Name of the lattice, or the list of names of all of the sublattices.
        If the name of the lattice is given, the names of sublattices (if any)
        are obtained by appending their number to the name of the lattice.

    Returns
    -------
    lattice : either `Monatomic` or `Polyatomic`
        Resulting lattice.

    Notes
    -----
    This function is largely an alias to the constructors of corresponding
    lattices.
    """
    if basis is None:
        return Monatomic(prim_vecs, name=name)
    else:
        return Polyatomic(prim_vecs, basis, name=name)


class Polyatomic(object):
    """
    A Bravais lattice with an arbitrary number of sites in the basis.

    Contains `Monatomic` sublattices.  Note that an instance of ``Polyatomic`` is
    not itself a `~kwant.builder.SiteFamily`, only its sublattices are.

    Parameters
    ----------
    prim_vecs : sequence of sequences of floats
        The primitive vectors of a Bravais lattice.
    basis : sequence of sequences of floats
        The coordinates of the basis sites inside the unit cell.
    name : string or sequence of strings
        The name of the lattice, or a list of the names of all the sublattices.
        If the name of the lattice is given, the names of sublattices are
        obtained by appending their number to the name of the lattice.

    Attributes
    ----------
    prim_vecs : sequence of vectors
        ``prim_vecs[i]`` is the `i`-th primitive basis vector of the lattice
    sublattices : list of `Monatomic`
        Sublattices belonging to this lattice.

    Raises
    ------
    ValueError
        If dimensionalities do not match.
    """
    def __init__(self, prim_vecs, basis, name=''):
        prim_vecs = ta.array(prim_vecs, float)
        dim = prim_vecs.shape[1]
        if name is None:
            name = ''
        if isinstance(name, str):
            name = [name + str(i) for i in range(len(basis))]
        if prim_vecs.shape[0] > dim:
            raise ValueError('Number of primitive vectors exceeds '
                             'the space dimensionality.')
        basis = ta.array(basis, float)
        if basis.shape[1] != dim:
            raise ValueError('Basis dimensionality does not match '
                             'the space dimensionality.')
        self.sublattices = [Monatomic(prim_vecs, offset, sname)
                            for offset, sname in zip(basis, name)]
        # Sequence of primitive vectors of the lattice.
        self._prim_vecs = prim_vecs
        # Precalculation of auxiliary arrays for real space calculations.
        self._reduced_vecs, self._transf = lll.lll(prim_vecs)
        self._voronoi = ta.dot(lll.voronoi(self._reduced_vecs), self._transf)

    def shape(self, function, start):
        """Return a key for all the lattice sites inside a given shape.

        The object returned by this method is primarily meant to be used as a
        key for indexing `kwant.Builder` instances.  See example below.

        Parameters
        ----------
        function : callable
            A function of real space coordinates that returns a truth value:
            true for coordinates inside the shape, and false otherwise.
        start : float vector
            The origin for the flood-fill algorithm.

        Returns
        -------
        shape_sites : function

        Notes
        -----
        When the function returned by this method is called, a flood-fill
        algorithm finds and yields all the lattice sites inside the specified
        shape starting from the specified position.

        A `~kwant.builder.Symmetry` or `~kwant.builder.Builder` may be passed as
        sole argument when calling the function returned by this method.  This
        will restrict the flood-fill to the fundamental domain of the symmetry
        (or the builder's symmetry).  Note that unless the shape function has
        that symmetry itself, the result may be unexpected.

        Examples
        --------
        >>> def circle(pos):
        ...     x, y = pos
        ...     return x**2 + y**2 < 100
        ...
        >>> lat = kwant.lattice.honeycomb()
        >>> sys = kwant.Builder()
        >>> sys[lat.shape(circle, (0, 0))] = 0
        >>> sys[lat.neighbors()] = 1
        """
        def shape_sites(symmetry=None):
            Site = builder.Site

            if symmetry is None:
                symmetry = builder.NoSymmetry()
            elif not isinstance(symmetry, builder.Symmetry):
                symmetry = symmetry.symmetry

            def fd_site(lat, tag):
                return symmetry.to_fd(Site(lat, tag, True))

            dim = len(start)
            if dim != self._prim_vecs.shape[1]:
                raise ValueError('Dimensionality of start position does not '
                                 'match the space dimensionality.')
            lats = self.sublattices
            deltas = list(self._voronoi)

            #### Flood-fill ####
            sites = []
            for tag in set(lat.closest(start) for lat in lats):
                for lat in lats:
                    site = fd_site(lat, tag)
                    if function(site.pos):
                        sites.append(site)
            if not sites:
                msg = 'No sites close to {0} are inside the desired shape.'
                raise ValueError(msg.format(start))
            tags = set(s.tag for s in sites)

            while sites:
                old_tags = tags
                tags = set()
                for site in sites:
                    yield site
                    tags.add(site.tag)
                old_tags |= tags

                new_tags = set()
                for tag in tags:
                    for delta in deltas:
                         new_tag = tag + delta
                         if new_tag not in old_tags:
                             new_tags.add(new_tag)

                sites = set()
                for tag in new_tags:
                    for lat in lats:
                        site = fd_site(lat, tag)
                        if site.tag not in old_tags and function(site.pos):
                            sites.add(site)

        return shape_sites

    def wire(self, center, radius):
        """Return a key for all the lattice sites inside an infinite cylinder.

        This method makes it easy to define cylindrical (2d: rectangular) leads
        that point in any direction.  The object returned by this method is
        primarily meant to be used as a key for indexing `kwant.Builder`
        instances.  See example below.

        Parameters
        ----------
        center : float vector
            A point belonging to the axis of the cylinder.
        radius : float
            The radius of the cylinder.

        Notes
        -----
        The function returned by this method is to be called with a
        `~kwant.builder.TranslationalSymmetry` instance (or a
        `~kwant.builder.Builder` instance whose symmetry is used then) as sole
        argument.  All the lattice sites (in the fundamental domain of the
        symmetry) inside the specified infinite cylinder are yielded.  The
        direction of the cylinder is determined by the symmetry.

        Examples
        --------
        >>> lat = kwant.lattice.honeycomb()
        >>> sym = kwant.TranslationalSymmetry(lat.a.vec((-2, 1)))
        >>> lead = kwant.Builder(sym)
        >>> lead[lat.wire((0, -5), 5)] = 0
        >>> lead[lat.neighbors()] = 1
        """
        center = ta.array(center, float)

        def wire_sites(sym):
            if not isinstance(sym, builder.Symmetry):
                sym = sym.symmetry
            if not isinstance(sym, TranslationalSymmetry):
                raise ValueError('wire shape only works with '
                                 'translational symmetry.')
            if len(sym.periods) != 1:
                raise ValueError('wire shape only works with one-dimensional '
                                 'translational symmetry.')
            period = np.array(sym.periods)[0]
            direction = ta.array(period / np.linalg.norm(period))
            r_squared = radius**2

            def wire_shape(pos):
                rel_pos = pos - center
                projection = rel_pos - direction * ta.dot(direction, rel_pos)
                return sum(projection * projection) <= r_squared

            return self.shape(wire_shape, center)(sym)

        return wire_sites

    def neighbors(self, n=1, eps=1e-8):
        """Return n-th nearest neighbor hoppings.

        Parameters
        ----------
        n : integer
            Order of the hoppings to return.
        eps : float
            Tolerance relative to the length of the shortest lattice vector for
            when to consider lengths to be approximately equal.

        Returns
        -------
        hoppings : list of kwant.builder.HopplingKind objects
            A list n-th nearest neighbor hoppings.

        Notes
        -----
        The hoppings are ordered lexicographically according to sublattice from
        which they originate, sublattice on which they end, and their lattice
        coordinates. Out of the two equivalent hoppings (a hopping and its
        reverse) only the lexicographically larger one is returned.
        """
        # This algorithm is not designed to be fast and can be improved,
        # however there is no real need.
        sls = self.sublattices
        shortest_hopping = sls[0].n_closest(sls[0](*([0] * sls[0].dim)).pos,
                                            2)[-1]
        eps *= np.linalg.norm(self.vec(shortest_hopping))
        nvec = len(self._prim_vecs)
        sublat_pairs = [(i, j) for (i, j) in product(sls, sls)
                        if sls.index(j) >= sls.index(i)]
        def first_nonnegative(tag):
            for i in tag:
                if i < 0:
                    return False
                elif i > 0:
                    return True
                else:
                    continue
            return True


        # Find the correct number of neighbors to calculate on each lattice.
        cutoff = n + 2
        while True:
            max_dist = []
            sites = []
            for i, j in sublat_pairs:
                origin = j(*ta.zeros(nvec)).pos
                tags = i.n_closest(origin, n=cutoff**nvec)

                ij_dist = [np.linalg.norm(i(*tag).pos - origin)
                              for tag in tags]
                sites.append((tags, (j, i), ij_dist))
            max_dist = [i[2][-1] for i in sites]
            distances = np.r_[tuple((i[2] for i in sites))]
            distances = np.sort(distances)
            group_boundaries = np.argwhere(np.diff(distances) > eps)
            if len(group_boundaries) < n:
                cutoff += 1
                continue
            try:
                n_dist = distances[group_boundaries[n]]
            except IndexError:
                cutoff += 1
                continue
            if np.all(max_dist > n_dist):
                break
            cutoff += 1

        # We now have all the required sites, we need to find n-th.
        result = []
        for group in sites:
            tags, distance = group[0], group[2]
            i, j = group[1]
            tags = np.array([tag for tag, dist in zip(tags, distance)
                             if abs(dist - n_dist) < eps])
            if len(tags):
                # Sort the tags.
                tags = tags[np.lexsort(tags.T[::-1])][::-1]
                # Throw away equivalent hoppings if
                # two sublattices are the same.
                if i == j and len(tags) > 1:
                    tags = tags[: len(tags) // 2]
                for tag in tags:
                    result.append(builder.HoppingKind(tag, j, i))
        return result

    @property
    def prim_vecs(self):
        return np.array(self._prim_vecs)

    def vec(self, int_vec):
        """
        Return the coordinates of a Bravais lattice vector in real space.

        Parameters
        ----------
        vec : integer vector

        Returns
        -------
        output : real vector
        """
        return ta.dot(int_vec, self._prim_vecs)


def short_array_repr(array):
    full = ' '.join([i.lstrip() for i in repr(array).split('\n')])
    return full[6 : -1]


def short_array_str(array):
    full = ', '.join([i.lstrip() for i in str(array).split('\n')])
    return full[1 : -1]


class Monatomic(builder.SiteFamily, Polyatomic):
    """
    A Bravais lattice with a single site in the basis.

    Instances of this class provide the `~kwant.builder.SiteFamily` interface.  Site
    tags (see `~kwant.builder.SiteFamily`) are sequences of integers and describe
    the lattice coordinates of a site.

    ``Monatomic`` instances are used as site families on their own or as sublattices
    of `Polyatomic` lattices.

    Parameters
    ----------
    prim_vecs : sequence of sequences of floats
        Primitive vectors of the Bravais lattice.
    offset : vector of floats
        Displacement of the lattice origin from the real space
        coordinates origin.

    Attributes
    ----------
    offset : vector
        Displacement of the lattice origin from the real space
        coordinates origin.
    prim_vecs : sequence of vectors
        ``prim_vecs[i]`` is the `i`-th primitive basis vector of the lattice
    """

    def __init__(self, prim_vecs, offset=None, name=''):
        prim_vecs = ta.array(prim_vecs, float)
        dim = prim_vecs.shape[1]
        if name is None:
            name = ''
        if prim_vecs.shape[0] > dim:
            raise ValueError('Number of primitive vectors exceeds '
                             'the space dimensionality.')
        if offset is None:
            offset = ta.zeros(dim)
        else:
            offset = ta.array(offset, float)
            if offset.shape != (dim,):
                raise ValueError('Dimensionality of offset does not match '
                                 'that of the space.')

        msg = '{0}({1}, {2}, {3})'
        cl = self.__module__ + '.' + self.__class__.__name__
        canonical_repr = msg.format(cl, short_array_repr(prim_vecs),
                                    short_array_repr(offset), repr(name))
        super(Monatomic, self).__init__(canonical_repr, name)

        self.sublattices = [self]
        self._prim_vecs = prim_vecs
        self.inv_pv = ta.array(np.linalg.pinv(prim_vecs))
        self.offset = offset

        # Precalculation of auxiliary arrays for real space calculations.
        self._reduced_vecs, self._transf = lll.lll(prim_vecs)
        self._voronoi = ta.dot(lll.voronoi(self._reduced_vecs), self._transf)

        self.dim = dim
        self._lattice_dim = len(prim_vecs)

        if name != '':
            msg = "Monatomic lattice {0}, vectors {1}, origin {2}"
            self.cached_str = msg.format(name,
                                         short_array_str(self._prim_vecs),
                                         short_array_str(self.offset))
        else:
            msg = "unnamed Monatomic lattice, vectors {0}, origin [{1}]"
            self.cached_str = msg.format(short_array_str(self._prim_vecs),
                                         short_array_str(self.offset))

    def __str__(self):
        return self.cached_str

    def normalize_tag(self, tag):
        tag = ta.array(tag, int)
        if len(tag) != self._lattice_dim:
            raise ValueError("Dimensionality mismatch.")
        return tag

    def n_closest(self, pos, n=1):
        """Find n sites closest to position `pos`.

        Returns
        -------
        sites : numpy array
            An array with sites coordinates.
        """
        # TODO (Anton): transform to tinyarrays, once ta indexing is better.
        return np.dot(lll.cvp(pos - self.offset, self._reduced_vecs, n),
                      self._transf.T)

    def closest(self, pos):
        """
        Find the lattice coordinates of the site closest to position `pos`.
        """
        return ta.array(self.n_closest(pos)[0])

    def pos(self, tag):
        """Return the real-space position of the site with a given tag."""
        return ta.dot(tag, self._prim_vecs) + self.offset


# The following class is designed such that it should avoid floating
# point precision issues.

class TranslationalSymmetry(builder.Symmetry):
    """
    A translational symmetry defined in real space.

    Group elements of this symmetry are integer tuples of appropriate length.

    Parameters
    ----------
    p0, p1, p2, ... : sequences of real numbers
        The symmetry periods in real space.

    Notes
    -----
    This symmetry automatically chooses the fundamental domain for each new
    `SiteFamily` it encounters. If this site family does not correspond to a
    Bravais lattice, or if it does not have a commensurate period, an error is
    produced. A certain flexibility in choice of the fundamental domain can be
    achieved by calling manually the `add_site_family` method and providing it
    the `other_vectors` parameter.

    The fundamental domain for hoppings are all hoppings ``(a, b)`` with site
    `a` in fundamental domain of sites.
    """
    def __init__(self, *periods):
        self.periods = ta.array(periods)
        self._periods = self.periods
        if self.periods.ndim != 2:
            # TODO: remove the second part of the following message once
            # everybody got used to it.
            msg = "TranslationalSymmetry takes 1d sequences as parameters.\n" \
                "See What's new in Kwant 0.2 in the documentation."
            raise ValueError(msg)
        if np.linalg.matrix_rank(periods) < len(periods):
            raise ValueError("Translational symmetry periods must be "
                             "linearly independent")
        # A dictionary containing cached data required for applying the
        # symmetry to different site families.
        self.site_family_data = {}
        self.is_reversed = False

    def add_site_family(self, fam, other_vectors=None):
        """
        Select a fundamental domain for site family and cache associated data.

        Parameters
        ----------
        fam : `SiteFamily`
            the site family which has to be processed.  Be sure to delete the
            previously processed site families from `site_family_data` if you
            want to modify the cache.

        other_vectors : list of lists of integers
            Bravais lattice vectors used to complement the periods in forming
            a basis. The fundamental domain consists of all the lattice sites
            for which the zero coefficients corresponding to the symmetry
            periods in the basis formed by the symmetry periods and
            `other_vectors`. If an insufficient number of `other_vectors` is
            provided to form a basis, the missing ones are selected
            automatically.

        Raises
        ------
        KeyError
            If `fam` is already stored in `site_family_data`.
        ValueError
            If lattice `fam` is incompatible with given periods.
        """
        dim = self._periods.shape[1]
        if fam in self.site_family_data:
            raise KeyError('Family already processed, delete it from '
                           'site_family_data first.')
        inv = np.linalg.pinv(fam.prim_vecs)
        bravais_periods = np.dot(self._periods, inv)
        # Absolute tolerance is correct in the following since we want an error
        # relative to the closest integer.
        if not np.allclose(bravais_periods, np.round(bravais_periods),
                           rtol=0, atol=1e-8) or \
           not np.allclose([fam.vec(i) for i in bravais_periods],
                           self._periods):
            msg = 'Site family {0} does not have commensurate periods with ' +\
                  'symmetry {1}.'
            raise ValueError(msg.format(fam, self))
        bravais_periods = np.array(np.round(bravais_periods), dtype='int')
        (num_dir, lat_dim) = bravais_periods.shape
        if other_vectors is None:
            other_vectors = np.zeros((0, lat_dim), dtype=int)
        else:
            other_vectors = np.array(other_vectors)
            if np.any(np.round(other_vectors) - other_vectors):
                raise ValueError('Only integer other_vectors are allowed.')
            other_vectors = np.array(np.round(other_vectors), dtype=int)

        m = np.zeros((lat_dim, lat_dim), dtype=int)

        m.T[:num_dir] = bravais_periods
        num_vec = num_dir + len(other_vectors)
        m.T[num_dir:num_vec] = other_vectors

        if np.linalg.matrix_rank(m) < num_vec:
            raise ValueError('other_vectors and symmetry periods are not '
                             'linearly independent.')

        # To define the fundamental domain of the new site family we now need to
        # choose `lat_dim - num_vec` extra lattice vectors that are not
        # linearly dependent on the vectors we already have. To do so we
        # continuously add the lattice basis vectors one by one such that they
        # are not linearly dependent on the existent vectors
        while num_vec < lat_dim:
            vh = np.linalg.svd(np.dot(m[:, :num_vec].T, fam.prim_vecs),
                               full_matrices=False)[2]
            projector = np.identity(dim) - np.dot(vh.T, vh)

            residuals = np.dot(fam.prim_vecs, projector)
            residuals = np.apply_along_axis(np.linalg.norm, 1, residuals)
            m[np.argmax(residuals), num_vec] = 1
            num_vec += 1

        det_m = int(round(np.linalg.det(m)))
        if det_m == 0:
            print m
            raise RuntimeError('Adding site family failed.')

        det_x_inv_m = \
            np.array(np.round(det_m * np.linalg.inv(m)), dtype=int)
        assert (np.dot(m, det_x_inv_m) // det_m == np.identity(lat_dim)).all()

        det_x_inv_m_part = det_x_inv_m[:num_dir, :]
        m_part = m[:, :num_dir]
        self.site_family_data[fam] = (ta.array(m_part),
                                     ta.array(det_x_inv_m_part), det_m)

    @property
    def num_directions(self):
        return len(self.periods)

    def _get_site_family_data(self, family):
        try:
            return self.site_family_data[family]
        except KeyError:
            self.add_site_family(family)
            return self.site_family_data[family]

    def which(self, site):
        det_x_inv_m_part, det_m = self._get_site_family_data(site.family)[-2:]
        result = ta.dot(det_x_inv_m_part, site.tag) // det_m
        return -result if self.is_reversed else result

    def act(self, element, a, b=None):
        m_part = self._get_site_family_data(a.family)[0]
        try:
            delta = ta.dot(m_part, element)
        except ValueError:
            msg = 'Expecting a {0}-tuple group element, but got `{1}` instead.'
            raise ValueError(msg.format(self.num_directions, element))
        if self.is_reversed:
            delta = -delta
        if b is None:
            return builder.Site(a.family, a.tag + delta, True)
        elif b.family == a.family:
            return builder.Site(a.family, a.tag + delta, True), \
                builder.Site(b.family, b.tag + delta, True)
        else:
            m_part = self._get_site_family_data(b.family)[0]
            try:
                delta2 = ta.dot(m_part, element)
            except ValueError:
                msg = 'Expecting a {0}-tuple group element, ' + \
                      'but got `{1}` instead.'
                raise ValueError(msg.format(self.num_directions, element))
            if self.is_reversed:
                delta2 = -delta2
            return builder.Site(a.family, a.tag + delta, True), \
                builder.Site(b.family, b.tag + delta2, True)

    def to_fd(self, a, b=None):
        return self.act(-self.which(a), a, b)

    def reversed(self):
        """Return a reversed copy of the symmetry.

        The resulting symmetry has all the period vectors opposite to the
        original and an identical fundamental domain.
        """
        result = TranslationalSymmetry(*self._periods)
        result.site_family_data = self.site_family_data
        result.is_reversed = not self.is_reversed
        result.periods = -self.periods
        return result



################ Library of lattices

def chain(a=1, name=''):
    """Make a one-dimensional lattice."""
    return Monatomic(((a,),), name=name)


def square(a=1, name=''):
    """Make a square lattice."""
    return Monatomic(((a, 0), (0, a)), name=name)


tri = ta.array(((1, 0), (0.5, 0.5 * sqrt(3))))

def triangular(a=1, name=''):
    """Make a triangular lattice."""
    return Monatomic(a * tri, name=name)


def honeycomb(a=1, name=''):
    """Make a honeycomb lattice."""
    lat = Polyatomic(a * tri, ((0, 0), (0, a / sqrt(3))), name=name)
    lat.a, lat.b = lat.sublattices
    return lat


def kagome(a=1, name=''):
    """Make a kagome lattice."""
    lat = Polyatomic(a * tri, ((0, 0),) + tuple(0.5 * a * tri), name=name)
    lat.a, lat.b, lat.c = lat.sublattices
    return lat


# TODO (Anton): unhide _prim_vecs, once tinyarray supports indexing of
# sub-arrays.
