# -*- coding: utf-8 -*-
"""
This module provides statistical functions for use with variant call data.

"""
from __future__ import absolute_import, print_function, division


import numpy as np


from allel.model import GenotypeArray, SortedIndex
from allel.util import asarray_ndim, ignore_invalid, check_arrays_aligned


def moving_statistic(values, statistic, size, start=0, stop=None, step=None):
    """Calculate a statistic in a moving window over `values`.

    Parameters
    ----------

    values : array_like
        The data to summarise.
    statistic : function
        The statistic to compute within each window.
    size : int
        The window size (number of values).
    start : int, optional
        The index at which to start.
    stop : int, optional
        The index at which to stop.
    step : int, optional
        The distance between start positions of windows. If not given,
        defaults to the window size, i.e., non-overlapping windows.

    Returns
    -------

    out : ndarray, shape (n_windows,)

    Examples
    --------

    >>> import allel
    >>> values = [2, 5, 8, 16]
    >>> allel.stats.moving_statistic(values, np.sum, size=2)
    array([ 7, 24])
    >>> allel.stats.moving_statistic(values, np.sum, size=2, step=1)
    array([ 7, 13, 24])

    """

    # determine step
    if stop is None:
        stop = len(values)
    if step is None:
        step = size

    # setup output
    out = []

    last = False

    # iterate over windows
    for window_start in range(start, stop, step):

        # determine window stop
        window_stop = window_start + size
        if window_stop >= stop:
            # last window
            window_stop = stop
            last = True

        # extract values for window
        window_values = values[window_start:window_stop]

        # compute statistic
        s = statistic(window_values)

        # store outputs
        out.append(s)

        if last:
            break

    # convert to arrays for output
    return np.array(out)


def _make_windows(pos, size, start, stop, step):
    last = False

    # determine start and stop positions
    if start is None:
        start = pos[0]
    if stop is None:
        stop = pos[-1]
    if step is None:
        # non-overlapping
        step = size

    windows = []
    for window_start in range(start, stop, step):

        # determine window stop
        window_stop = window_start + size
        if window_stop >= stop:
            # last window
            window_stop = stop
            last = True
        else:
            window_stop -= 1

        windows.append([window_start, window_stop])

        if last:
            break

    return windows


def windowed_count(pos, size=None, start=None, stop=None, step=None,
                   windows=None):
    """Count the number of items in windows over a single chromosome/contig.

    Parameters
    ----------

    pos : array_like, int, shape (n_items,)
        The item positions in ascending order, using 1-based coordinates..
    size : int
        The window size (number of bases).
    start : int, optional
        The position at which to start (1-based).
    stop : int, optional
        The position at which to stop (1-based).
    step : int, optional
        The distance between start positions of windows. If not given,
        defaults to the window size, i.e., non-overlapping windows.
    windows : array_like, int, shape (n_windows, 2), optional
        Manually specify the windows to use as a sequence of (window_start,
        window_stop) positions, using 1-based coordinates. Overrides the
        size/start/stop/step parameters.

    Returns
    -------

    counts : ndarray, int, shape (n_windows,)
        The number of items in each window.
    windows : ndarray, int, shape (n_windows, 2)
        The windows used, as an array of (window_start, window_stop) positions,
        using 1-based coordinates.

    Notes
    -----

    The window stop positions are included within a window.

    The final window will be truncated to the specified stop position,
    and so may be smaller than the other windows.

    Examples
    --------

    Non-overlapping windows::

        >>> import allel
        >>> pos = [1, 7, 12, 15, 28]
        >>> counts, windows = allel.stats.windowed_count(pos, size=10)
        >>> counts
        array([2, 2, 1])
        >>> windows
        array([[ 1, 10],
               [11, 20],
               [21, 28]])

    Half-overlapping windows::

        >>> counts, windows = allel.stats.windowed_count(pos, size=10, step=5)
        >>> counts
        array([2, 3, 2, 0, 1])
        >>> windows
        array([[ 1, 10],
               [ 6, 15],
               [11, 20],
               [16, 25],
               [21, 28]])

    """

    # assume sorted positions
    pos = SortedIndex(pos, copy=False)

    # setup windows
    if windows is None:
        windows = _make_windows(pos, size, start, stop, step)

    # setup output
    counts = []

    # iterate over windows
    for window_start, window_stop in windows:

        # locate window
        try:
            loc = pos.locate_range(window_start, window_stop)
        except KeyError:
            n = 0
        else:
            n = loc.stop - loc.start

        # store outputs
        counts.append(n)

    # convert to arrays for output
    return np.asarray(counts), np.asarray(windows)


