Data structures
===============

.. automodule:: allel.model

GenotypeArray
-------------

.. autoclass:: GenotypeArray

    .. autoattribute:: n_variants
    .. autoattribute:: n_samples
    .. autoattribute:: ploidy
    .. automethod:: subset
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
    .. automethod:: count_alleles
    .. automethod:: to_haplotypes
    .. automethod:: to_n_alt
    .. automethod:: to_allele_counts
    .. automethod:: to_packed
    .. automethod:: from_packed
    .. automethod:: to_sparse
    .. automethod:: from_sparse
    .. automethod:: to_gt
    .. automethod:: haploidify_samples


HaplotypeArray
--------------

.. autoclass:: HaplotypeArray

    .. autoattribute:: n_variants
    .. autoattribute:: n_haplotypes
    .. automethod:: subset
    .. automethod:: is_called
    .. automethod:: is_missing
    .. automethod:: is_ref
    .. automethod:: is_alt
    .. automethod:: is_call
    .. automethod:: count_called
    .. automethod:: count_missing
    .. automethod:: count_ref
    .. automethod:: count_alt
    .. automethod:: count_call
    .. automethod:: count_alleles
    .. automethod:: to_genotypes
    .. automethod:: to_sparse
    .. automethod:: from_sparse

AlleleCountsArray
-----------------

.. autoclass:: AlleleCountsArray

    .. autoattribute:: n_variants
    .. autoattribute:: n_alleles
    .. automethod:: allelism
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
    .. automethod:: to_frequencies

SortedIndex
-----------

.. autoclass:: SortedIndex

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


UniqueIndex
-----------

.. autoclass:: UniqueIndex

    .. automethod:: locate_key
    .. automethod:: locate_keys
    .. automethod:: locate_intersection
    .. automethod:: intersect

SortedMultiIndex
----------------

.. autoclass:: SortedMultiIndex

    .. automethod:: locate_key
    .. automethod:: locate_range

VariantTable
------------

.. autoclass:: VariantTable

    .. autoattribute:: n_variants
    .. autoattribute:: names
    .. automethod:: eval
    .. automethod:: query
    .. automethod:: to_vcf
