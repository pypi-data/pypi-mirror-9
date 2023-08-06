# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division


import itertools


import numpy as np


from allel.model import SortedIndex
from allel.util import asarray_ndim
from allel.stats.diversity import sequence_divergence


def pairwise_distance(x, metric):
    """Compute pairwise distance between individuals (e.g., samples or
    haplotypes).

    Parameters
    ----------

    x : array_like, shape (n, m, ...)
        Array of m observations (e.g., samples or haplotypes) in a space
        with n dimensions (e.g., variants). Note that the order of the first
        two dimensions is **swapped** compared to what is expected by
        scipy.spatial.distance.pdist.
    metric : string or function
        Distance metric. See documentation for the function
        :func:`scipy.spatial.distance.pdist` for a list of built-in
        distance metrics.

    Returns
    -------

    dist : ndarray, shape (n_individuals * (n_individuals - 1) / 2,)
        Distance matrix in condensed form.

    See Also
    --------

    allel.plot.pairwise_distance

    Notes
    -----

    If `x` is a bcolz carray, a chunk-wise implementation will be used to
    avoid loading the entire input array into memory. This means that
    a distance matrix will be calculated for each chunk in the input array,
    and the results will be summed to produce the final output. For some
    distance metrics this will return a different result from the standard
    implementation, although the relative distances may be equivalent.

    Examples
    --------

    >>> import allel
    >>> g = allel.model.GenotypeArray([[[0, 0], [0, 1], [1, 1]],
    ...                                [[0, 1], [1, 1], [1, 2]],
    ...                                [[0, 2], [2, 2], [-1, -1]]])
    >>> d = allel.stats.pairwise_distance(g.to_n_alt(), metric='cityblock')
    >>> d
    array([ 3.,  4.,  3.])
    >>> import scipy.spatial
    >>> scipy.spatial.distance.squareform(d)
    array([[ 0.,  3.,  4.],
           [ 3.,  0.,  3.],
           [ 4.,  3.,  0.]])

    """

    import scipy.spatial

    # check inputs
    if not hasattr(x, 'ndim'):
        x = np.asarray(x)
    if x.ndim < 2:
        raise ValueError('array with at least 2 dimensions expected')

    if x.ndim == 2:
        # use scipy to calculate distance, it's most efficient

        def f(b):

            # transpose as pdist expects (m, n) for m observations in an
            # n-dimensional space
            t = b.T

            # compute the distance matrix
            return scipy.spatial.distance.pdist(t, metric=metric)

    else:
        # use our own implementation, it handles multidimensional observations

        def f(b):
            return pdist(b, metric=metric)

    if hasattr(x, 'chunklen'):
        # use chunk-wise implementation
        blen = x.chunklen
        dist = None
        for i in range(0, x.shape[0], blen):
            block = x[i:i+blen]
            if dist is None:
                dist = f(block)
            else:
                dist += f(block)

    else:
        # standard implementation
        dist = f(x)

    return dist


def pdist(x, metric):
    """Alternative implementation of :func:`scipy.spatial.distance.pdist`
    which is slower but more flexible in that arrays with >2 dimensions can be
    passed, allowing for multidimensional observations, e.g., diploid
    genotype calls or allele counts.

    Parameters
    ----------

    x : array_like, shape (n, m, ...)
        Array of m observations (e.g., samples or haplotypes) in a space
        with n dimensions (e.g., variants). Note that the order of the first
        two dimensions is **swapped** compared to what is expected by
        scipy.spatial.distance.pdist.
    metric : string or function
        Distance metric. See documentation for the function
        :func:`scipy.spatial.distance.pdist` for a list of built-in
        distance metrics.

    Returns
    -------

    dist : ndarray
        Distance matrix in condensed form.

    """

    if isinstance(metric, str):
        import scipy.spatial
        if hasattr(scipy.spatial.distance, metric):
            metric = getattr(scipy.spatial.distance, metric)
        else:
            raise ValueError('metric name not found')

    m = x.shape[1]
    dist = list()
    for i, j in itertools.combinations(range(m), 2):
        a = x[:, i, ...]
        b = x[:, j, ...]
        d = metric(a, b)
        dist.append(d)
    return np.array(dist)


def pairwise_dxy(pos, gac, start=None, stop=None, is_accessible=None):
    """Convenience function to calculate a pairwise distance matrix using
    nucleotide divergence (a.k.a. Dxy) as the distance metric.

    Parameters
    ----------

    pos : array_like, int, shape (n_variants,)
        Variant positions.
    gac : array_like, int, shape (n_variants, n_samples, n_alleles)
        Per-genotype allele counts.
    start : int, optional
        Start position of region to use.
    stop : int, optional
        Stop position of region to use.
    is_accessible : array_like, bool, shape (len(contig),), optional
        Boolean array indicating accessibility status for all positions in the
        chromosome/contig.

    Returns
    -------

    dist : ndarray
        Distance matrix in condensed form.

    See Also
    --------

    allel.model.GenotypeArray.to_allele_counts
    """

    if not isinstance(pos, SortedIndex):
        pos = SortedIndex(pos, copy=False)
    gac = asarray_ndim(gac, 3)
    # compute this once here, to avoid repeated evaluation within the loop
    gan = np.sum(gac, axis=2)
    m = gac.shape[1]
    dist = list()
    for i, j in itertools.combinations(range(m), 2):
        ac1 = gac[:, i, ...]
        an1 = gan[:, i]
        ac2 = gac[:, j, ...]
        an2 = gan[:, j]
        d = sequence_divergence(pos, ac1, ac2, an1=an1, an2=an2,
                                start=start, stop=stop,
                                is_accessible=is_accessible)
        dist.append(d)
    return np.array(dist)
