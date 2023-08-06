# -*- coding: utf-8 -*-
"""
This module provides alternative implementations of array interfaces defined in
the :mod:`allel.model` module, using `bcolz <http://bcolz.blosc.org>`_
compressed arrays (:class:`bcolz.carray`) instead of numpy arrays for data
storage. Compressed arrays can use either main memory or be stored on disk.
In either case, the use of compressed arrays enables analysis of data that
are too large to fit uncompressed into main memory.

"""
from __future__ import absolute_import, print_function, division


import os
import operator
import itertools
from allel.compat import range


import numpy as np
import bcolz


from allel.model import GenotypeArray, HaplotypeArray, AlleleCountsArray, \
    SortedIndex, SortedMultiIndex, subset, VariantTable, \
    sample_to_haplotype_selection, FeatureTable
from allel.constants import DIM_PLOIDY
from allel.util import asarray_ndim
from allel.io import write_vcf_header, write_vcf_data, iter_gff3


__all__ = ['GenotypeCArray', 'HaplotypeCArray', 'AlleleCountsCArray',
           'VariantCTable']


# monkey-patch bcolz.ctable.dtype property because it's broken for
# multi-dimensional columns

def _ctable_dtype(self):
    """The data type of this object (numpy dtype)."""
    names, cols = self.names, self.cols
    l = []
    for name in names:
        col = cols[name]
        if col.ndim == 1:
            t = (name, col.dtype)
        else:
            t = (name, (col.dtype, col.shape[1:]))
        l.append(t)
    return np.dtype(l)

bcolz.ctable.dtype = property(_ctable_dtype)


# bcolz.ctable.addcol is broken for persistent ctables

def ctable_addcol_persistent(self, newcol, name, **kwargs):
    # require name to simplify patch
    if self.rootdir is not None and self.mode != 'r':
        rootdir = os.path.join(self.rootdir, name)
        kwargs['rootdir'] = rootdir
        kwargs['mode'] = 'w'
        self.addcol(newcol, name=name, **kwargs)
        if isinstance(newcol, bcolz.carray):
            # ensure carrays are actually written to disk
            newcol.copy(**kwargs)
    else:
        self.addcol(newcol, name=name, **kwargs)

bcolz.ctable.addcol_persistent = ctable_addcol_persistent


def carray_block_map(carr, f, out=None, blen=None, **kwargs):
    kwargs.setdefault('expectedlen', carr.shape[0])
    if blen is None:
        blen = carr.chunklen
    for i in range(0, carr.shape[0], blen):
        block = carr[i:i+blen]
        res = f(block)
        if out is None:
            out = bcolz.carray(res, **kwargs)
        else:
            out.append(res)
    return out


def carray_block_sum(carr, axis=None, blen=None, transform=None):
    if blen is None:
        blen = carr.chunklen

    if axis is None:
        out = 0
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            if transform:
                block = transform(block)
            out += np.sum(block)
        return out

    elif axis == 0 or axis == (0, 2):
        out = np.zeros((carr.shape[1],), dtype=int)
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            if transform:
                block = transform(block)
            out += np.sum(block, axis=0)
        return out

    elif axis == 1 or axis == (1, 2):
        out = np.zeros((carr.shape[0],), dtype=int)
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            if transform:
                block = transform(block)
            out[i:i+blen] += np.sum(block, axis=1)
        return out

    else:
        raise NotImplementedError('axis not supported: %s' % axis)


def carray_block_max(carr, axis=None, blen=None):
    if blen is None:
        blen = carr.chunklen
    out = None

    if axis is None:
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            m = np.max(block)
            if out is None:
                out = m
            else:
                out = m if m > out else out
        return out

    elif axis == 0 or axis == (0, 2):
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            m = np.max(block, axis=axis)
            if out is None:
                out = m
            else:
                out = np.where(m > out, m, out)
        return out

    elif axis == 1 or axis == (1, 2):
        out = np.zeros((carr.shape[0],), dtype=int)
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            out[i:i+blen] = np.max(block, axis=axis)
        return out

    else:
        raise NotImplementedError('axis not supported: %s' % axis)


def carray_block_min(carr, axis=None, blen=None):
    if blen is None:
        blen = carr.chunklen
    out = None

    if axis is None:
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            m = np.min(block)
            if out is None:
                out = m
            else:
                out = m if m < out else out
        return out

    elif axis == 0 or axis == (0, 2):
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            m = np.min(block, axis=axis)
            if out is None:
                out = m
            else:
                out = np.where(m < out, m, out)
        return out

    elif axis == 1 or axis == (1, 2):
        out = np.zeros((carr.shape[0],), dtype=int)
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            out[i:i+blen] = np.min(block, axis=axis)
        return out

    else:
        raise NotImplementedError('axis not supported: %s' % axis)


def carray_block_compress(carr, condition, axis, blen=None, **kwargs):
    if blen is None:
        blen = carr.chunklen

    # check inputs
    condition = asarray_ndim(condition, 1)

    if axis == 0:
        if condition.size != carr.shape[0]:
            raise ValueError('length of condition must match length of '
                             'first dimension; expected %s, found %s' %
                             (carr.shape[0], condition.size))

        # setup output
        kwargs.setdefault('dtype', carr.dtype)
        kwargs.setdefault('expectedlen', np.count_nonzero(condition))
        out = bcolz.zeros((0,) + carr.shape[1:], **kwargs)

        # build output
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            bcond = condition[i:i+blen]
            out.append(np.compress(bcond, block, axis=0))

        return out

    elif axis == 1:
        if condition.size != carr.shape[1]:
            raise ValueError('length of condition must match length of '
                             'second dimension; expected %s, found %s' %
                             (carr.shape[1], condition.size))

        # setup output
        kwargs.setdefault('dtype', carr.dtype)
        kwargs.setdefault('expectedlen', carr.shape[0])
        out = bcolz.zeros((0, np.count_nonzero(condition)) + carr.shape[2:],
                          **kwargs)

        # build output
        for i in range(0, carr.shape[0], blen):
            block = carr[i:i+blen]
            out.append(np.compress(condition, block, axis=1))

        return out

    else:
        raise NotImplementedError('axis not supported: %s' % axis)


def carray_block_take(carr, indices, axis, **kwargs):

    # check inputs
    indices = asarray_ndim(indices, 1)

    if axis == 0:
        condition = np.zeros((carr.shape[0],), dtype=bool)
        condition[indices] = True
        return carray_block_compress(carr, condition, axis=0, **kwargs)

    elif axis == 1:
        condition = np.zeros((carr.shape[1],), dtype=bool)
        condition[indices] = True
        return carray_block_compress(carr, condition, axis=1, **kwargs)

    else:
        raise NotImplementedError('axis not supported: %s' % axis)


