from datetime import timedelta
import functools

import numpy as np
import pandas as pd

from . import common
from . import indexing
from . import ops
from . import utils
from .pycompat import basestring, OrderedDict, zip

import xray # only for Dataset and DataArray


def as_variable(obj, key=None, strict=True):
    """Convert an object into an Variable

    - If the object is already an `Variable`, return it.
    - If the object is a `DataArray`, return it if `strict=False` or return
      its variable if `strict=True`.
    - Otherwise, if the object has 'dims' and 'data' attributes, convert
      it into a new `Variable`.
    - If all else fails, attempt to convert the object into an `Variable` by
      unpacking it into the arguments for `Variable.__init__`.
    """
    # TODO: consider extending this method to automatically handle Iris and
    # pandas objects.
    if strict and hasattr(obj, 'variable'):
        # extract the primary Variable from DataArrays
        obj = obj.variable
    if not isinstance(obj, (Variable, xray.DataArray)):
        if hasattr(obj, 'dims') and hasattr(obj, 'values'):
            obj = Variable(obj.dims, obj.values,
                           getattr(obj, 'attrs', None),
                           getattr(obj, 'encoding', None))
        elif isinstance(obj, tuple):
            try:
                obj = Variable(*obj)
            except TypeError:
                raise TypeError('cannot convert argument into an Variable')
        elif utils.is_scalar(obj):
            obj = Variable([], obj)
        elif getattr(obj, 'name', None) is not None:
            obj = Variable(obj.name, obj)
        elif key is not None:
            obj = Variable(key, obj)
        else:
            raise TypeError('cannot infer Variable dimensions')
    return obj


def _maybe_wrap_data(data):
    """
    Put pandas.Index and numpy.ndarray arguments in adapter objects to ensure
    they can be indexed properly.

    NumpyArrayAdapter, PandasIndexAdapter and LazilyIndexedArray should
    all pass through unmodified.
    """
    if isinstance(data, pd.Index):
        # check pd.Index first since it may be an ndarray subclass
        return PandasIndexAdapter(data)
    if isinstance(data, np.ndarray):
        return NumpyArrayAdapter(data)
    return data


def _as_compatible_data(data, fastpath=False):
    """Prepare and wrap data to put in a Variable.

    - If data does not have the necessary attributes, convert it to ndarray.
    - If data has dtype=datetime64, ensure that it has ns precision. If it's a
      pandas.Timestamp, convert it to datetime64.
    - If data is already a pandas or xray object (other than an Index), just
      use the values.

    Finally, wrap it up with an adapter if necessary.
    """
    if fastpath and getattr(data, 'ndim', 0) > 0:
        # can't use fastpath (yet) for scalars
        return _maybe_wrap_data(data)

    if isinstance(data, pd.Index):
        if isinstance(data, pd.MultiIndex):
            raise NotImplementedError(
                'no support yet for using a pandas.MultiIndex in an '
                'xray.Coordinate')
        return _maybe_wrap_data(data)

    if isinstance(data, pd.Timestamp):
        # TODO: convert, handle datetime objects, too
        data = np.datetime64(data.value, 'ns')
    if isinstance(data, timedelta):
        data = np.timedelta64(getattr(data, 'value', data), 'ns')

    # don't check for __len__ or __iter__ so as not to cast if data is a numpy
    # numeric type like np.float32
    required = ['dtype', 'shape', 'size', 'ndim']
    if (any(not hasattr(data, attr) for attr in required)
            or isinstance(data, (np.string_, np.datetime64, np.timedelta64))):
        # data must be ndarray-like
        data = np.asarray(data)

    # we don't want nested self-described arrays
    data = getattr(data, 'values', data)

    if isinstance(data, np.ma.MaskedArray):
        mask = np.ma.getmaskarray(data)
        if mask.any():
            dtype, fill_value = common._maybe_promote(data.dtype)
            data = np.asarray(data, dtype=dtype)
            data[mask] = fill_value
        else:
            data = np.asarray(data)

    if isinstance(data, np.ndarray):
        data = common._possibly_convert_objects(data)
        if data.dtype.kind == 'M':
            # TODO: automatically cast arrays of datetime objects as well
            data = np.asarray(data, 'datetime64[ns]')
        if data.dtype.kind == 'm':
            data = np.asarray(data, 'timedelta64[ns]')

    return _maybe_wrap_data(data)