def windowed_statistic(pos, values, statistic, size, start=None, stop=None,
                       step=None, windows=None, fill=np.nan):
    """Calculate a statistic from items in windows over a single
    chromosome/contig.

    Parameters
    ----------

    pos : array_like, int, shape (n_items,)
        The item positions in ascending order, using 1-based coordinates..
    values : array_like, int, shape (n_items,)
        The values to summarise.
    statistic : function
        The statistic to compute.
    size : int
        The window size (number of bases).
    start : int, optional
        The position at which to start (1-based).
    stop : int, optional
        The position at which to stop (1-based).
    step : int, optional
        The distance between start positions of windows. If not given,
        defaults to the window size, i.e., non-overlapping windows.
    windows : array_like, int, shape (n_windows, 2), optional
        Manually specify the windows to use as a sequence of (window_start,
        window_stop) positions, using 1-based coordinates. Overrides the
        size/start/stop/step parameters.
    fill : object, optional
        The value to use where a window is empty, i.e., contains no items.

    Returns
    -------

    out : ndarray, shape (n_windows,)
        The value of the statistic for each window.
    windows : ndarray, int, shape (n_windows, 2)
        The windows used, as an array of (window_start, window_stop) positions,
        using 1-based coordinates.
    counts : ndarray, int, shape (n_windows,)
        The number of items in each window.

    Notes
    -----

    The window stop positions are included within a window.

    The final window will be truncated to the specified stop position,
    and so may be smaller than the other windows.

    Examples
    --------

    Count non-zero (i.e., True) items in non-overlapping windows::

        >>> import allel
        >>> pos = [1, 7, 12, 15, 28]
        >>> values = [True, False, True, False, False]
        >>> nnz, windows, counts = allel.stats.windowed_statistic(
        ...     pos, values, statistic=np.count_nonzero, size=10
        ... )
        >>> nnz
        array([1, 1, 0])
        >>> windows
        array([[ 1, 10],
               [11, 20],
               [21, 28]])
        >>> counts
        array([2, 2, 1])

    Compute a sum over items in half-overlapping windows::

        >>> values = [3, 4, 2, 6, 9]
        >>> x, windows, counts = allel.stats.windowed_statistic(
        ...     pos, values, statistic=np.sum, size=10, step=5, fill=0
        ... )
        >>> x
        array([ 7, 12,  8,  0,  9])
        >>> windows
        array([[ 1, 10],
               [ 6, 15],
               [11, 20],
               [16, 25],
               [21, 28]])
        >>> counts
        array([2, 3, 2, 0, 1])

    """

    # assume sorted positions
    pos = SortedIndex(pos, copy=False)

    # check lengths are equal
    if len(pos) != len(values):
        raise ValueError('arrays must be of equal length')

    # setup windows
    if windows is None:
        windows = _make_windows(pos, size, start, stop, step)

    # setup outputs
    out = []
    counts = []

    # iterate over windows
    for window_start, window_stop in windows:

        # locate window
        try:
            loc = pos.locate_range(window_start, window_stop)
        except KeyError:
            n = 0
            s = fill
        else:
            n = loc.stop - loc.start
            # extract values for window
            window_values = values[loc]
            # compute statistic
            s = statistic(window_values)

        # store outputs
        out.append(s)
        counts.append(n)

    # convert to arrays for output
    return np.asarray(out), np.asarray(windows), np.asarray(counts)


