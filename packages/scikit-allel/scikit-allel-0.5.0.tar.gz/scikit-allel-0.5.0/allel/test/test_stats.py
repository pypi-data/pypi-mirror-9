# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division


import unittest


import numpy as np
from allel.test.tools import assert_array_equal as aeq, assert_array_close


from allel.util import ignore_invalid
from allel.model import GenotypeArray, HaplotypeArray, SortedIndex
from allel.stats import moving_statistic, windowed_statistic, \
    mean_pairwise_diversity, mean_pairwise_divergence, windowed_diversity, \
    windowed_divergence, per_base, heterozygosity_observed, \
    heterozygosity_expected, inbreeding_coefficient


class TestWindowUtilities(unittest.TestCase):

    def test_moving_statistic(self):
        f = moving_statistic

        values = [2, 5, 8, 16]
        expect = [7, 24]
        actual = f(values, statistic=np.sum, size=2)
        aeq(expect, actual)

        values = [2, 5, 8, 16]
        expect = [7, 13, 24]
        actual = f(values, statistic=np.sum, size=2, step=1)
        aeq(expect, actual)

    def test_windowed_statistic(self):
        f = windowed_statistic
        pos = [1, 12, 15, 27]

        # boolean array, all true
        b = [True, True, True, True]
        expected_nnz = [1, 2, 1]
        expected_windows = [[1, 10], [11, 20], [21, 27]]
        expected_counts = [1, 2, 1]
        actual_nnz, actual_windows, actual_counts = \
            f(pos, b, np.count_nonzero, 10)
        aeq(expected_nnz, actual_nnz)
        aeq(expected_windows, actual_windows)
        aeq(expected_counts, actual_counts)

        # boolean array, not all true
        b = [False, True, False, True]
        expected_nnz = [0, 1, 1]
        expected_windows = [[1, 10], [11, 20], [21, 27]]
        expected_counts = [1, 2, 1]
        actual_nnz, actual_windows, actual_counts = \
            f(pos, b, np.count_nonzero, 10)
        aeq(expected_windows, actual_windows)
        aeq(expected_nnz, actual_nnz)
        aeq(expected_counts, actual_counts)

        # explicit start and stop
        b = [False, True, False, True]
        expected_nnz = [1, 0, 1]
        expected_windows = [[5, 14], [15, 24], [25, 29]]
        expected_counts = [1, 1, 1]
        actual_nnz, actual_windows, actual_counts = \
            f(pos, b, np.count_nonzero, 10, start=5, stop=29)
        aeq(expected_windows, actual_windows)
        aeq(expected_nnz, actual_nnz)
        aeq(expected_counts, actual_counts)

        # boolean array, bad length
        b = [False, True, False]
        with self.assertRaises(ValueError):
            f(pos, b, np.count_nonzero, 10)

        # 2D, 4 variants, 2 samples
        b = [[True, False],
             [True, True],
             [True, False],
             [True, True]]
        expected_nnz = [[1, 0],
                        [2, 1],
                        [1, 1]]
        expected_windows = [[1, 10], [11, 20], [21, 27]]
        expected_counts = [1, 2, 1]
        actual_nnz, actual_windows, actual_counts = \
            f(pos, b, statistic=lambda x: np.sum(x, axis=0), size=10)
        aeq(expected_nnz, actual_nnz)
        aeq(expected_windows, actual_windows)
        aeq(expected_counts, actual_counts)

    def test_per_base(self):
        pos = [1, 12, 15, 27]

        # boolean array, all true
        b = [True, True, True, True]
        # N.B., final bin includes right edge
        expected_nnz = [1, 2, 1]
        expected_windows = [[1, 10], [11, 20], [21, 27]]
        expected_counts = [1, 2, 1]
        expected_densities = [1/10, 2/10, 1/7]
        expected_n_bases = [10, 10, 7]
        nnz, windows, counts = windowed_statistic(pos, b,
                                                  statistic=np.count_nonzero,
                                                  size=10, start=1)
        densities, n_bases = per_base(nnz, windows)
        aeq(expected_nnz, nnz)
        aeq(expected_windows, windows)
        aeq(expected_counts, counts)
        aeq(expected_densities, densities)
        aeq(expected_n_bases, n_bases)

        # boolean array, not all true
        b = [False, True, False, True]
        expected_densities = [0/10, 1/10, 1/7]
        expected_n_bases = [10, 10, 7]
        nnz, windows, counts = windowed_statistic(pos, b,
                                                  statistic=np.count_nonzero,
                                                  size=10, start=1)
        densities, n_bases = per_base(nnz, windows)
        aeq(expected_densities, densities)
        aeq(expected_n_bases, n_bases)

        # 2D, 4 variants, 2 samples
        b = [[True, False],
             [True, True],
             [True, False],
             [True, True]]
        expected_densities = [[1/10, 0/10],
                              [2/10, 1/10],
                              [1/7, 1/7]]
        expected_n_bases = [10, 10, 7]
        nnz, windows, counts = windowed_statistic(
            pos, b, statistic=lambda x: np.sum(x, axis=0), size=10, start=1
        )
        densities, n_bases = per_base(nnz, windows)
        aeq(expected_densities, densities)
        aeq(expected_n_bases, n_bases)

        # include is_accessible array option
        is_accessible = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  1, 1, 1, 1, 0, 0, 1, 1, 0, 0,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=bool)
        b = [False, True, False, True]
        expected_densities = [-1, 1/6, 1/7]
        expected_n_bases = [0, 6, 7]
        nnz, windows, counts = windowed_statistic(pos, b,
                                                  statistic=np.count_nonzero,
                                                  size=10, start=1)
        densities, n_bases = per_base(nnz, windows,
                                      is_accessible=is_accessible,
                                      fill=-1)
        aeq(expected_densities, densities)
        aeq(expected_n_bases, n_bases)