class NumpyArrayAdapter(utils.NDArrayMixin):
    """Wrap a NumPy array to use orthogonal indexing (array indexing
    accesses different dimensions independently, like netCDF4-python variables)
    """
    # note: this object is somewhat similar to biggus.NumpyArrayAdapter in that
    # it implements orthogonal indexing, except it casts to a numpy array,
    # isn't lazy and supports writing values.
    def __init__(self, array):
        self.array = np.asarray(array)

    def __array__(self, dtype=None):
        return np.asarray(self.array, dtype=dtype)

    def _convert_key(self, key):
        key = indexing.expanded_indexer(key, self.ndim)
        if any(not isinstance(k, (int, np.integer, slice)) for k in key):
            # key would trigger fancy indexing
            key = indexing.orthogonal_indexer(key, self.shape)
        return key

    def __getitem__(self, key):
        key = self._convert_key(key)
        return self.array[key]

    def __setitem__(self, key, value):
        key = self._convert_key(key)
        self.array[key] = value


class PandasIndexAdapter(utils.NDArrayMixin):
    """Wrap a pandas.Index to be better about preserving dtypes and to handle
    indexing by length 1 tuples like numpy
    """
    def __init__(self, array, dtype=None):
        self.array = utils.safe_cast_to_index(array)
        if dtype is None:
            dtype = array.dtype
        self._dtype = dtype

    @property
    def dtype(self):
        return self._dtype

    def __array__(self, dtype=None):
        if dtype is None:
            dtype = self.dtype
        return self.array.values.astype(dtype)

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 1:
            # unpack key so it can index a pandas.Index object (pandas.Index
            # objects don't like tuples)
            key, = key

        if isinstance(key, (int, np.integer)):
            value = self.array[key]
            if value is pd.NaT:
                # work around the impossibility of casting NaT with asarray
                # note: it probably would be better in general to return
                # pd.Timestamp rather np.than datetime64 but this is easier
                # (for now)
                value = np.datetime64('NaT', 'ns')
            elif isinstance(value, timedelta):
                value = np.timedelta64(getattr(value, 'value', value), 'ns')
            else:
                value = np.asarray(value, dtype=self.dtype)
        else:
            value = PandasIndexAdapter(self.array[key], dtype=self.dtype)

        return value

    def __repr__(self):
        return ('%s(array=%r, dtype=%r)'
                % (type(self).__name__, self.array, self.dtype))


def _as_array_or_item(data):
    """Return the given values as a numpy array, or as an individual item if
    it's a 0-dimensional object array or datetime64.

    Importantly, this function does not copy data if it is already an ndarray -
    otherwise, it will not be possible to update Variable values in place.
    """
    data = np.asarray(data)
    if data.ndim == 0:
        if data.dtype.kind == 'O':
            # unpack 0d object arrays to be consistent with numpy
            data = data.item()
        elif data.dtype.kind == 'M':
            # convert to a np.datetime64 object, because 0-dimensional ndarrays
            # with dtype=datetime64 are broken :(
            data = np.datetime64(data, 'ns')
        elif data.dtype.kind == 'm':
            data = np.timedelta64(data, 'ns')
    return data