def per_base(x, windows, is_accessible=None, fill=np.nan):
    """Calculate the per-base value of a windowed statistic.

    Parameters
    ----------

    x : array_like, shape (n_windows,)
        The statistic to average per-base.
    windows : array_like, int, shape (n_windows, 2)
        The windows used, as an array of (window_start, window_stop)
        positions using 1-based coordinates.
    is_accessible : array_like, bool, shape (len(contig),), optional
        Boolean array indicating accessibility status for all positions in the
        chromosome/contig.
    fill : object, optional
        Use this value where there are no accessible bases in a window.

    Returns
    -------

    y : ndarray, float, shape (n_windows,)
        The input array divided by the number of (accessible) bases in each
        window.
    n_bases : ndarray, int, shape (n_windows,)
        The number of (accessible) bases in each window

    """

    # calculate window sizes
    if is_accessible is None:
        # N.B., window stops are included
        n_bases = np.diff(windows, axis=1).reshape(-1) + 1
    else:
        pos_accessible = np.nonzero(is_accessible)[0] + 1  # use 1-based coords
        n_bases, _ = windowed_count(pos_accessible, windows=windows)

    # deal with multidimensional x
    if x.ndim == 1:
        pass
    elif x.ndim == 2:
        n_bases = n_bases[:, None]
    else:
        raise NotImplementedError('only arrays of 1 or 2 dimensions supported')

    with ignore_invalid():
        y = np.where(n_bases > 0, x / n_bases, fill)

    if n_bases.ndim > 1:
        n_bases = n_bases.reshape(-1)

    return y, n_bases


def mean_pairwise_diversity(ac, fill=np.nan):
    """Calculate for each variant the mean number of pairwise differences
    between haplotypes within a single population.

    Parameters
    ----------

    ac : array_like, int, shape (n_variants, n_alleles)
        Allele counts array.
    fill : float
        Use this value where there are no pairs to compare (e.g.,
        all allele calls are missing).

    Returns
    -------

    mpd : ndarray, float, shape (n_variants,)

    Notes
    -----

    The values returned by this function can be summed over a genome
    region and divided by the number of accessible bases to estimate
    nucleotide diversity, a.k.a. *pi*.

    Examples
    --------

    >>> import allel
    >>> h = allel.model.HaplotypeArray([[0, 0, 0, 0],
    ...                                 [0, 0, 0, 1],
    ...                                 [0, 0, 1, 1],
    ...                                 [0, 1, 1, 1],
    ...                                 [1, 1, 1, 1],
    ...                                 [0, 0, 1, 2],
    ...                                 [0, 1, 1, 2],
    ...                                 [0, 1, -1, -1]])
    >>> ac = h.count_alleles()
    >>> allel.stats.mean_pairwise_diversity(ac)
    array([ 0.        ,  0.5       ,  0.66666667,  0.5       ,  0.        ,
            0.83333333,  0.83333333,  1.        ])

    See Also
    --------

    windowed_diversity

    """

    # This function calculates the mean number of pairwise differences
    # between haplotypes within a single population, generalising to any number
    # of alleles.

    # check inputs
    ac = asarray_ndim(ac, 2)

    # total number of haplotypes
    n = np.sum(ac, axis=1)

    # total number of pairwise comparisons for each variant:
    # (an choose 2)
    n_pairs = n * (n - 1) / 2

    # number of pairwise comparisons where there is no difference:
    # sum of (ac choose 2) for each allele (i.e., number of ways to
    # choose the same allele twice)
    n_same = np.sum(ac * (ac - 1) / 2, axis=1)

    # number of pairwise differences
    n_diff = n_pairs - n_same

    # mean number of pairwise differences, accounting for cases where
    # there are no pairs
    with ignore_invalid():
        mpd = np.where(n_pairs > 0, n_diff / n_pairs, fill)

    return mpd


