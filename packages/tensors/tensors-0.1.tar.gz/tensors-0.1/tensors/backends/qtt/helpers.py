import functools
import operator
import numpy
import tt


def product(iterable):
    return functools.reduce(operator.mul, iterable[1:], iterable[0])


def ilog2(x):
    result = 1
    while 2**result < x:
        result += 1
    return result


def ab(matrix, rank):
    u, s, v = numpy.linalg.svd(matrix, full_matrices=False)
    return u[:, :rank], numpy.diag(s[:rank]).dot(v[:rank, :])


def approximate(function, accuracy):

    def approximated_function(*args, **kwargs):

        def wrapped_function(samples):
            return function(*samples.transpose(), **kwargs)

        error_states = numpy.geterr()
        numpy.seterr(divide="ignore", invalid="ignore")
        result, error = tt.multifuncrs2(args, wrapped_function, eps=accuracy,
            verb=0, return_dy=True)
        if error > accuracy:
            raise RuntimeError("approximation failed to converge")
        numpy.seterr(**error_states)
        return result

    return approximated_function