class Variable(common.AbstractArray):
    """A netcdf-like variable consisting of dimensions, data and attributes
    which describe a single Array. A single Variable object is not fully
    described outside the context of its parent Dataset (if you want such a
    fully described object, use a DataArray instead).

    The main functional difference between Variables and numpy arrays is that
    numerical operations on Variables implement array broadcasting by dimension
    name. For example, adding an Variable with dimensions `('time',)` to
    another Variable with dimensions `('space',)` results in a new Variable
    with dimensions `('time', 'space')`. Furthermore, numpy reduce operations
    like ``mean`` or ``sum`` are overwritten to take a "dimension" argument
    instead of an "axis".

    Variables are light-weight objects used as the building block for datasets.
    They are more primitive objects, so operations with them provide marginally
    higher performance than using DataArrays. However, manipulating data in the
    form of a Dataset or DataArray should almost always be preferred, because
    they can use more complete metadata in context of coordinate labels.
    """
    def __init__(self, dims, data, attrs=None, encoding=None, fastpath=False):
        """
        Parameters
        ----------
        dims : str or sequence of str
            Name(s) of the the data dimension(s). Must be either a string (only
            for 1D data) or a sequence of strings with length equal to the
            number of dimensions.
        data : array_like
            Data array which supports numpy-like data access.
        attrs : dict_like or None, optional
            Attributes to assign to the new variable. If None (default), an
            empty attribute dictionary is initialized.
        encoding : dict_like or None, optional
            Dictionary specifying how to encode this array's data into a
            serialized format like netCDF4. Currently used keys (for netCDF)
            include '_FillValue', 'scale_factor', 'add_offset' and 'dtype'.
            Well behaviored code to serialize a Variable should ignore
            unrecognized encoding items.
        """
        self._data = _as_compatible_data(data, fastpath=fastpath)
        self._dims = self._parse_dimensions(dims)
        self._attrs = None
        self._encoding = None
        if attrs is not None:
            self.attrs = attrs
        if encoding is not None:
            self.encoding = encoding

    @property
    def dtype(self):
        return self._data.dtype

    @property
    def shape(self):
        return self._data.shape

    @property
    def size(self):
        return self._data.size

    @property
    def ndim(self):
        return self._data.ndim

    def __len__(self):
        return len(self._data)

    @property
    def _in_memory(self):
        return isinstance(self._data, (NumpyArrayAdapter, PandasIndexAdapter))

    _cache_data_class = NumpyArrayAdapter

    def _data_cached(self):
        if not isinstance(self._data, self._cache_data_class):
            self._data = self._cache_data_class(self._data)
        return self._data

    def load_data(self):
        """Manually trigger loading of this variable's data from disk or a
        remote source into memory and return this variable.

        Normally, it should not be necessary to call this method in user code,
        because all xray functions should either work on deferred data or
        load data automatically.
        """
        self._data_cached()
        return self

    def __getstate__(self):
        """Always cache data as an in-memory array before pickling"""
        self._data_cached()
        # self.__dict__ is the default pickle object, we don't need to
        # implement our own __setstate__ method to make pickle work
        return self.__dict__

    @property
    def values(self):
        """The variable's data as a numpy.ndarray"""
        return _as_array_or_item(self._data_cached())

    @values.setter
    def values(self, values):
        values = _as_compatible_data(values)
        if values.shape != self.shape:
            raise ValueError(
                "replacement values must match the Variable's shape")
        self._data = values

    def to_coord(self):
        """Return this variable as an xray.Coordinate"""
        return Coordinate(self.dims, self._data, self._attrs,
                          encoding=self._encoding, fastpath=True)

    def to_index(self):
        """Convert this variable to a pandas.Index"""
        return self.to_coord().to_index()

    @property
    def dims(self):
        """Tuple of dimension names with which this variable is associated.
        """
        return self._dims

    def _parse_dimensions(self, dims):
        if isinstance(dims, basestring):
            dims = (dims,)
        dims = tuple(dims)
        if len(dims) != self.ndim:
            raise ValueError('dimensions %s must have the same length as the '
                             'number of data dimensions, ndim=%s'
                             % (dims, self.ndim))
        return dims

    @dims.setter
    def dims(self, value):
        self._dims = self._parse_dimensions(value)

    def _item_key_to_tuple(self, key):
        if utils.is_dict_like(key):
            return tuple(key.get(dim, slice(None)) for dim in self.dims)
        else:
            return key

    def __getitem__(self, key):
        """Return a new Array object whose contents are consistent with
        getting the provided key from the underlying data.

        NB. __getitem__ and __setitem__ implement "orthogonal indexing" like
        netCDF4-python, where the key can only include integers, slices
        (including `Ellipsis`) and 1d arrays, each of which are applied
        orthogonally along their respective dimensions.

        The difference does not matter in most cases unless you are using
        numpy's "fancy indexing," which can otherwise result in data arrays
        whose shapes is inconsistent (or just uninterpretable with) with the
        variable's dimensions.

        If you really want to do indexing like `x[x > 0]`, manipulate the numpy
        array `x.values` directly.
        """
        key = self._item_key_to_tuple(key)
        key = indexing.expanded_indexer(key, self.ndim)
        dims = tuple(dim for k, dim in zip(key, self.dims)
                     if not isinstance(k, (int, np.integer)))
        values = self._data[key]
        # orthogonal indexing should ensure the dimensionality is consistent
        if hasattr(values, 'ndim'):
            assert values.ndim == len(dims), (values.ndim, len(dims))
        else:
            assert len(dims) == 0, len(dims)
        return type(self)(dims, values, self._attrs, fastpath=True)

    def __setitem__(self, key, value):
        """__setitem__ is overloaded to access the underlying numpy values with
        orthogonal indexing.

        See __getitem__ for more details.
        """
        key = self._item_key_to_tuple(key)
        self._data_cached()[key] = value

    @property
    def attrs(self):
        """Dictionary of local attributes on this variable.
        """
        if self._attrs is None:
            self._attrs = OrderedDict()
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        self._attrs = OrderedDict(value)

    @property
    def encoding(self):
        """Dictionary of encodings on this variable.
        """
        if self._encoding is None:
            self._encoding = {}
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = dict(value)

    def copy(self, deep=True):
        """Returns a copy of this object.

        If `deep=True`, the data array is loaded into memory and copied onto
        the new object. Dimensions, attributes and encodings are always copied.
        """
        data = self.values.copy() if deep else self._data
        # note:
        # dims is already an immutable tuple
        # attributes and encoding will be copied when the new Array is created
        return type(self)(self.dims, data, self._attrs, self._encoding,
                          fastpath=True)

    def __copy__(self):
        return self.copy(deep=False)

    def __deepcopy__(self, memo=None):
        # memo does nothing but is required for compatability with
        # copy.deepcopy
        return self.copy(deep=True)

    # mutable objects should not be hashable
    __hash__ = None

    def isel(self, **indexers):
        """Return a new array indexed along the specified dimension(s).

        Parameters
        ----------
        **indexers : {dim: indexer, ...}
            Keyword arguments with names matching dimensions and values given
            by integers, slice objects or arrays.

        Returns
        -------
        obj : Array object
            A new Array with the selected data and dimensions. In general,
            the new variable's data will be a view of this variable's data,
            unless numpy fancy indexing was triggered by using an array
            indexer, in which case the data will be a copy.
        """
        invalid = [k for k in indexers if not k in self.dims]
        if invalid:
            raise ValueError("dimensions %r do not exist" % invalid)

        key = [slice(None)] * self.ndim
        for i, dim in enumerate(self.dims):
            if dim in indexers:
                key[i] = indexers[dim]
        return self[tuple(key)]

    def transpose(self, *dims):
        """Return a new Variable object with transposed dimensions.

        Parameters
        ----------
        *dims : str, optional
            By default, reverse the dimensions. Otherwise, reorder the
            dimensions to this order.

        Returns
        -------
        transposed : Variable
            The returned object has transposed data and dimensions with the
            same attributes as the original.

        Notes
        -----
        Although this operation returns a view of this variable's data, it is
        not lazy -- the data will be fully loaded.

        See Also
        --------
        numpy.transpose
        """
        if len(dims) == 0:
            dims = self.dims[::-1]
        axes = self.get_axis_num(dims)
        data = self.values.transpose(axes)
        return type(self)(dims, data, self._attrs, self._encoding, fastpath=True)

    def squeeze(self, dim=None):
        """Return a new Variable object with squeezed data.

        Parameters
        ----------
        dim : None or str or tuple of str, optional
            Selects a subset of the length one dimensions. If a dimension is
            selected with length greater than one, an error is raised. If
            None, all length one dimensions are squeezed.

        Returns
        -------
        squeezed : Variable
            This array, but with with all or a subset of the dimensions of
            length 1 removed.

        Notes
        -----
        Although this operation returns a view of this variable's data, it is
        not lazy -- the data will be fully loaded.

        See Also
        --------
        numpy.squeeze
        """
        dims = dict(zip(self.dims, self.shape))
        return common.squeeze(self, dims, dim)

    def set_dims(self, dims):
        """Return a new variable with expanded dimensions.

        When possible, this operation does not copy this variable's data.

        Parameters
        ----------
        dims : str or sequence of str or dict
            Dimensions to include on the new variable. If a dict, values are
            used to provide the sizes of new dimensions; otherwise, new
            dimensions are inserted with length 1.

        Returns
        -------
        Variable
        """
        if isinstance(dims, basestring):
            dims = [dims]

        if not utils.is_dict_like(dims):
            dims_map = dict(zip(self.dims, self.shape))
            dims = OrderedDict((d, dims_map.get(d, 1)) for d in dims)

        missing_dims = set(self.dims) - set(dims)
        if missing_dims:
            raise ValueError('new dimensions must be a superset of existing '
                             'dimensions')

        self_dims = set(self.dims)
        exp_dims = tuple(d for d in dims if d not in self_dims) + self.dims
        exp_data = utils.broadcast_to(self, [dims[d] for d in exp_dims])
        expanded_var = Variable(exp_dims, exp_data, self._attrs,
                                self._encoding, fastpath=True)
        return expanded_var.transpose(*dims)

    def reduce(self, func, dim=None, axis=None, keep_attrs=False,
               **kwargs):
        """Reduce this array by applying `func` along some dimension(s).

        Parameters
        ----------
        func : function
            Function which can be called in the form
            `func(x, axis=axis, **kwargs)` to return the result of reducing an
            np.ndarray over an integer valued axis.
        dim : str or sequence of str, optional
            Dimension(s) over which to apply `func`.
        axis : int or sequence of int, optional
            Axis(es) over which to apply `func`. Only one of the 'dim'
            and 'axis' arguments can be supplied. If neither are supplied, then
            the reduction is calculated over the flattened array (by calling
            `func(x)` without an axis argument).
        keep_attrs : bool, optional
            If True, the variable's attributes (`attrs`) will be copied from
            the original object to the new one.  If False (default), the new
            object will be returned without attributes.
        **kwargs : dict
            Additional keyword arguments passed on to `func`.

        Returns
        -------
        reduced : Array
            Array with summarized data and the indicated dimension(s)
            removed.
        """
        if dim is not None and axis is not None:
            raise ValueError("cannot supply both 'axis' and 'dim' arguments")

        if dim is not None:
            axis = self.get_axis_num(dim)
        data = func(self.values, axis=axis, **kwargs)

        removed_axes = (range(self.ndim) if axis is None
                        else np.atleast_1d(axis) % self.ndim)
        dims = [dim for n, dim in enumerate(self.dims)
                if n not in removed_axes]

        attrs = self._attrs if keep_attrs else None

        return Variable(dims, data, attrs=attrs)

    @classmethod
    def concat(cls, variables, dim='concat_dim', indexers=None, length=None,
               shortcut=False):
        """Concatenate variables along a new or existing dimension.

        Parameters
        ----------
        variables : iterable of Array
            Arrays to stack together. Each variable is expected to have
            matching dimensions and shape except for along the stacked
            dimension.
        dim : str or DataArray, optional
            Name of the dimension to stack along. This can either be a new
            dimension name, in which case it is added along axis=0, or an
            existing dimension name, in which case the location of the
            dimension is unchanged. Where to insert the new dimension is
            determined by the first variable.
        indexers : iterable of indexers, optional
            Iterable of indexers of the same length as variables which
            specifies how to assign variables along the given dimension. If
            not supplied, indexers is inferred from the length of each
            variable along the dimension, and the variables are stacked in the
            given order.
        length : int, optional
            Length of the new dimension. This is used to allocate the new data
            array for the stacked variable data before iterating over all
            items, which is thus more memory efficient and a bit faster. If
            dimension is provided as a DataArray, length is calculated
            automatically.
        shortcut : bool, optional
            This option is used internally to speed-up groupby operations.
            If `shortcut` is True, some checks of internal consistency between
            arrays to concatenate are skipped.

        Returns
        -------
        stacked : Variable
            Concatenated Variable formed by stacking all the supplied variables
            along the given dimension.
        """
        if not isinstance(dim, basestring):
            length = dim.size
            dim, = dim.dims

        if length is None or indexers is None:
            # so much for lazy evaluation! we need to look at all the variables
            # to figure out the indexers and/or dimensions of the stacked
            # variable
            variables = list(variables)
            steps = [var.shape[var.get_axis_num(dim)]
                     if dim in var.dims else 1
                     for var in variables]
            if length is None:
                length = sum(steps)
            if indexers is None:
                indexers = []
                i = 0
                for step in steps:
                    indexers.append(slice(i, i + step))
                    i += step
                if i != length:
                    raise ValueError('actual length of stacked variables '
                                     'along %s is %r but expected length was '
                                     '%s' % (dim, i, length))

        # initialize the stacked variable with empty data
        first_var, variables = utils.peek_at(variables)
        if dim in first_var.dims:
            axis = first_var.get_axis_num(dim)
            shape = tuple(length if n == axis else s
                          for n, s in enumerate(first_var.shape))
            dims = first_var.dims
        else:
            axis = 0
            shape = (length,) + first_var.shape
            dims = (dim,) + first_var.dims

        dtype = first_var.dtype
        if dtype.kind in ['S', 'U']:
            # use an object array instead of a fixed length strings to avoid
            # possible truncation
            dtype = object

        data = np.empty(shape, dtype=dtype)
        attrs = OrderedDict(first_var.attrs)

        alt_dims = tuple(d for d in dims if d != dim)
        key = [slice(None)] * len(dims)

        # copy in the data from the variables
        for var, indexer in zip(variables, indexers):
            if not shortcut:
                # do sanity checks & attributes clean-up
                if dim in var.dims:
                    # transpose verifies that the dims are equivalent
                    if var.dims != dims:
                        var = var.transpose(*dims)
                elif var.dims != alt_dims:
                    raise ValueError('inconsistent dimensions')
                utils.remove_incompatible_items(attrs, var.attrs)

            key[axis] = indexer
            data[key] = var.values

        return cls(dims, data, attrs)

    def _data_equals(self, other):
        return (self._data is other._data
                or utils.array_equiv(self.values, other.values))

    def equals(self, other):
        """True if two Variables have the same dimensions and values;
        otherwise False.

        Variables can still be equal (like pandas objects) if they have NaN
        values in the same locations.

        This method is necessary because `v1 == v2` for Variables
        does element-wise comparisions (like numpy.ndarrays).
        """
        other = getattr(other, 'variable', other)
        try:
            return (self.dims == other.dims
                    and self._data_equals(other))
        except (TypeError, AttributeError):
            return False

    def broadcast_equals(self, other):
        """True if two Variables have the values after being broadcast against
        each other; otherwise False.

        Variables can still be equal (like pandas objects) if they have NaN
        values in the same locations.
        """
        try:
            self, other = broadcast_variables(self, other)
        except (ValueError, AttributeError):
            return False
        return self.equals(other)

    def identical(self, other):
        """Like equals, but also checks attributes.
        """
        try:
            return (utils.dict_equiv(self.attrs, other.attrs)
                    and self.equals(other))
        except (TypeError, AttributeError):
            return False

    def __array_wrap__(self, obj, context=None):
        return Variable(self.dims, obj)

    @staticmethod
    def _unary_op(f):
        @functools.wraps(f)
        def func(self, *args, **kwargs):
            return self.__array_wrap__(f(self.values, *args, **kwargs))
        return func

    @staticmethod
    def _binary_op(f, reflexive=False):
        @functools.wraps(f)
        def func(self, other):
            if isinstance(other, (xray.DataArray, xray.Dataset)):
                return NotImplemented
            self_data, other_data, dims = _broadcast_variable_data(self, other)
            new_data = (f(self_data, other_data)
                        if not reflexive
                        else f(other_data, self_data))
            return Variable(dims, new_data)
        return func

    @staticmethod
    def _inplace_binary_op(f):
        @functools.wraps(f)
        def func(self, other):
            if isinstance(other, xray.Dataset):
                raise TypeError('cannot add a Dataset to a Variable in-place')
            self_data, other_data, dims = _broadcast_variable_data(self, other)
            if dims != self.dims:
                raise ValueError('dimensions cannot change for in-place '
                                 'operations')
            self.values = f(self_data, other_data)
            return self
        return func