def ctable_block_compress(ctbl, condition, blen=None, **kwargs):
    if blen is None:
        blen = min(ctbl[col].chunklen for col in ctbl.cols)

    # check inputs
    condition = asarray_ndim(condition, 1)

    if condition.size != ctbl.shape[0]:
        raise ValueError('length of condition must match length of '
                         'table; expected %s, found %s' %
                         (ctbl.shape[0], condition.size))

    # setup output
    kwargs.setdefault('expectedlen', np.count_nonzero(condition))
    out = None

    # build output
    for i in range(0, ctbl.shape[0], blen):
        block = ctbl[i:i+blen]
        bcond = condition[i:i+blen]
        res = np.compress(bcond, block, axis=0)
        if out is None:
            out = bcolz.ctable(res, **kwargs)
        else:
            out.append(res)

    return out


def ctable_block_take(ctbl, indices, **kwargs):
    indices = asarray_ndim(indices, 1)
    condition = np.zeros((ctbl.shape[0],), dtype=bool)
    condition[indices] = True
    return ctable_block_compress(ctbl, condition, **kwargs)


def carray_block_subset(carr, sel0=None, sel1=None, blen=None, **kwargs):
    if blen is None:
        blen = carr.chunklen

    # check inputs
    sel0 = asarray_ndim(sel0, 1, allow_none=True)
    sel1 = asarray_ndim(sel1, 1, allow_none=True)
    if sel0 is None and sel1 is None:
        raise ValueError('missing selection')

    # if either selection is None, use take/compress
    if sel1 is None:
        if sel0.size < carr.shape[0]:
            return carray_block_take(carr, sel0, axis=0, **kwargs)
        else:
            return carray_block_compress(carr, sel0, axis=0, **kwargs)
    elif sel0 is None:
        if sel1.size < carr.shape[1]:
            return carray_block_take(carr, sel1, axis=1, **kwargs)
        else:
            return carray_block_compress(carr, sel1, axis=1, **kwargs)

    # ensure boolean array for dim 0
    if sel0.size < carr.shape[0]:
        tmp = np.zeros((carr.shape[0],), dtype=bool)
        tmp[sel0] = True
        sel0 = tmp

    # ensure indices for dim 1
    if sel1.size == carr.shape[1]:
        sel1 = np.nonzero(sel1)[0]

    # setup output
    kwargs.setdefault('dtype', carr.dtype)
    kwargs.setdefault('expectedlen', np.count_nonzero(sel0))
    out = bcolz.zeros((0, sel1.size) + carr.shape[2:], **kwargs)

    # build output
    for i in range(0, carr.shape[0], blen):
        block = carr[i:i+blen]
        bsel0 = sel0[i:i+blen]
        out.append(subset(block, bsel0, sel1))

    return out


def carray_from_hdf5(*args, **kwargs):
    """Load a bcolz carray from an HDF5 dataset.

    Either provide an h5py dataset as a single positional argument,
    or provide two positional arguments giving the HDF5 file path and the
    dataset node path within the file.

    All keyword arguments are passed through to the bcolz.carray constructor.

    """

    import h5py

    h5f = None

    if len(args) == 1:
        dataset = args[0]

    elif len(args) == 2:
        file_path, node_path = args
        h5f = h5py.File(file_path, mode='r')
        try:
            dataset = h5f[node_path]
        except:
            h5f.close()
            raise

    else:
        raise ValueError('bad arguments; expected dataset or (file_path, '
                         'node_path), found %s' % repr(args))

    try:

        if not isinstance(dataset, h5py.Dataset):
            raise ValueError('expected dataset, found %r' % dataset)

        length = dataset.shape[0]
        start = kwargs.pop('start', 0)
        stop = kwargs.pop('stop', length)
        step = kwargs.pop('step', 1)
        condition = kwargs.pop('condition', None)
        condition = asarray_ndim(condition, 1, allow_none=True)
        blen = kwargs.pop('blen', None)

        # setup output data
        if condition is None:
            expectedlen = (stop - start) // step
        else:
            if condition.size != length:
                raise ValueError('length of condition does not match length '
                                 'of dataset')
            expectedlen = np.count_nonzero(condition[start:stop:step])
        kwargs.setdefault('expectedlen', expectedlen)
        kwargs.setdefault('dtype', dataset.dtype)
        carr = bcolz.zeros((0,) + dataset.shape[1:], **kwargs)

        # determine block size
        if blen is None:
            if hasattr(dataset, 'chunks'):
                # use input chunk length
                blen = dataset.chunks[0]
            else:
                # use output chunk length
                blen = carr.chunklen

        # load block-wise
        for i in range(start, stop, blen):
            j = min(i + blen, stop)
            # N.B., apply step after load because step within h5py is slooow
            block = dataset[i:j][::step]
            if condition is not None:
                bcnd = condition[i:j:step]
                block = np.compress(bcnd, block, axis=0)
            carr.append(block)

        return carr

    finally:
        if h5f is not None:
            h5f.close()


def carray_to_hdf5(carr, parent, name, **kwargs):
    """Write a bcolz carray to an HDF5 dataset.

    Parameters
    ----------

    carr : bcolz.carray
        Data to write.
    parent : string or h5py group
        Parent HDF5 file or group. If a string, will be treated as HDF5 file
        name.
    name : string
        Name or path of dataset to write data into.
    kwargs : keyword arguments
        Passed through to h5py require_dataset() function.

    Returns
    -------

    h5d : h5py dataset

    """

    import h5py

    h5f = None

    if isinstance(parent, str):
        h5f = h5py.File(parent, mode='a')
        parent = h5f

    try:

        kwargs.setdefault('chunks', True)  # auto-chunking
        kwargs.setdefault('dtype', carr.dtype)
        kwargs.setdefault('compression', 'gzip')
        h5d = parent.require_dataset(name, shape=carr.shape, **kwargs)

        blen = carr.chunklen
        for i in range(0, carr.shape[0], blen):
            h5d[i:i+blen] = carr[i:i+blen]

        return h5d

    finally:
        if h5f is not None:
            h5f.close()