def _resize_dim2(a, l):
    newshape = a.shape[0], l
    b = np.zeros(newshape, dtype=a.dtype)
    b[:, :a.shape[1]] = a
    return b


def mean_pairwise_divergence(ac1, ac2, fill=np.nan):
    """Calculate for each variant the mean number of pairwise differences
    between haplotypes from two different populations.

    Parameters
    ----------

    ac1 : array_like, int, shape (n_variants, n_alleles)
        Allele counts array from the first population.
    ac2 : array_like, int, shape (n_variants, n_alleles)
        Allele counts array from the second population.
    fill : float
        Use this value where there are no pairs to compare (e.g.,
        all allele calls are missing).

    Returns
    -------

    mpd : ndarray, float, shape (n_variants,)

    Notes
    -----

    The values returned by this function can be summed over a genome
    region and divided by the number of accessible bases to estimate
    nucleotide divergence between two populations, a.k.a. *Dxy*.

    Examples
    --------

    >>> import allel
    >>> h = allel.model.HaplotypeArray([[0, 0, 0, 0],
    ...                                 [0, 0, 0, 1],
    ...                                 [0, 0, 1, 1],
    ...                                 [0, 1, 1, 1],
    ...                                 [1, 1, 1, 1],
    ...                                 [0, 0, 1, 2],
    ...                                 [0, 1, 1, 2],
    ...                                 [0, 1, -1, -1]])
    >>> ac1 = h.take([0, 1], axis=1).count_alleles()
    >>> ac2 = h.take([2, 3], axis=1).count_alleles()
    >>> allel.stats.mean_pairwise_divergence(ac1, ac2)
    array([ 0.  ,  0.5 ,  1.  ,  0.5 ,  0.  ,  1.  ,  0.75,   nan])

    See Also
    --------

    windowed_divergence

    """

    # This function calculates the mean number of pairwise differences
    # between haplotypes from two different populations, generalising to any
    # number of alleles.

    # check inputs
    ac1 = asarray_ndim(ac1, 2)
    ac2 = asarray_ndim(ac2, 2)
    # check lengths match
    check_arrays_aligned(ac1, ac2)
    # ensure same number of alleles in both pops
    if ac1.shape[1] < ac2.shape[1]:
        ac1 = _resize_dim2(ac1, ac2.shape[1])
    elif ac2.shape[1] < ac1.shape[1]:
        ac2 = _resize_dim2(ac2, ac1.shape[1])

    # total number of haplotypes sampled from each population
    n1 = np.sum(ac1, axis=1)
    n2 = np.sum(ac2, axis=1)

    # total number of pairwise comparisons for each variant
    n_pairs = n1 * n2

    # number of pairwise comparisons where there is no difference:
    # sum of (ac1 * ac2) for each allele (i.e., number of ways to
    # choose the same allele twice)
    n_same = np.sum(ac1 * ac2, axis=1)

    # number of pairwise differences
    n_diff = n_pairs - n_same

    # mean number of pairwise differences, accounting for cases where
    # there are no pairs
    with ignore_invalid():
        mpd = np.where(n_pairs > 0, n_diff / n_pairs, fill)

    return mpd