ops.inject_all_ops_and_reduce_methods(Variable)


class Coordinate(Variable):
    """Wrapper around pandas.Index that adds xray specific functionality.

    The most important difference is that Coordinate objects must always have a
    name, which is the dimension along which they index values.

    Coordinates must always be 1-dimensional. In addition to Variable methods
    and properties (attributes, encoding, broadcasting), they support some
    pandas.Index methods directly (e.g., get_indexer), even though pandas does
    not (yet) support duck-typing for indexes.
    """
    _cache_data_class = PandasIndexAdapter

    def __init__(self, name, data, attrs=None, encoding=None, fastpath=False):
        super(Coordinate, self).__init__(name, data, attrs, encoding, fastpath)
        if self.ndim != 1:
            raise ValueError('%s objects must be 1-dimensional' %
                             type(self).__name__)

    def __getitem__(self, key):
        key = self._item_key_to_tuple(key)
        values = self._data[key]
        if not hasattr(values, 'ndim') or values.ndim == 0:
            return Variable((), values, self._attrs, self._encoding)
        else:
            return type(self)(self.dims, values, self._attrs, self._encoding,
                              fastpath=True)

    def __setitem__(self, key, value):
        raise TypeError('%s values cannot be modified' % type(self).__name__)

    def copy(self, deep=True):
        """Returns a copy of this object.

        If `deep=True`, the values array is loaded into memory and copied onto
        the new object. Dimensions, attributes and encodings are always copied.
        """
        # there is no need to copy the index values here even if deep=True
        # since pandas.Index objects are immutable
        data = PandasIndexAdapter(self) if deep else self._data
        return type(self)(self.dims, data, self._attrs, self._encoding,
                          fastpath=True)

    def _data_equals(self, other):
        return self.to_index().equals(other.to_index())

    def to_coord(self):
        """Return this variable as an xray.Coordinate"""
        return self

    def to_index(self):
        """Convert this variable to a pandas.Index"""
        # n.b. creating a new pandas.Index from an old pandas.Index is
        # basically free as pandas.Index objects are immutable
        assert self.ndim == 1
        return pd.Index(self._data_cached().array, name=self.dims[0])

    # pandas.Index like properties:

    @property
    def name(self):
        return self.dims[0]

    @name.setter
    def name(self, value):
        raise AttributeError('cannot modify name of Coordinate in-place')

    def get_indexer(self, label):
        return self.to_index().get_indexer(label)

    def slice_indexer(self, start=None, stop=None, step=None):
        return self.to_index().slice_indexer(start, stop, step)

    def slice_locs(self, start=None, stop=None):
        return self.to_index().slice_locs(start, stop)

    def get_loc(self, label):
        return self.to_index().get_loc(label)

    @property
    def is_monotonic(self):
        return self.to_index().is_monotonic

    def is_numeric(self):
        return self.to_index().is_numeric()


