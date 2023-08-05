Data structures
===============

.. automodule:: allel.model

GenotypeArray
-------------

.. autoclass:: GenotypeArray(data)

    .. autoattribute:: n_variants
    .. autoattribute:: n_samples
    .. autoattribute:: ploidy
    .. automethod:: is_called
    .. automethod:: is_missing
    .. automethod:: is_hom
    .. automethod:: is_hom_ref
    .. automethod:: is_hom_alt
    .. automethod:: is_het
    .. automethod:: is_call
    .. automethod:: count_called
    .. automethod:: count_missing
    .. automethod:: count_hom
    .. automethod:: count_hom_ref
    .. automethod:: count_hom_alt
    .. automethod:: count_het
    .. automethod:: count_call
    .. automethod:: view_haplotypes
    .. automethod:: to_n_alt
    .. automethod:: to_allele_counts
    .. automethod:: to_packed
    .. automethod:: from_packed
    .. automethod:: to_sparse
    .. automethod:: from_sparse
    .. automethod:: allelism
    .. automethod:: allele_number
    .. automethod:: allele_count
    .. automethod:: allele_frequency
    .. automethod:: allele_counts
    .. automethod:: allele_frequencies
    .. automethod:: is_variant
    .. automethod:: is_non_variant
    .. automethod:: is_segregating
    .. automethod:: is_non_segregating
    .. automethod:: is_singleton
    .. automethod:: is_doubleton
    .. automethod:: count_variant
    .. automethod:: count_non_variant
    .. automethod:: count_segregating
    .. automethod:: count_non_segregating
    .. automethod:: count_singleton
    .. automethod:: count_doubleton
    .. automethod:: haploidify_samples
    .. automethod:: heterozygosity_observed
    .. automethod:: heterozygosity_expected
    .. automethod:: inbreeding_coefficient
    .. automethod:: mean_pairwise_difference


HaplotypeArray
--------------

.. autoclass:: HaplotypeArray(data)

    .. autoattribute:: n_variants
    .. autoattribute:: n_haplotypes
    .. automethod:: view_genotypes
    .. automethod:: to_sparse
    .. automethod:: from_sparse
    .. automethod:: allelism
    .. automethod:: allele_number
    .. automethod:: allele_count
    .. automethod:: allele_frequency
    .. automethod:: allele_counts
    .. automethod:: allele_frequencies
    .. automethod:: is_variant
    .. automethod:: is_non_variant
    .. automethod:: is_segregating
    .. automethod:: is_non_segregating
    .. automethod:: is_singleton
    .. automethod:: is_doubleton
    .. automethod:: count_variant
    .. automethod:: count_non_variant
    .. automethod:: count_segregating
    .. automethod:: count_non_segregating
    .. automethod:: count_singleton
    .. automethod:: count_doubleton
    .. automethod:: mean_pairwise_difference

PositionIndex
-------------

.. autoclass:: PositionIndex(data)

    .. autoattribute:: is_unique
    .. automethod:: locate_key
    .. automethod:: locate_keys
    .. automethod:: locate_intersection
    .. automethod:: intersect
    .. automethod:: locate_range
    .. automethod:: intersect_range
    .. automethod:: locate_ranges
    .. automethod:: locate_intersection_ranges
    .. automethod:: intersect_ranges


LabelIndex
----------

.. autoclass:: LabelIndex(data)

    .. automethod:: locate_key
    .. automethod:: locate_keys
    .. automethod:: locate_intersection
    .. automethod:: intersect