def windowed_diversity(pos, ac, size, start=None, stop=None, step=None,
                       windows=None, is_accessible=None, fill=np.nan):
    """Calculate nucleotide diversity in windows over a single
    chromosome/contig.

    Parameters
    ----------

    pos : array_like, int, shape (n_items,)
        Variant positions, using 1-based coordinates, in ascending order.
    ac : array_like, int, shape (n_variants, n_alleles)
        Allele counts array.
    size : int
        The window size (number of bases).
    start : int, optional
        The position at which to start (1-based).
    stop : int, optional
        The position at which to stop (1-based).
    step : int, optional
        The distance between start positions of windows. If not given,
        defaults to the window size, i.e., non-overlapping windows.
    windows : array_like, int, shape (n_windows, 2), optional
        Manually specify the windows to use as a sequence of (window_start,
        window_stop) positions, using 1-based coordinates. Overrides the
        size/start/stop/step parameters.
    is_accessible : array_like, bool, shape (len(contig),), optional
        Boolean array indicating accessibility status for all positions in the
        chromosome/contig.
    fill : object, optional
        The value to use where a window is empty, i.e., contains no items.

    Returns
    -------

    pi : ndarray, float, shape (n_windows,)
        Nucleotide diversity in each window.
    windows : ndarray, int, shape (n_windows, 2)
        The windows used, as an array of (window_start, window_stop) positions,
        using 1-based coordinates.
    n_bases : ndarray, int, shape (n_windows,)
        Number of (accessible) bases in each window.
    counts : ndarray, int, shape (n_windows,)
        Number of variants in each window.

    Examples
    --------

    >>> import allel
    >>> g = allel.model.GenotypeArray([[[0, 0], [0, 0]],
    ...                                [[0, 0], [0, 1]],
    ...                                [[0, 0], [1, 1]],
    ...                                [[0, 1], [1, 1]],
    ...                                [[1, 1], [1, 1]],
    ...                                [[0, 0], [1, 2]],
    ...                                [[0, 1], [1, 2]],
    ...                                [[0, 1], [-1, -1]],
    ...                                [[-1, -1], [-1, -1]]])
    >>> ac = g.count_alleles()
    >>> pos = [2, 4, 7, 14, 15, 18, 19, 25, 27]
    >>> pi, windows, n_bases, counts = allel.stats.windowed_diversity(
    ...     pos, ac, size=10, start=1, stop=31
    ... )
    >>> pi
    array([ 0.11666667,  0.21666667,  0.09090909])
    >>> windows
    array([[ 1, 10],
           [11, 20],
           [21, 31]])
    >>> n_bases
    array([10, 10, 11])
    >>> counts
    array([3, 4, 2])

    """

    # check inputs
    pos = SortedIndex(pos, copy=False)
    is_accessible = asarray_ndim(is_accessible, 1, allow_none=True)

    # calculate mean pairwise diversity
    mpd = mean_pairwise_diversity(ac, fill=0)

    # sum in windows
    mpd_sum, windows, counts = windowed_statistic(
        pos, values=mpd, statistic=np.sum, size=size, start=start, stop=stop,
        step=step, windows=windows, fill=0
    )

    # calculate value per base
    pi, n_bases = per_base(mpd_sum, windows, is_accessible=is_accessible,
                           fill=fill)

    return pi, windows, n_bases, counts