def broadcast_variables(*variables):
    """Given any number of variables, return variables with matching dimensions
    and broadcast data.

    The data on the returned variables will be a view of the data on the
    corresponding original arrays, but dimensions will be reordered and
    inserted so that both broadcast arrays have the same dimensions. The new
    dimensions are sorted in order of appearence in the first variable's
    dimensions followed by the second variable's dimensions.
    """
    # validate dimensions
    all_dims = OrderedDict()
    for var in variables:
        var_dims = var.dims
        if len(set(var_dims)) < len(var_dims):
            raise ValueError('broadcasting cannot handle duplicate '
                             'dimensions: %r' % list(var_dims))
        for d, s in zip(var_dims, var.shape):
            if d not in all_dims:
                all_dims[d] = s
            elif all_dims[d] != s:
                raise ValueError('operands cannot be broadcast together '
                                 'with mismatched lengths for dimension %r: %s'
                                 % (d, (all_dims[d], s)))
    dims = tuple(all_dims)
    return tuple(var.set_dims(all_dims) if var.dims != dims else var
                 for var in variables)


def _broadcast_variable_data(self, other):
    if all(hasattr(other, attr) for attr
             in ['dims', 'values', 'shape', 'encoding']):
        # `other` satisfies the necessary Variable API for broadcast_variables
        new_self, new_other = broadcast_variables(self, other)
        self_data = new_self.values
        other_data = new_other.values
        dims = new_self.dims
    else:
        # rely on numpy broadcasting rules
        self_data = self.values
        other_data = other
        dims = self.dims
    return self_data, other_data, dims
