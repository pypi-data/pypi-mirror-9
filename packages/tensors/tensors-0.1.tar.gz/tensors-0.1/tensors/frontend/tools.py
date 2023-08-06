import functools

import tensors.settings


def tensorize(function, accuracy=tensors.settings.DEFAULT_ACCURACY):
    """
    Make the vectorized function applicable to tensors.

    :param function: the function to be tensorized
    :type function: a callable that accepts a number of one-dimensional
        NumPy arrays of equal length and returns a one-dimensional NumPy
        array of the same length
    :param accuracy: an acceptable relative root mean squared error of the
        approximation
    :type accuracy: a non-negative number
    :returns: the tensorized function
    :rtype: a callable that accepts a number of tensors of the same shape (but
        any type) and returns an approximation of the function of the given
        tensors with the specified accuracy
    :raises: :class:`AssertionError` if `accuracy` is negative

    The default implementation delegates approximation to the
    :func:`tensors.tensor.Tensor.approximate` method of the arguments' common
    superclass.

    .. seealso::
        :func:`tensors.tools.tensorized`
    """

    def common_superclass(*instances):
        mros = (type(i).mro() for i in instances)
        mro = next(mros)
        common_mro = set(mro).intersection(*mros)
        return next((c for c in mro if c in common_mro), None)

    @functools.wraps(function)
    def tensorized_function(*args, **kwargs):
        superclass = common_superclass(*args)
        if hasattr(superclass, "approximate"):
            return superclass.approximate(function, accuracy, *args, **kwargs)
        return function(*args, **kwargs)

    assert accuracy >= 0
    return tensorized_function


def tensorized(function=None, accuracy=tensors.settings.DEFAULT_ACCURACY):
    """
    Make the vectorized function applicable to tensors.

    This is a convenient decorator form of :func:`tensors.tools.tensorize`,
    which can be used in one of the two following ways.

    >>> @tensors.tools.tensorized
    >>> def sinc(x):
    >>>     return numpy.sin(x) / x

    >>> @tensors.tools.tensorized(accuracy=1e-6)
    >>> def sinc(x):
    >>>     return numpy.sin(x) / x
    """

    def decorate(function):
        return tensorize(function, accuracy)

    return decorate if function is None else decorate(function)