class TestDiversityDivergence(unittest.TestCase):

    def test_mean_pairwise_diversity(self):

        # start with simplest case, two haplotypes, one pairwise comparison
        h = HaplotypeArray([[0, 0],
                            [1, 1],
                            [0, 1],
                            [1, 2],
                            [0, -1],
                            [-1, -1]])
        ac = h.count_alleles()
        expect = [0, 0, 1, 1, -1, -1]
        actual = mean_pairwise_diversity(ac, fill=-1)
        aeq(expect, actual)

        # four haplotypes, 6 pairwise comparison
        h = HaplotypeArray([[0, 0, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1],
                            [0, 1, 1, 1],
                            [1, 1, 1, 1],
                            [0, 0, 1, 2],
                            [0, 1, 1, 2],
                            [0, 1, -1, -1],
                            [-1, -1, -1, -1]])
        ac = h.count_alleles()
        expect = [0, 3/6, 4/6, 3/6, 0, 5/6, 5/6, 1, -1]
        actual = mean_pairwise_diversity(ac, fill=-1)
        assert_array_close(expect, actual)

    def test_windowed_diversity(self):

        # four haplotypes, 6 pairwise comparison
        h = HaplotypeArray([[0, 0, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1],
                            [0, 1, 1, 1],
                            [1, 1, 1, 1],
                            [0, 0, 1, 2],
                            [0, 1, 1, 2],
                            [0, 1, -1, -1],
                            [-1, -1, -1, -1]])
        ac = h.count_alleles()
        # mean pairwise diversity
        # expect = [0, 3/6, 4/6, 3/6, 0, 5/6, 5/6, 1, -1]
        pos = SortedIndex([2, 4, 7, 14, 15, 18, 19, 25, 27])
        expect = [(7/6)/10, (13/6)/10, 1/11]
        actual, _, _, _ = windowed_diversity(pos, ac, size=10, start=1,
                                             stop=31)
        assert_array_close(expect, actual)

    def test_mean_pairwise_divergence(self):

        # simplest case, two haplotypes in each population
        h = HaplotypeArray([[0, 0, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1],
                            [0, 1, 1, 1],
                            [1, 1, 1, 1],
                            [0, 0, 1, 2],
                            [0, 1, 1, 2],
                            [0, 1, -1, -1],
                            [-1, -1, -1, -1]])
        h1 = h.subset(haplotypes=[0, 1])
        h2 = h.subset(haplotypes=[2, 3])
        ac1 = h1.count_alleles()
        ac2 = h2.count_alleles()

        expect = [0/4, 2/4, 4/4, 2/4, 0/4, 4/4, 3/4, -1, -1]
        actual = mean_pairwise_divergence(ac1, ac2, fill=-1)
        aeq(expect, actual)

    def test_windowed_divergence(self):

        # simplest case, two haplotypes in each population
        h = HaplotypeArray([[0, 0, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 1],
                            [0, 1, 1, 1],
                            [1, 1, 1, 1],
                            [0, 0, 1, 2],
                            [0, 1, 1, 2],
                            [0, 1, -1, -1],
                            [-1, -1, -1, -1]])
        h1 = h.subset(haplotypes=[0, 1])
        h2 = h.subset(haplotypes=[2, 3])
        ac1 = h1.count_alleles()
        ac2 = h2.count_alleles()
        # mean pairwise divergence
        # expect = [0/4, 2/4, 4/4, 2/4, 0/4, 4/4, 3/4, -1, -1]
        pos = SortedIndex([2, 4, 7, 14, 15, 18, 19, 25, 27])
        expect = [(6/4)/10, (9/4)/10, 0/11]
        actual, _, _, _ = windowed_divergence(pos, ac1, ac2, size=10, start=1,
                                              stop=31)
        assert_array_close(expect, actual)