def windowed_divergence(pos, ac1, ac2, size, start=None, stop=None, step=None,
                        is_accessible=None, fill=np.nan):
    """Calculate nucleotide divergence between two populations in windows
    over a single chromosome/contig.

    Parameters
    ----------

    pos : array_like, int, shape (n_items,)
        Variant positions, using 1-based coordinates, in ascending order.
    ac1 : array_like, int, shape (n_variants, n_alleles)
        Allele counts array for the first population.
    ac2 : array_like, int, shape (n_variants, n_alleles)
        Allele counts array for the second population.
    size : int
        The window size (number of bases).
    start : int, optional
        The position at which to start (1-based).
    stop : int, optional
        The position at which to stop (1-based).
    step : int, optional
        The distance between start positions of windows. If not given,
        defaults to the window size, i.e., non-overlapping windows.
    windows : array_like, int, shape (n_windows, 2), optional
        Manually specify the windows to use as a sequence of (window_start,
        window_stop) positions, using 1-based coordinates. Overrides the
        size/start/stop/step parameters.
    is_accessible : array_like, bool, shape (len(contig),), optional
        Boolean array indicating accessibility status for all positions in the
        chromosome/contig.
    fill : object, optional
        The value to use where a window is empty, i.e., contains no items.

    Returns
    -------

    Dxy : ndarray, float, shape (n_windows,)
        Nucleotide divergence in each window.
    windows : ndarray, int, shape (n_windows, 2)
        The windows used, as an array of (window_start, window_stop) positions,
        using 1-based coordinates.
    n_bases : ndarray, int, shape (n_windows,)
        Number of (accessible) bases in each window.
    counts : ndarray, int, shape (n_windows,)
        Number of variants in each window.

    Examples
    --------

    Simplest case, two haplotypes in each population::

        >>> import allel
        >>> h = allel.model.HaplotypeArray([[0, 0, 0, 0],
        ...                                 [0, 0, 0, 1],
        ...                                 [0, 0, 1, 1],
        ...                                 [0, 1, 1, 1],
        ...                                 [1, 1, 1, 1],
        ...                                 [0, 0, 1, 2],
        ...                                 [0, 1, 1, 2],
        ...                                 [0, 1, -1, -1],
        ...                                 [-1, -1, -1, -1]])
        >>> h1 = h.subset(haplotypes=[0, 1])
        >>> h2 = h.subset(haplotypes=[2, 3])
        >>> ac1 = h1.count_alleles()
        >>> ac2 = h2.count_alleles()
        >>> pos = [2, 4, 7, 14, 15, 18, 19, 25, 27]
        >>> dxy, windows, n_bases, counts = windowed_divergence(
        ...     pos, ac1, ac2, size=10, start=1, stop=31
        ... )
        >>> dxy
        array([ 0.15 ,  0.225,  0.   ])
        >>> windows
        array([[ 1, 10],
               [11, 20],
               [21, 31]])
        >>> n_bases
        array([10, 10, 11])
        >>> counts
        array([3, 4, 2])

    """

    # check inputs
    pos = SortedIndex(pos, copy=False)
    is_accessible = asarray_ndim(is_accessible, 1, allow_none=True)

    # calculate mean pairwise divergence
    mpd = mean_pairwise_divergence(ac1, ac2, fill=0)

    # sum in windows
    mpd_sum, windows, counts = windowed_statistic(
        pos, values=mpd, statistic=np.sum, size=size, start=start,
        stop=stop, step=step, fill=0
    )

    # calculate value per base
    dxy, n_bases = per_base(mpd_sum, windows, is_accessible=is_accessible,
                            fill=fill)

    return dxy, windows, n_bases, counts


def heterozygosity_observed(g, fill=np.nan):
    """Calculate the rate of observed heterozygosity for each variant.

    Parameters
    ----------

    g : array_like, int, shape (n_variants, n_samples, ploidy)
        Genotype array.
    fill : float, optional
        Use this value for variants where all calls are missing.

    Returns
    -------

    ho : ndarray, float, shape (n_variants,)
        Observed heterozygosity

    Examples
    --------

    >>> import allel
    >>> g = allel.model.GenotypeArray([[[0, 0], [0, 0], [0, 0]],
    ...                                [[0, 0], [0, 1], [1, 1]],
    ...                                [[0, 0], [1, 1], [2, 2]],
    ...                                [[1, 1], [1, 2], [-1, -1]]])
    >>> allel.stats.heterozygosity_observed(g)
    array([ 0.        ,  0.33333333,  0.        ,  0.5       ])

    """

    # check inputs
    if not hasattr(g, 'count_het') or not hasattr(g, 'count_called'):
        g = GenotypeArray(g, copy=False)

    # count hets
    n_het = np.asarray(g.count_het(axis=1))
    n_called = np.asarray(g.count_called(axis=1))

    # calculate rate of observed heterozygosity, accounting for variants
    # where all calls are missing
    with ignore_invalid():
        ho = np.where(n_called > 0, n_het / n_called, fill)

    return ho


