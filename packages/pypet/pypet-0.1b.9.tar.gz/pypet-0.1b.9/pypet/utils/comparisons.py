"""Module containing utility functions to compare parameters and results"""

__author__ = 'Robert Meyer'

from collections import Sequence, Mapping, Set

try:
    from future_builtins import zip
except ImportError:  # not 2.6+ or is 3.x
    try:
        from itertools import izip as zip  # < 2.5 or 3.x
    except ImportError:
        pass
import numpy as np
import pandas as pd
import scipy.sparse as spsp

import pypet.pypetconstants as pypetconstants
import pypet.compat as compat


def results_equal(a, b):
    """Compares two result instances

    Checks full name and all data. Does not consider the comment.

    :return: True or False

    :raises: ValueError if both inputs are no result instances

    """
    if a.v_is_parameter or b.v_is_parameter:
        raise ValueError('Both inputs are not results.')

    if a.v_is_parameter or b.v_is_parameter:
        return False

    if not a.v_name == b.v_name:
        return False

    if not a.v_location == b.v_location:
        return False

    if not a.v_full_name == b.v_full_name:
        return False

    if hasattr(a, '_data') and not hasattr(b, '_data'):
        return False

    if hasattr(a, '_data'):
        akeyset = set(a._data.keys())
        bkeyset = set(b._data.keys())

        if akeyset != bkeyset:
            return False

        for key in a._data:
            val = a._data[key]
            bval = b._data[key]

            if not nested_equal(val, bval):
                return False

    return True


def parameters_equal(a, b):
    """Compares two parameter instances

    Checks full name, data, and ranges. Does not consider the comment.

    :return: True or False

    :raises: ValueError if both inputs are no parameter instances

    """
    if (not b.v_is_parameter and
            not a.v_is_parameter):
        raise ValueError('Both inputs are not parameters')

    if (not b.v_is_parameter or
            not a.v_is_parameter):
        return False

    if not a.v_name == b.v_name:
        return False

    if not a.v_location == b.v_location:
        return False

    if not a.v_full_name == b.v_full_name:
        return False

    if a.f_is_empty() and b.f_is_empty():
        return True

    if a.f_is_empty() != b.f_is_empty():
        return False

    if not a._values_of_same_type(a.f_get(), b.f_get()):
        return False

    if not a._equal_values(a.f_get(), b.f_get()):
        return False

    if a.f_has_range() != b.f_has_range():
        return False

    if a.f_has_range():
        if a.f_get_range_length() != b.f_get_range_length():
            return False

        for myitem, bitem in zip(a.f_get_range(), b.f_get_range()):
            if not a._values_of_same_type(myitem, bitem):
                return False
            if not a._equal_values(myitem, bitem):
                return False

    return True


def nested_equal(a, b):
    """Compares two objects recursively by their elements, also handling numpy objects.

    Assumes hashable items are not mutable in a way that affects equality.
    Based on the suggestion from HERE_, thanks again Lauritz V. Thaulow :-)

    .. _HERE: http://stackoverflow.com/questions/18376935/best-practice-for-equality-in-python

    """
    try:
        if a is b:
            return True
        # for types that support __eq__
        try:
            custom_eq = a.__eq__(b)  # Best way I came up with to check in python 2 and 3
            # if equality is implemented
            if isinstance(custom_eq, (bool, np.bool_)):
                return custom_eq
        except (AttributeError, NotImplementedError, TypeError, ValueError):
            pass

        # Check equality according to type type [sic].
        if a is None:
            return b is None
        if isinstance(a, (compat.unicode_type, compat.bytes_type)):
            return a == b
        if isinstance(a, pypetconstants.PARAMETER_SUPPORTED_DATA):
            return a == b
        if isinstance(a, (pd.Panel, pd.Panel4D)):
            return nested_equal(a.to_frame(), b.to_frame())
        if spsp.isspmatrix(a):
            if a.nnz == 0:
                return b.nnz == 0
            else:
                return np.all((a == b).data)
        if isinstance(a, (pd.DataFrame, pd.Series)):
            try:
                new_frame = a == b
                new_frame = new_frame | (pd.isnull(a) & pd.isnull(b))
                if isinstance(new_frame, pd.DataFrame):
                    return np.all(new_frame.as_matrix())
                else:
                    eq = new_frame.all() # In older pandas versions,
                    # series do not support as_matrix
                    if isinstance(eq, (bool, np.bool_)):
                        return eq
                    else:
                        raise ValueError('')
            except ValueError:
                # The Value Error can happen if the data frame is of dtype=object and contains
                # numpy arrays. Numpy array comparisons do not evaluate to a single truth value
                if isinstance(a, pd.DataFrame):
                    for name in a:
                        cola = a[name]
                        if not name in b:
                            return False
                        colb = b[name]
                        if not len(cola) == len(colb):
                            return False
                        for idx, itema in enumerate(cola):
                            itemb = colb[idx]
                            if not nested_equal(itema, itemb):
                                return False
                else:
                    if not len(a) == len(b):
                        return False
                    for idx, itema in enumerate(a):
                        itemb = b[idx]
                        if not nested_equal(itema, itemb):
                            return False
                return True
        if isinstance(a, np.ndarray):
            if a.shape != b.shape:
                return False
            return np.all(a == b)
        if isinstance(a, Sequence):
            return all(nested_equal(x, y) for x, y in zip(a, b))
        if isinstance(a, Mapping):
            if set(a.keys()) != set(b.keys()):
                return False
            return all(nested_equal(a[k], b[k]) for k in a.keys())
        if isinstance(a, Set):
            return a == b

        if hasattr(a, '__dict__'):
            if not hasattr(b, '__dict__'):
                return False

            if set(a.__dict__.keys()) != set(b.__dict__.keys()):
                return False

            return all(nested_equal(a.__dict__[k], b.__dict__[k]) for k in a.__dict__.keys())

        return False

    except Exception:
        return False