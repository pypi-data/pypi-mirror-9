import numbers
import numpy

import tensors.tensor


class Scalar(tensors.tensor.Tensor):
    """
    Zero-dimensional tensor.

    Instances of this class can be used on a par with ordinary numbers in all
    tensor operations (addition, multiplication, etc.).
    """

    def __add__(self, other):
        if isinstance(other, (numbers.Number, Scalar)):
            return Scalar(self.value + other)
        return self.value + other

    def __eq__(self, other):
        return self.value == other

    def __init__(self, other):
        """
        Convert the object into a scalar.

        :param other: the object to be converted
        :type other: a number or a scalar
        :raises: :class:`TypeError` if `other` has the wrong type
        """
        if isinstance(other, numbers.Number):
            self.value = other
        elif isinstance(other, Scalar):
            self.value = other.value
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, (numbers.Number, Scalar)):
            return Scalar(self.value * other)
        return self.value * other

    def __neg__(self):
        return Scalar(-self.value)

    def __repr__(self):
        return "S(%s)" % numpy.sign(self.value)

    def __rtruediv__(self, other):
        return other / self.value

    def __sub__(self, other):
        if isinstance(other, (numbers.Number, Scalar)):
            return Scalar(self.value - other)
        return self.value - other

    def __truediv__(self, other):
        return Scalar(self.value / other)

    @classmethod
    def approximate(Class, function, accuracy, *args, **kwargs):
        values = [numpy.array([a.value]) for a in args]
        return Class(function(*values, **kwargs)[0])

    def expand(self):
        return numpy.array(self.value)

    @classmethod
    def ones(Class):
        return Class(1)

    @property
    def shape(self):
        return ()

    def sum(self):
        return self.value

    @classmethod
    def zeros(Class):
        return Class(0)
