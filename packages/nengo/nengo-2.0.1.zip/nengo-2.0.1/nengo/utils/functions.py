from __future__ import absolute_import

import numpy as np

from nengo.utils.compat import is_number, OrderedDict, iteritems


def piecewise(data):
    """Create a piecewise constant function from a dictionary.

    Given an input of data={0: 0, 0.5: 1, 0.75: -1, 1: 0} this will generate a
    function that returns 0 up until t=0.5, then outputs a 1 until t=0.75,
    then a -1 until t=1, and then returns 0 after that. This is meant as a
    shortcut for::

        def function(t):
            if t < 0.5:
                return 0
            elif t < 0.75
                return 1
            elif t < 1:
                return -1
            else:
                return 0

    The keys in the dictionary must be times (floats or ints). The values in
    the data dictionary can be floats, lists, or functions that return
    floats or lists. All lists must be of the same length.

    For times before the first specified time, it will default to zero (of
    the correct length). This means the above example can be simplified to::

        piecewise({0.5: 1, 0.75: -1, 1: 0})

    Parameters
    ----------
    data : dict
        The values to change to. Keys are the beginning time for the value.
        Values can be int, float, list, or functions that return those.

    Returns
    -------
    function:
        A function that takes a variable t and returns the corresponding
        value from the dictionary.

    Examples
    --------

      >>> func = piecewise({0.5: 1, 0.75: -1, 1: 0})
      >>> func(0.2)
      [0]
      >>> func(0.58)
      [1]

      >>> func = piecewise({0.5: [1, 0], 0.75: [0, 1]})
      >>> func(0.2)
      [0,0]
      >>> func(0.58)
      [1,0]
      >>> func(100)
      [0,1]

      >>> import math
      >>> func = piecewise({0: math.sin, 0.5: math.cos})
      >>> func(0.499)
      [0.47854771647582706]
      >>> func(0.5)
      [0.8775825618903728]

    """

    # first, sort the data (to simplify finding the right element
    # when calling the function)
    output_length = None  # the dimensionality of the returned values
    for time in data:
        if not is_number(time):
            raise TypeError('Keys must be times (floats or ints), not "%s"'
                            % repr(time.__class__))

        # figure out the length of this item
        if callable(data[time]):
            length = np.asarray(data[time](0.0)).size
        else:
            data[time] = np.asarray(data[time])
            length = data[time].size

        # make sure this is the same length as previous items
        if length != output_length and output_length is not None:
            raise ValueError('Invalid data for piecewise function: '
                             'time %4g has %d items instead of %d' %
                             (time, length, output_length))
        output_length = length

    # make a default output of 0 when t before what was passed
    data[np.finfo(float).min] = np.zeros(output_length)
    ordered_data = OrderedDict(sorted(iteritems(data)))

    # build the function to return
    def piecewise_function(t, data=ordered_data):
        # get the t we'll use for output
        for time in (time for time in data if time <= t):
            out_t = time

        # if it's a function, call it
        if callable(data[out_t]):
            return np.asarray(data[out_t](t))
        return data[out_t]
    return piecewise_function