class TestHardyWeinberg(unittest.TestCase):

    def test_heterozygosity_observed(self):

        # diploid
        g = GenotypeArray([[[0, 0], [0, 0]],
                           [[1, 1], [1, 1]],
                           [[1, 1], [2, 2]],
                           [[0, 0], [0, 1]],
                           [[0, 0], [0, 2]],
                           [[1, 1], [1, 2]],
                           [[0, 1], [0, 1]],
                           [[0, 1], [1, 2]],
                           [[0, 0], [-1, -1]],
                           [[0, 1], [-1, -1]],
                           [[-1, -1], [-1, -1]]], dtype='i1')
        expect = [0, 0, 0, .5, .5, .5, 1, 1, 0, 1, -1]
        actual = heterozygosity_observed(g, fill=-1)
        aeq(expect, actual)

        # polyploid
        g = GenotypeArray([[[0, 0, 0], [0, 0, 0]],
                           [[1, 1, 1], [1, 1, 1]],
                           [[1, 1, 1], [2, 2, 2]],
                           [[0, 0, 0], [0, 0, 1]],
                           [[0, 0, 0], [0, 0, 2]],
                           [[1, 1, 1], [0, 1, 2]],
                           [[0, 0, 1], [0, 1, 1]],
                           [[0, 1, 1], [0, 1, 2]],
                           [[0, 0, 0], [-1, -1, -1]],
                           [[0, 0, 1], [-1, -1, -1]],
                           [[-1, -1, -1], [-1, -1, -1]]], dtype='i1')
        expect = [0, 0, 0, .5, .5, .5, 1, 1, 0, 1, -1]
        actual = heterozygosity_observed(g, fill=-1)
        aeq(expect, actual)

    def test_heterozygosity_expected(self):

        def refimpl(af, ploidy, fill=0):
            """Limited reference implementation for testing purposes."""

            # check allele frequencies sum to 1
            af_sum = np.sum(af, axis=1)

            # assume three alleles
            p = af[:, 0]
            q = af[:, 1]
            r = af[:, 2]

            out = 1 - p**ploidy - q**ploidy - r**ploidy
            with ignore_invalid():
                out[(af_sum < 1) | np.isnan(af_sum)] = fill

            return out

        # diploid
        g = GenotypeArray([[[0, 0], [0, 0]],
                           [[1, 1], [1, 1]],
                           [[1, 1], [2, 2]],
                           [[0, 0], [0, 1]],
                           [[0, 0], [0, 2]],
                           [[1, 1], [1, 2]],
                           [[0, 1], [0, 1]],
                           [[0, 1], [1, 2]],
                           [[0, 0], [-1, -1]],
                           [[0, 1], [-1, -1]],
                           [[-1, -1], [-1, -1]]], dtype='i1')
        expect1 = [0, 0, 0.5, .375, .375, .375, .5, .625, 0, .5, -1]
        af = g.count_alleles().to_frequencies()
        expect2 = refimpl(af, ploidy=g.ploidy, fill=-1)
        actual = heterozygosity_expected(af, ploidy=g.ploidy, fill=-1)
        assert_array_close(expect1, actual)
        assert_array_close(expect2, actual)
        expect3 = [0, 0, 0.5, .375, .375, .375, .5, .625, 0, .5, 0]
        actual = heterozygosity_expected(af, ploidy=g.ploidy, fill=0)
        assert_array_close(expect3, actual)

        # polyploid
        g = GenotypeArray([[[0, 0, 0], [0, 0, 0]],
                           [[1, 1, 1], [1, 1, 1]],
                           [[1, 1, 1], [2, 2, 2]],
                           [[0, 0, 0], [0, 0, 1]],
                           [[0, 0, 0], [0, 0, 2]],
                           [[1, 1, 1], [0, 1, 2]],
                           [[0, 0, 1], [0, 1, 1]],
                           [[0, 1, 1], [0, 1, 2]],
                           [[0, 0, 0], [-1, -1, -1]],
                           [[0, 0, 1], [-1, -1, -1]],
                           [[-1, -1, -1], [-1, -1, -1]]], dtype='i1')
        af = g.count_alleles().to_frequencies()
        expect = refimpl(af, ploidy=g.ploidy, fill=-1)
        actual = heterozygosity_expected(af, ploidy=g.ploidy, fill=-1)
        assert_array_close(expect, actual)

    def test_inbreeding_coefficient(self):

        # diploid
        g = GenotypeArray([[[0, 0], [0, 0]],
                           [[1, 1], [1, 1]],
                           [[1, 1], [2, 2]],
                           [[0, 0], [0, 1]],
                           [[0, 0], [0, 2]],
                           [[1, 1], [1, 2]],
                           [[0, 1], [0, 1]],
                           [[0, 1], [1, 2]],
                           [[0, 0], [-1, -1]],
                           [[0, 1], [-1, -1]],
                           [[-1, -1], [-1, -1]]], dtype='i1')
        # ho = np.array([0, 0, 0, .5, .5, .5, 1, 1, 0, 1, -1])
        # he = np.array([0, 0, 0.5, .375, .375, .375, .5, .625, 0, .5, -1])
        # expect = 1 - (ho/he)
        expect = [-1, -1, 1-0, 1-(.5/.375), 1-(.5/.375), 1-(.5/.375),
                  1-(1/.5), 1-(1/.625), -1, 1-(1/.5), -1]
        actual = inbreeding_coefficient(g, fill=-1)
        assert_array_close(expect, actual)