def heterozygosity_expected(af, ploidy, fill=np.nan):
    """Calculate the expected rate of heterozygosity for each variant
    under Hardy-Weinberg equilibrium.

    Parameters
    ----------

    af : array_like, float, shape (n_variants, n_alleles)
        Allele frequencies array.
    fill : float, optional
        Use this value for variants where allele frequencies do not sum to 1.

    Returns
    -------

    he : ndarray, float, shape (n_variants,)
        Expected heterozygosity

    Examples
    --------

    >>> import allel
    >>> g = allel.model.GenotypeArray([[[0, 0], [0, 0], [0, 0]],
    ...                                [[0, 0], [0, 1], [1, 1]],
    ...                                [[0, 0], [1, 1], [2, 2]],
    ...                                [[1, 1], [1, 2], [-1, -1]]])
    >>> af = g.count_alleles().to_frequencies()
    >>> allel.stats.heterozygosity_expected(af, ploidy=2)
    array([ 0.        ,  0.5       ,  0.66666667,  0.375     ])

    """

    # check inputs
    af = asarray_ndim(af, 2)

    # calculate expected heterozygosity
    out = 1 - np.sum(np.power(af, ploidy), axis=1)

    # fill values where allele frequencies could not be calculated
    af_sum = np.sum(af, axis=1)
    with ignore_invalid():
        out[(af_sum < 1) | np.isnan(af_sum)] = fill

    return out


def inbreeding_coefficient(g, fill=np.nan):
    """Calculate the inbreeding coefficient for each variant.

    Parameters
    ----------

    g : array_like, int, shape (n_variants, n_samples, ploidy)
        Genotype array.
    fill : float, optional
        Use this value for variants where the expected heterozygosity is
        zero.

    Returns
    -------

    f : ndarray, float, shape (n_variants,)
        Inbreeding coefficient.

    Notes
    -----

    The inbreeding coefficient is calculated as *1 - (Ho/He)* where *Ho* is
    the observed heterozygosity and *He* is the expected heterozygosity.

    Examples
    --------

    >>> import allel
    >>> g = allel.model.GenotypeArray([[[0, 0], [0, 0], [0, 0]],
    ...                                [[0, 0], [0, 1], [1, 1]],
    ...                                [[0, 0], [1, 1], [2, 2]],
    ...                                [[1, 1], [1, 2], [-1, -1]]])
    >>> allel.stats.inbreeding_coefficient(g)
    array([        nan,  0.33333333,  1.        , -0.33333333])

    """

    # check inputs
    if not hasattr(g, 'count_het') or not hasattr(g, 'count_called'):
        g = GenotypeArray(g, copy=False)

    # calculate observed and expected heterozygosity
    ho = heterozygosity_observed(g)
    af = g.count_alleles().to_frequencies()
    he = heterozygosity_expected(af, ploidy=g.shape[-1], fill=0)

    # calculate inbreeding coefficient, accounting for variants with no
    # expected heterozygosity
    with ignore_invalid():
        f = np.where(he > 0, 1 - (ho / he), fill)

    return f


def pairwise_distance(x, metric):
    """Compute pairwise distance between individuals (samples or haplotypes).

    Parameters
    ----------

    x : array_like, shape (n_variants, n_individuals)
        Array of genotype data.
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
    if x.ndim != 2:
        raise ValueError('expected array with 2 dimensions')

    def f(b):

        # transpose as pdist expects (m, n) for m observations in an
        # n-dimensional space
        t = b.T

        # compute the distance matrix
        return scipy.spatial.distance.pdist(t, metric=metric)

    if hasattr(x, 'chunklen'):
        # use chunk-wise implementation
        bs = x.chunklen
        dist = None
        for i in range(0, x.shape[0], bs):
            block = x[i:i+bs]
            if dist is None:
                dist = f(block)
            else:
                dist += f(block)

    else:
        # standard implementation
        dist = f(x)

    return dist