def ctable_from_hdf5_group(*args, **kwargs):
    """Load a bcolz ctable from columns stored as separate datasets with an
    HDF5 group.

    Either provide an h5py group as a single positional argument,
    or provide two positional arguments giving the HDF5 file path and the
    group node path within the file.

    All keyword arguments are passed through to the bcolz.ctable constructor.

    """

    import h5py

    h5f = None

    if len(args) == 1:
        group = args[0]

    elif len(args) == 2:
        file_path, node_path = args
        h5f = h5py.File(file_path, mode='r')
        try:
            group = h5f[node_path]
        except:
            h5f.close()
            raise

    else:
        raise ValueError('bad arguments; expected group or (file_path, '
                         'node_path), found %s' % repr(args))

    try:

        if not isinstance(group, h5py.Group):
            raise ValueError('expected group, found %r' % group)

        # determine dataset names to load
        available_dataset_names = [n for n in group.keys()
                                   if isinstance(group[n], h5py.Dataset)]
        names = kwargs.pop('names', available_dataset_names)
        for n in names:
            if n not in set(group.keys()):
                raise ValueError('name not found: %s' % n)
            if not isinstance(group[n], h5py.Dataset):
                raise ValueError('name does not refer to a dataset: %s, %r'
                                 % (n, group[n]))

        # check datasets are aligned
        datasets = [group[n] for n in names]
        length = datasets[0].shape[0]
        for d in datasets[1:]:
            if d.shape[0] != length:
                raise ValueError('datasets must be of equal length')

        # determine start and stop parameters for load
        start = kwargs.pop('start', 0)
        stop = kwargs.pop('stop', length)
        step = kwargs.pop('step', 1)
        blen = kwargs.pop('blen', None)
        condition = kwargs.pop('condition', None)
        condition = asarray_ndim(condition, 1, allow_none=True)

        # setup output data
        if condition is None:
            expectedlen = (stop - start) // step
        else:
            if condition.size != length:
                raise ValueError('length of condition does not match length '
                                 'of datasets')
            expectedlen = np.count_nonzero(condition[start:stop:step])
        kwargs.setdefault('expectedlen', expectedlen)
        if blen is None:
            # use smallest input chunk length
            blen = min([d.chunks[0] for d in datasets if hasattr(d, 'chunks')])
        ctbl = None

        # load block-wise
        for i in range(start, stop, blen):
            j = min(i + blen, stop)
            # N.B., apply step after load because step within h5py is slooow
            blocks = [d[i:j][::step] for d in datasets]
            if condition is not None:
                bcnd = condition[i:j:step]
                blocks = [np.compress(bcnd, block, axis=0) for block in blocks]
            if ctbl is None:
                ctbl = bcolz.ctable(blocks, names=names, **kwargs)
            else:
                ctbl.append(blocks)

        return ctbl

    finally:
        if h5f is not None:
            h5f.close()


def ctable_to_hdf5_group(ctbl, parent, name, **kwargs):
    """Write each column in a bcolz ctable to a dataset in an HDF5 group.

    Parameters
    ----------

    parent : string or h5py group
        Parent HDF5 file or group. If a string, will be treated as HDF5 file
        name.
    name : string
        Name or path of group to write data into.
    kwargs : keyword arguments
        Passed through to h5py require_dataset() function.

    Returns
    -------

    h5g : h5py group

    """

    import h5py

    h5f = None

    if isinstance(parent, str):
        h5f = h5py.File(parent, mode='a')
        parent = h5f

    try:

        h5g = parent.require_group(name)
        for col in ctbl.cols:
            carray_to_hdf5(ctbl[col], h5g, col, **kwargs)

        return h5g

    finally:
        if h5f is not None:
            h5f.close()


class _CArrayWrapper(object):

    def __setitem__(self, key, value):
        self.carr[key] = value

    def __getattr__(self, item):
        return getattr(self.carr, item)

    def __setattr__(self, key, value):
        setattr(self.carr, key, value)

    def __array__(self):
        return self.carr[:]

    def __repr__(self):
        s = repr(self.carr)
        s = type(self).__name__ + s[6:]
        return s

    def __len__(self):
        return len(self.carr)

    @classmethod
    def open(cls, rootdir, mode='r'):
        cobj = bcolz.open(rootdir, mode=mode)
        if isinstance(cobj, bcolz.carray):
            return cls(cobj, copy=False)
        else:
            raise ValueError('rootdir does not contain a carray')

    def max(self, axis=None):
        return carray_block_max(self.carr, axis=axis)

    def min(self, axis=None):
        return carray_block_min(self.carr, axis=axis)

    def compare_scalar(self, op, other, **kwargs):
        if not np.isscalar(other):
            raise NotImplementedError('only supported for scalars')

        # build output
        def f(block):
            return op(block, other)
        out = carray_block_map(self.carr, f, **kwargs)

        return out

    def __eq__(self, other):
        return self.compare_scalar(operator.eq, other)

    def __ne__(self, other):
        return self.compare_scalar(operator.ne, other)

    def __lt__(self, other):
        return self.compare_scalar(operator.lt, other)

    def __gt__(self, other):
        return self.compare_scalar(operator.gt, other)

    def __le__(self, other):
        return self.compare_scalar(operator.le, other)

    def __ge__(self, other):
        return self.compare_scalar(operator.ge, other)

    @classmethod
    def from_hdf5(cls, *args, **kwargs):
        """Load a bcolz carray from an HDF5 dataset.

        Either provide an h5py dataset as a single positional argument,
        or provide two positional arguments giving the HDF5 file path and the
        dataset node path within the file.

        All keyword arguments are passed through to the bcolz.carray
        constructor.

        """
        carr = carray_from_hdf5(*args, **kwargs)
        return cls(carr, copy=False)

    def to_hdf5(self, parent, name, **kwargs):
        """Write a bcolz carray to an HDF5 dataset.

        Parameters
        ----------

        carr : bcolz.carray
            Data to write.
        parent : string or h5py group
            Parent HDF5 file or group. If a string, will be treated as HDF5
            file name.
        name : string
            Name or path of dataset to write data into.
        kwargs : keyword arguments
            Passed through to h5py require_dataset() function.

        Returns
        -------

        h5d : h5py dataset

        """
        return carray_to_hdf5(self.carr, parent, name, **kwargs)


class GenotypeCArray(_CArrayWrapper):
    """Alternative implementation of the :class:`allel.model.GenotypeArray`
    interface, using a :class:`bcolz.carray` as the backing store.

    Parameters
    ----------

    data : array_like, int, shape (n_variants, n_samples, ploidy), optional
        Data to initialise the array with. May be a bcolz carray, which will
        not be copied if copy=False. May also be None, in which case rootdir
        must be provided (disk-based array).
    copy : bool, optional
        If True, copy the input data into a new bcolz carray.
    **kwargs : keyword arguments
        Passed through to the bcolz carray constructor.

    Examples
    --------

    Instantiate a compressed genotype array from existing data::

        >>> import allel
        >>> g = allel.bcolz.GenotypeCArray([[[0, 0], [0, 1]],
        ...                                 [[0, 1], [1, 1]],
        ...                                 [[0, 2], [-1, -1]]], dtype='i1')
        >>> g
        GenotypeCArray((3, 2, 2), int8)
          nbytes: 12; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[[ 0  0]
          [ 0  1]]
         [[ 0  1]
          [ 1  1]]
         [[ 0  2]
          [-1 -1]]]

    Obtain a numpy ndarray from a compressed array by slicing::

        >>> g[:]
        GenotypeArray((3, 2, 2), dtype=int8)
        [[[ 0  0]
          [ 0  1]]
         [[ 0  1]
          [ 1  1]]
         [[ 0  2]
          [-1 -1]]]

    Build incrementally::

        >>> import bcolz
        >>> data = bcolz.zeros((0, 2, 2), dtype='i1')
        >>> data.append([[0, 0], [0, 1]])
        >>> data.append([[0, 1], [1, 1]])
        >>> data.append([[0, 2], [-1, -1]])
        >>> g = allel.bcolz.GenotypeCArray(data, copy=False)
        >>> g
        GenotypeCArray((3, 2, 2), int8)
          nbytes: 12; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[[ 0  0]
          [ 0  1]]
         [[ 0  1]
          [ 1  1]]
         [[ 0  2]
          [-1 -1]]]

    Load from HDF5::

        >>> import h5py
        >>> with h5py.File('example.h5', mode='w') as h5f:
        ...     h5f.create_dataset('genotype',
        ...                        data=[[[0, 0], [0, 1]],
        ...                              [[0, 1], [1, 1]],
        ...                              [[0, 2], [-1, -1]]],
        ...                        dtype='i1',
        ...                        chunks=(2, 2, 2))
        ...
        <HDF5 dataset "genotype": shape (3, 2, 2), type "|i1">
        >>> g = allel.bcolz.GenotypeCArray.from_hdf5('example.h5', 'genotype')
        >>> g
        GenotypeCArray((3, 2, 2), int8)
          nbytes: 12; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[[ 0  0]
          [ 0  1]]
         [[ 0  1]
          [ 1  1]]
         [[ 0  2]
          [-1 -1]]]

    Note that methods of this class will return bcolz carrays rather than
    numpy ndarrays where possible. E.g.::

        >>> g.take([0, 2], axis=0)
        GenotypeCArray((2, 2, 2), int8)
          nbytes: 8; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[[ 0  0]
          [ 0  1]]
         [[ 0  2]
          [-1 -1]]]
        >>> g.is_called()
        carray((3, 2), bool)
          nbytes: 6; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[ True  True]
         [ True  True]
         [ True False]]
        >>> g.to_haplotypes()
        HaplotypeCArray((3, 4), int8)
          nbytes: 12; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[ 0  0  0  1]
         [ 0  1  1  1]
         [ 0  2 -1 -1]]
        >>> g.count_alleles()
        AlleleCountsCArray((3, 3), int32)
          nbytes: 36; cbytes: 16.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [[3 1 0]
         [1 3 0]
         [1 0 1]]

    """

    @staticmethod
    def check_input_data(obj):

        # check dtype
        if obj.dtype.kind not in 'ui':
            raise TypeError('integer dtype required')

        # check dimensionality
        if hasattr(obj, 'ndim'):
            ndim = obj.ndim
        else:
            ndim = len(obj.shape)
        if ndim != 3:
            raise TypeError('array with 3 dimensions required')

        # check length of ploidy dimension
        if obj.shape[DIM_PLOIDY] == 1:
            raise ValueError('use HaplotypeCArray for haploid calls')

    def __init__(self, data=None, copy=True, **kwargs):
        if copy or not isinstance(data, bcolz.carray):
            carr = bcolz.carray(data, **kwargs)
        else:
            carr = data
        # check late to avoid creating an intermediate numpy array
        self.check_input_data(carr)
        object.__setattr__(self, 'carr', carr)

    def __getitem__(self, *args):
        out = self.carr.__getitem__(*args)
        if hasattr(out, 'ndim') and out.ndim == 3:
            out = GenotypeArray(out, copy=False)
        return out

    @property
    def n_variants(self):
        return self.carr.shape[0]

    @property
    def n_samples(self):
        return self.carr.shape[1]

    @property
    def ploidy(self):
        return self.carr.shape[2]

    def compress(self, condition, axis=0, **kwargs):
        carr = carray_block_compress(self.carr, condition, axis, **kwargs)
        return GenotypeCArray(carr, copy=False)

    def take(self, indices, axis=0, **kwargs):
        carr = carray_block_take(self.carr, indices, axis, **kwargs)
        return GenotypeCArray(carr, copy=False)

    def subset(self, variants=None, samples=None, **kwargs):
        carr = carray_block_subset(self.carr, variants, samples, **kwargs)
        return GenotypeCArray(carr, copy=False)

    def is_called(self, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_called()
        return carray_block_map(self.carr, f, **kwargs)

    def is_missing(self, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_missing()
        return carray_block_map(self.carr, f, **kwargs)

    def is_hom(self, allele=None, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_hom(allele=allele)
        return carray_block_map(self.carr, f, **kwargs)

    def is_hom_ref(self, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_hom_ref()
        return carray_block_map(self.carr, f, **kwargs)

    def is_hom_alt(self, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_hom_alt()
        return carray_block_map(self.carr, f, **kwargs)

    def is_het(self, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_het()
        return carray_block_map(self.carr, f, **kwargs)

    def is_call(self, call, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).is_call(call)
        return carray_block_map(self.carr, f, **kwargs)

    def count_called(self, axis=None):
        def f(block):
            return GenotypeArray(block, copy=False).is_called()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_missing(self, axis=None):
        def f(block):
            return GenotypeArray(block, copy=False).is_missing()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_hom(self, allele=None, axis=None):
        def f(block):
            g = GenotypeArray(block, copy=False)
            return g.is_hom(allele=allele)
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_hom_ref(self, axis=None):
        def f(block):
            return GenotypeArray(block, copy=False).is_hom_ref()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_hom_alt(self, axis=None):
        def f(block):
            return GenotypeArray(block, copy=False).is_hom_alt()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_het(self, axis=None):
        def f(block):
            return GenotypeArray(block, copy=False).is_het()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_call(self, call, axis=None):
        def f(block):
            g = GenotypeArray(block, copy=False)
            return g.is_call(call=call)
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def to_haplotypes(self, **kwargs):
        # Unfortunately this cannot be implemented as a lightweight view,
        # so we have to copy.

        # build output
        def f(block):
            return block.reshape((block.shape[0], -1))
        out = carray_block_map(self.carr, f, **kwargs)
        return HaplotypeCArray(out, copy=False)

    def to_n_alt(self, fill=0, **kwargs):
        def f(block):
            return GenotypeArray(block, copy=False).to_n_alt(fill)
        return carray_block_map(self.carr, f, **kwargs)

    def to_allele_counts(self, alleles=None, **kwargs):

        # determine alleles to count
        if alleles is None:
            m = self.max()
            alleles = list(range(m+1))

        # build output
        def f(block):
            g = GenotypeArray(block, copy=False)
            return g.to_allele_counts(alleles)

        return carray_block_map(self.carr, f, **kwargs)

    def to_packed(self, boundscheck=True, **kwargs):

        if self.ploidy != 2:
            raise ValueError('can only pack diploid calls')

        if boundscheck:
            amx = self.max()
            if amx > 14:
                raise ValueError('max allele for packing is 14, found %s'
                                 % amx)
            amn = self.min()
            if amn < -1:
                raise ValueError('min allele for packing is -1, found %s'
                                 % amn)

        # build output
        def f(block):
            g = GenotypeArray(block, copy=False)
            return g.to_packed(boundscheck=False)

        return carray_block_map(self.carr, f, **kwargs)

    @staticmethod
    def from_packed(packed, **kwargs):

        # check input
        if not isinstance(packed, (np.ndarray, bcolz.carray)):
            packed = np.asarray(packed)

        # set up output
        kwargs.setdefault('dtype', 'i1')
        kwargs.setdefault('expectedlen', packed.shape[0])
        out = bcolz.zeros((0, packed.shape[1], 2), **kwargs)
        blen = out.chunklen

        # build output
        def f(block):
            return GenotypeArray.from_packed(block)
        carray_block_map(packed, f, out=out, blen=blen)

        return GenotypeCArray(out, copy=False)

    def count_alleles(self, max_allele=None, subpop=None, **kwargs):

        # if max_allele not specified, count all alleles
        if max_allele is None:
            max_allele = self.max()

        if subpop is not None:
            # convert to a haplotype selection
            subpop = sample_to_haplotype_selection(subpop, self.ploidy)

        def f(block):
            h = GenotypeArray(block, copy=False).to_haplotypes()
            return h.count_alleles(max_allele=max_allele, subpop=subpop)

        out = carray_block_map(self.carr, f, **kwargs)

        return AlleleCountsCArray(out, copy=False)

    def count_alleles_subpops(self, subpops, max_allele=None, **kwargs):

        # if max_allele not specified, count all alleles
        if max_allele is None:
            max_allele = self.max()

        # convert to haplotype selections
        names = sorted(subpops.keys())
        subpops = [sample_to_haplotype_selection(subpops[n], self.ploidy)
                   for n in names]

        # setup output table
        kwargs['names'] = names  # override to ensure correct order
        kwargs.setdefault('expectedlen', self.shape[0])
        acs_ctbl = None

        # determine block size for iteration
        blen = kwargs.pop('blen', None)
        if blen is None:
            blen = self.carr.chunklen

        # block iteration
        for i in range(0, self.carr.shape[0], blen):
            block = self.carr[i:i+blen]
            h = GenotypeArray(block, copy=False).to_haplotypes()
            cols = [h.count_alleles(max_allele=max_allele, subpop=subpop)
                    for subpop in subpops]
            if acs_ctbl is None:
                acs_ctbl = bcolz.ctable(cols, **kwargs)
            else:
                acs_ctbl.append(cols)

        return AlleleCountsCTable(acs_ctbl)

    def to_gt(self, phased=False, max_allele=None, **kwargs):
        if max_allele is None:
            max_allele = self.max()

        def f(block):
            g = GenotypeArray(block, copy=False)
            return g.to_gt(phased=phased, max_allele=max_allele)
        return carray_block_map(self.carr, f, **kwargs)


class HaplotypeCArray(_CArrayWrapper):
    """Alternative implementation of the :class:`allel.model.HaplotypeArray`
    interface, using a :class:`bcolz.carray` as the backing store.

    Parameters
    ----------

    data : array_like, int, shape (n_variants, n_haplotypes), optional
        Data to initialise the array with. May be a bcolz carray, which will
        not be copied if copy=False. May also be None, in which case rootdir
        must be provided (disk-based array).
    copy : bool, optional
        If True, copy the input data into a new bcolz carray.
    **kwargs : keyword arguments
        Passed through to the bcolz carray constructor.

    """

    @staticmethod
    def check_input_data(obj):

        # check dtype
        if obj.dtype.kind not in 'ui':
            raise TypeError('integer dtype required')

        # check dimensionality
        if hasattr(obj, 'ndim'):
            ndim = obj.ndim
        else:
            ndim = len(obj.shape)
        if ndim != 2:
            raise TypeError('array with 2 dimensions required')

    def __init__(self, data=None, copy=True, **kwargs):
        if copy or not isinstance(data, bcolz.carray):
            carr = bcolz.carray(data, **kwargs)
        else:
            carr = data
        # check late to avoid creating an intermediate numpy array
        self.check_input_data(carr)
        object.__setattr__(self, 'carr', carr)

    def __getitem__(self, *args):
        out = self.carr.__getitem__(*args)
        if hasattr(out, 'ndim') and out.ndim == 2:
            out = HaplotypeArray(out, copy=False)
        return out

    @property
    def n_variants(self):
        """Number of variants (length of first array dimension)."""
        return self.carr.shape[0]

    @property
    def n_haplotypes(self):
        """Number of haplotypes (length of second array dimension)."""
        return self.carr.shape[1]

    def compress(self, condition, axis=0, **kwargs):
        carr = carray_block_compress(self.carr, condition, axis, **kwargs)
        return HaplotypeCArray(carr, copy=False)

    def take(self, indices, axis=0, **kwargs):
        carr = carray_block_take(self.carr, indices, axis, **kwargs)
        return HaplotypeCArray(carr, copy=False)

    def subset(self, variants=None, haplotypes=None, **kwargs):
        data = carray_block_subset(self.carr, variants, haplotypes, **kwargs)
        return HaplotypeCArray(data, copy=False)

    def to_genotypes(self, ploidy, **kwargs):
        # Unfortunately this cannot be implemented as a lightweight view,
        # so we have to copy.

        # check ploidy is compatible
        if (self.n_haplotypes % ploidy) > 0:
            raise ValueError('incompatible ploidy')

        # build output
        def f(block):
            return block.reshape((block.shape[0], -1, ploidy))
        carr = carray_block_map(self.carr, f, **kwargs)

        g = GenotypeCArray(carr, copy=False)
        return g

    def is_called(self, **kwargs):
        return self.compare_scalar(operator.ge, 0, **kwargs)

    def is_missing(self, **kwargs):
        return self.compare_scalar(operator.lt, 0, **kwargs)

    def is_ref(self, **kwargs):
        return self.compare_scalar(operator.eq, 0, **kwargs)

    def is_alt(self, allele=None, **kwargs):
        if allele is None:
            return self.compare_scalar(operator.gt, 0, **kwargs)
        else:
            return self.compare_scalar(operator.eq, allele, **kwargs)

    def is_call(self, allele, **kwargs):
        return self.compare_scalar(operator.eq, allele, **kwargs)

    def count_called(self, axis=None):
        def f(block):
            return HaplotypeArray(block, copy=False).is_called()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_missing(self, axis=None):
        def f(block):
            return HaplotypeArray(block, copy=False).is_missing()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_ref(self, axis=None):
        def f(block):
            return HaplotypeArray(block, copy=False).is_ref()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_alt(self, axis=None):
        def f(block):
            return HaplotypeArray(block, copy=False).is_alt()
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_call(self, allele, axis=None):
        def f(block):
            h = HaplotypeArray(block, copy=False)
            return h.is_call(allele=allele)
        return carray_block_sum(self.carr, axis=axis, transform=f)

    def count_alleles(self, max_allele=None, subpop=None, **kwargs):

        # if max_allele not specified, count all alleles
        if max_allele is None:
            max_allele = self.max()

        def f(block):
            h = HaplotypeArray(block, copy=False)
            return h.count_alleles(max_allele=max_allele, subpop=subpop)

        carr = carray_block_map(self.carr, f, **kwargs)

        return AlleleCountsCArray(carr, copy=False)

    def count_alleles_subpops(self, subpops, max_allele=None, **kwargs):

        # if max_allele not specified, count all alleles
        if max_allele is None:
            max_allele = self.max()

        # setup output table
        names = sorted(subpops.keys())
        subpops = [subpops[n] for n in names]
        kwargs['names'] = names  # override to ensure correct order
        kwargs.setdefault('expectedlen', self.shape[0])
        acs_ctbl = None

        # determine block size for iteration
        blen = kwargs.pop('blen', None)
        if blen is None:
            blen = self.carr.chunklen

        # block iteration
        for i in range(0, self.carr.shape[0], blen):
            block = self.carr[i:i+blen]
            h = HaplotypeArray(block, copy=False)
            cols = [h.count_alleles(max_allele=max_allele, subpop=subpop)
                    for subpop in subpops]
            if acs_ctbl is None:
                acs_ctbl = bcolz.ctable(cols, **kwargs)
            else:
                acs_ctbl.append(cols)

        # wrap for convenience
        return AlleleCountsCTable(acs_ctbl)


class AlleleCountsCArray(_CArrayWrapper):
    """Alternative implementation of the :class:`allel.model.AlleleCountsArray`
    interface, using a :class:`bcolz.carray` as the backing store.

    Parameters
    ----------

    data : array_like, int, shape (n_variants, n_alleles), optional
        Data to initialise the array with. May be a bcolz carray, which will
        not be copied if copy=False. May also be None, in which case rootdir
        must be provided (disk-based array).
    copy : bool, optional
        If True, copy the input data into a new bcolz carray.
    **kwargs : keyword arguments
        Passed through to the bcolz carray constructor.

    """

    @staticmethod
    def check_input_data(obj):

        # check dtype
        if obj.dtype.kind not in 'ui':
            raise TypeError('integer dtype required')

        # check dimensionality
        if hasattr(obj, 'ndim'):
            ndim = obj.ndim
        else:
            ndim = len(obj.shape)
        if ndim != 2:
            raise TypeError('array with 2 dimensions required')

    def __init__(self, data=None, copy=True, **kwargs):
        if copy or not isinstance(data, bcolz.carray):
            carr = bcolz.carray(data, **kwargs)
        else:
            carr = data
        # check late to avoid creating an intermediate numpy array
        self.check_input_data(carr)
        object.__setattr__(self, 'carr', carr)

    def __getitem__(self, *args):
        out = self.carr.__getitem__(*args)
        if hasattr(out, 'ndim') \
                and out.ndim == 2 \
                and out.shape[1] == self.n_alleles:
            # wrap only if number of alleles is preserved
            out = AlleleCountsArray(out, copy=False)
        return out

    @property
    def n_variants(self):
        """Number of variants (length of first array dimension)."""
        return self.carr.shape[0]

    @property
    def n_alleles(self):
        """Number of alleles (length of second array dimension)."""
        return self.carr.shape[1]

    def compress(self, condition, axis=0, **kwargs):
        carr = carray_block_compress(self.carr, condition, axis, **kwargs)
        if carr.shape[1] == self.shape[1]:
            return AlleleCountsCArray(carr, copy=False)
        else:
            return carr

    def take(self, indices, axis=0, **kwargs):
        carr = carray_block_take(self.carr, indices, axis, **kwargs)
        if carr.shape[1] == self.shape[1]:
            # alleles preserved, safe to wrap
            return AlleleCountsCArray(carr, copy=False)
        else:
            return carr

    def to_frequencies(self, fill=np.nan, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.to_frequencies(fill=fill)
        return carray_block_map(self.carr, f, **kwargs)

    def allelism(self, **kwargs):
        def f(block):
            return AlleleCountsArray(block, copy=False).allelism()
        return carray_block_map(self.carr, f, **kwargs)

    def is_variant(self, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_variant()
        return carray_block_map(self.carr, f, **kwargs)

    def is_non_variant(self, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_non_variant()
        return carray_block_map(self.carr, f, **kwargs)

    def is_segregating(self, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_segregating()
        return carray_block_map(self.carr, f, **kwargs)

    def is_non_segregating(self, allele=None, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_non_segregating(allele=allele)
        return carray_block_map(self.carr, f, **kwargs)

    def is_singleton(self, allele=1, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_singleton(allele=allele)
        return carray_block_map(self.carr, f, **kwargs)

    def is_doubleton(self, allele=1, **kwargs):
        def f(block):
            ac = AlleleCountsArray(block, copy=False)
            return ac.is_doubleton(allele=allele)
        return carray_block_map(self.carr, f, **kwargs)

    def count_variant(self):
        return carray_block_sum(self.is_variant())

    def count_non_variant(self):
        return carray_block_sum(self.is_non_variant())

    def count_segregating(self):
        return carray_block_sum(self.is_segregating())

    def count_non_segregating(self, allele=None):
        return carray_block_sum(self.is_non_segregating(allele=allele))

    def count_singleton(self, allele=1):
        return carray_block_sum(self.is_singleton(allele=allele))

    def count_doubleton(self, allele=1):
        return carray_block_sum(self.is_doubleton(allele=allele))


class _CTableWrapper(object):

    ndarray_cls = None

    def __array__(self):
        return self.ctbl[:]

    def __getitem__(self, item):
        res = self.ctbl[item]
        if isinstance(res, np.ndarray) \
                and res.dtype.names \
                and self.ndarray_cls is not None:
            return self.ndarray_cls(res, copy=False)
        if isinstance(res, bcolz.ctable):
            return type(self)(res, copy=False)
        return res

    def __getattr__(self, item):
        if hasattr(self.ctbl, item):
            return getattr(self.ctbl, item)
        elif item in self.names:
            return self.ctbl[item]
        else:
            raise AttributeError(item)

    def __repr__(self):
        s = repr(self.ctbl)
        s = type(self).__name__ + s[6:]
        return s

    def __len__(self):
        return len(self.ctbl)

    def _repr_html_(self):
        # use implementation from pandas
        import pandas
        df = pandas.DataFrame(self[:5])
        # noinspection PyProtectedMember
        return df._repr_html_()

    @classmethod
    def open(cls, rootdir, mode='r'):
        cobj = bcolz.open(rootdir, mode=mode)
        if isinstance(cobj, bcolz.ctable):
            return cls(cobj, copy=False)
        else:
            raise ValueError('rootdir does not contain a ctable')

    def addcol(self, newcol, name, **kwargs):
        # bcolz.ctable.addcol is broken for persistent ctables
        self.ctbl.addcol_persistent(newcol, name=name, **kwargs)

    def display(self, n=5):
        # use implementation from pandas
        import pandas
        import IPython.display
        df = pandas.DataFrame(self[:n])
        # noinspection PyProtectedMember
        html = df._repr_html_()
        IPython.display.display_html(html, raw=True)

    @property
    def names(self):
        return tuple(self.ctbl.names)

    def compress(self, condition, **kwargs):
        ctbl = ctable_block_compress(self.ctbl, condition, **kwargs)
        return type(self)(ctbl, copy=False)

    def take(self, indices, **kwargs):
        ctbl = ctable_block_take(self.ctbl, indices, **kwargs)
        return type(self)(ctbl, copy=False)

    def eval(self, expression, vm='numexpr', **kwargs):
        return self.ctbl.eval(expression, vm=vm, **kwargs)

    def query(self, expression, vm='numexpr'):
        condition = self.eval(expression, vm=vm)
        return self.compress(condition)

    @classmethod
    def from_hdf5_group(cls, *args, **kwargs):
        """Load a bcolz ctable from columns stored as separate datasets with an
        HDF5 group.

        Either provide an h5py group as a single positional argument,
        or provide two positional arguments giving the HDF5 file path and the
        group node path within the file.

        All keyword arguments are passed through to the bcolz.ctable
        constructor.

        """
        ctbl = ctable_from_hdf5_group(*args, **kwargs)
        return cls(ctbl, copy=False)

    def to_hdf5_group(self, parent, name, **kwargs):
        """Write each column in a bcolz ctable to a dataset in an HDF5 group.

        Parameters
        ----------

        parent : string or h5py group
            Parent HDF5 file or group. If a string, will be treated as HDF5
            file name.
        name : string
            Name or path of group to write data into.
        kwargs : keyword arguments
            Passed through to h5py require_dataset() function.

        Returns
        -------

        h5g : h5py group

        """
        return ctable_to_hdf5_group(self.ctbl, parent, name, **kwargs)


class VariantCTable(_CTableWrapper):
    """Alternative implementation of the :class:`allel.model.VariantTable`
    interface, using a :class:`bcolz.ctable` as the backing store.

    Parameters
    ----------

    data : tuple or list of column objects, optional
        The list of column data to build the ctable object. This can also be a
        pure NumPy structured array. May also be a bcolz ctable, which will
        not be copied if copy=False. May also be None, in which case rootdir
        must be provided (disk-based array).
    copy : bool, optional
        If True, copy the input data into a new bcolz ctable.
    index : string or pair of strings, optional
        If a single string, name of column to use for a sorted index. If a
        pair of strings, name of columns to use for a sorted multi-index.
    **kwargs : keyword arguments
        Passed through to the bcolz ctable constructor.

    Examples
    --------

    Instantiate from existing data::

        >>> import allel
        >>> chrom = [b'chr1', b'chr1', b'chr2', b'chr2', b'chr3']
        >>> pos = [2, 7, 3, 9, 6]
        >>> dp = [35, 12, 78, 22, 99]
        >>> qd = [4.5, 6.7, 1.2, 4.4, 2.8]
        >>> ac = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
        >>> vt = allel.bcolz.VariantCTable([chrom, pos, dp, qd, ac],
        ...                                names=['CHROM', 'POS', 'DP', 'QD', 'AC'],
        ...                                index=('CHROM', 'POS'))
        >>> vt
        VariantCTable((5,), [('CHROM', 'S4'), ('POS', '<i8'), ('DP', '<i8'), ('QD', '<f8'), ('AC', '<i8', (2,))])
          nbytes: 220; cbytes: 80.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [(b'chr1', 2, 35, 4.5, [1, 2]) (b'chr1', 7, 12, 6.7, [3, 4])
         (b'chr2', 3, 78, 1.2, [5, 6]) (b'chr2', 9, 22, 4.4, [7, 8])
         (b'chr3', 6, 99, 2.8, [9, 10])]

    Slicing rows returns :class:`allel.model.VariantTable`::

        >>> vt[:2]
        VariantTable((2,), dtype=[('CHROM', 'S4'), ('POS', '<i8'), ('DP', '<i8'), ('QD', '<f8'), ('AC', '<i8', (2,))])
        [(b'chr1', 2, 35, 4.5, array([1, 2])) (b'chr1', 7, 12, 6.7, array([3, 4]))]

    Accessing columns returns :class:`allel.bcolz.VariantCTable`::

        >>> vt[['DP', 'QD']]
        VariantCTable((5,), [('DP', '<i8'), ('QD', '<f8')])
          nbytes: 80; cbytes: 32.00 KB; ratio: 0.00
          cparams := cparams(clevel=5, shuffle=True, cname='blosclz')
        [(35, 4.5) (12, 6.7) (78, 1.2) (22, 4.4) (99, 2.8)]

    Use the index to locate variants:

        >>> loc = vt.index.locate_range(b'chr2', 1, 10)
        >>> vt[loc]
        VariantTable((2,), dtype=[('CHROM', 'S4'), ('POS', '<i8'), ('DP', '<i8'), ('QD', '<f8'), ('AC', '<i8', (2,))])
        [(b'chr2', 3, 78, 1.2, array([5, 6])) (b'chr2', 9, 22, 4.4, array([7, 8]))]

    """  # noqa

    ndarray_cls = VariantTable

    def __init__(self, data=None, copy=True, index=None, **kwargs):
        if copy or not isinstance(data, bcolz.ctable):
            ctbl = bcolz.ctable(data, **kwargs)
        else:
            ctbl = data
        object.__setattr__(self, 'ctbl', ctbl)
        # initialise index
        self.set_index(index)

    def set_index(self, index):
        if index is None:
            pass
        elif isinstance(index, str):
            index = SortedIndex(self.ctbl[index][:], copy=False)
        elif isinstance(index, (tuple, list)) and len(index) == 2:
            index = SortedMultiIndex(self.ctbl[index[0]][:],
                                     self.ctbl[index[1]][:],
                                     copy=False)
        else:
            raise ValueError('invalid index argument, expected string or '
                             'pair of strings, found %s' % repr(index))
        object.__setattr__(self, 'index', index)

    @property
    def n_variants(self):
        return len(self.ctbl)

    def to_vcf(self, path, rename=None, number=None, description=None,
               fill=None, blen=None, write_header=True):
        with open(path, 'w') as vcf_file:
            if write_header:
                write_vcf_header(vcf_file, self, rename=rename, number=number,
                                 description=description)
            if blen is None:
                blen = min(self.ctbl[col].chunklen for col in self.ctbl.cols)
            for i in range(0, self.ctbl.shape[0], blen):
                block = self.ctbl[i:i+blen]
                write_vcf_data(vcf_file, block, rename=rename, fill=fill)


class FeatureCTable(_CTableWrapper):
    """Alternative implementation of the :class:`allel.model.FeatureTable`
    interface, using a :class:`bcolz.ctable` as the backing store.

    Parameters
    ----------

    data : tuple or list of column objects, optional
        The list of column data to build the ctable object. This can also be a
        pure NumPy structured array. May also be a bcolz ctable, which will
        not be copied if copy=False. May also be None, in which case rootdir
        must be provided (disk-based array).
    copy : bool, optional
        If True, copy the input data into a new bcolz ctable.
    index : pair or triplet of strings, optional
        Names of columns to use for positional index, e.g., ('start',
        'stop') if table contains 'start' and 'stop' columns and records
        from a single chromosome/contig, or ('seqid', 'start', 'end') if table
        contains records from multiple chromosomes/contigs.
    **kwargs : keyword arguments
        Passed through to the bcolz ctable constructor.

    """

    ndarray_cls = FeatureTable

    def __init__(self, data=None, copy=True, **kwargs):
        if copy or not isinstance(data, bcolz.ctable):
            ctbl = bcolz.ctable(data, **kwargs)
        else:
            ctbl = data
        object.__setattr__(self, 'ctbl', ctbl)
        # TODO initialise interval index
        # self.set_index(index)

    @property
    def n_features(self):
        return len(self.ctbl)

    def to_mask(self, size, start_name='start', stop_name='end'):
        """Construct a mask array where elements are True if the fall within
        features in the table.

        Parameters
        ----------

        size : int
            Size of chromosome/contig.
        start_name : string, optional
            Name of column with start coordinates.
        stop_name : string, optional
            Name of column with stop coordinates.

        Returns
        -------

        mask : ndarray, bool

        """
        m = np.zeros(size, dtype=bool)
        for start, stop in self[[start_name, stop_name]]:
            m[start-1:stop] = True
        return m

    @staticmethod
    def from_gff3(path, attributes=None, region=None,
                  score_fill=-1, phase_fill=-1, attributes_fill=b'.',
                  dtype=None, **kwargs):
        """Read a feature table from a GFF3 format file.

        Parameters
        ----------

        path : string
            File path.
        attributes : list of strings, optional
            List of columns to extract from the "attributes" field.
        region : string, optional
            Genome region to extract. If given, file must be position
            sorted, bgzipped and tabix indexed. Tabix must also be installed
            and on the system path.
        score_fill : object, optional
            Value to use where score field has a missing value.
        phase_fill : object, optional
            Value to use where phase field has a missing value.
        attributes_fill : object or list of objects, optional
            Value(s) to use where attribute field(s) have a missing value.
        dtype : numpy dtype, optional
            Manually specify a dtype.

        Returns
        -------

        ft : FeatureCTable

        """

        # setup iterator
        recs = iter_gff3(path, attributes=attributes, region=region,
                         score_fill=score_fill, phase_fill=phase_fill,
                         attributes_fill=attributes_fill)

        # determine dtype from sample of initial records
        if dtype is None:
            names = 'seqid', 'source', 'type', 'start', 'end', 'score', \
                    'strand', 'phase'
            if attributes is not None:
                names += tuple(attributes)
            recs_sample = list(itertools.islice(recs, 1000))
            a = np.rec.array(recs_sample, names=names)
            dtype = a.dtype
            recs = itertools.chain(recs_sample, recs)

        # set ctable defaults
        kwargs.setdefault('expectedlen', 200000)

        # initialise ctable
        ctbl = bcolz.ctable(np.array([], dtype=dtype), **kwargs)

        # determine block size to read
        blen = min(ctbl[col].chunklen for col in ctbl.cols)

        # read block-wise
        block = list(itertools.islice(recs, 0, blen))
        while block:
            a = np.array(block, dtype=dtype)
            ctbl.append(a)
            block = list(itertools.islice(recs, 0, blen))

        ft = FeatureCTable(ctbl, copy=False)
        return ft


class AlleleCountsCTable(_CTableWrapper):

    def __init__(self, ctbl):
        self.ctbl = ctbl

    def __getitem__(self, item):
        o = super(AlleleCountsCTable, self).__getitem__(item)
        if isinstance(o, bcolz.carray):
            return AlleleCountsCArray(o, copy=False)
        return o
