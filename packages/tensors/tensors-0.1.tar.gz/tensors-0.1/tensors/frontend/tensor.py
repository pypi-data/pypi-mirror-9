import tensors.settings


class Tensor:
    """
    Tensor (multi-dimensional real array) interface.

    The interface declares operations common for all tensors.
    """

    def __add__(self, other):
        """
        Add the two tensors, or add the number to the tensor.

        :param other: the addend
        :type other: a number or a tensor of the same type and shape
        :returns: the element-wise sum of the two tensors if `other` is a
            tensor, or the tensor increased by `other` element-wise if `other`
            is a number
        :rtype: a tensor of the same type and shape
        :raises: :class:`AssertionError` if `other` has the wrong shape

        This operation is commutative.

        The default implementation evaluates ``self - (-other)``.
        """
        return self - (-other)

    def __mul__(self, other):
        """
        Multiply the two tensors, or multiply the tensor by the number.

        :param other: the multiplier
        :type other: a number or a tensor of the same type and shape
        :returns: the Hadamard product of the two tensors if `other` is a
            tensor, or the tensor multiplied by `other` element-wise if
            `other` is a number
        :rtype: a tensor of the same type and shape
        :raises: :class:`AssertionError` if `other` has the wrong shape

        This operation is commutative.
        """
        return NotImplemented

    def __neg__(self):
        """
        Negate the tensor.

        :returns: the tensor negated element-wise
        :rtype: a tensor of the same type and shape

        The default implementation evaluates ``self * (-1)``.
        """
        return self * (-1)

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return -(self - other)

    def __sub__(self, other):
        """
        Subtract the two tensors, or subtract the number from the tensor.

        :param other: the subtrahend
        :type other: a number or a tensor of the same type and shape
        :returns: the difference between the two tensors if `other` is a tensor,
            or the tensor decreased by `other` element-wise if `other` is a
            number
        :rtype: a tensor of the same type and shape
        :raises: :class:`AssertionError` if `other` has the wrong shape

        This operation is anticommutative.

        The default implementation evaluates ``self + (-other)``.
        """
        return self + (-other)

    def __truediv__(self, other):
        """
        Divide the tensor by the number.

        :param other: the divisor
        :type other: a number
        :returns: the tensor divided by `other` element-wise
        :rtype: a tensor of the same type and shape
        :raises: :class:`ZeroDivisionError` if `other` is zero

        The default implementation evaluates ``self * (1 / other)``.
        """
        return self * (1 / other)

    @classmethod
    def approximate(Class, function, accuracy, *args, **kwargs):
        """
        Approximate the function of the given tensor arguments.

        :param function: the function to be approximated
        :type function: a callable that accepts a number of one-dimensional
            NumPy arrays of equal length and returns a one-dimensional NumPy
            array of the same length
        :param accuracy: an acceptable relative root mean squared error of the
            approximation
        :type accuracy: a non-negative number
        :param args: the arguments to be passed to `function`
        :type args: tensors of the same type and shape
        :param kwargs: optional keyword arguments to be passed to `function`
        :returns: an approximation of the function of the given tensor arguments
            with the specified accuracy
        :rtype: a tensor of the same type and shape as `args`
        :raises: :class:`AssertionError` if `accuracy` is negative,
            :class:`AssertionError` if `args` have different shapes, and
            :class:`RuntimeError` if the approximation process fails to converge

        .. seealso::
            :func:`tensors.tools.tensorize`
        """
        raise NotImplementedError

    def expand(self):
        """
        Calculate the full representation of the tensor.

        :returns: the full representation of the tensor
        :rtype: a NumPy array of the same shape
        :raises: :class:`MemoryError` if the result does not fit into memory

        .. warning::
            Care must be taken since the result might not fit into memory.
        """
        raise NotImplementedError

    @classmethod
    def ones(Class, *shape):
        """
        Create a tensor with all ones.

        :param shape: the required shape
        :type shape: a tuple of positive integers
        :returns: a tensor with all ones
        :rtype: a tensor of the specified shape
        :raises: :class:`AssertionError` if `shape` has non-positive elements

        The default implementation evaluates ``Class.zeros(*shape) + 1``.

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        return Class.zeros(*shape) + 1

    def round(self, accuracy=tensors.settings.DEFAULT_ACCURACY):
        """
        Round the tensor.

        :param accuracy: an acceptable relative root mean squared error of the
            approximation
        :type accuracy: a non-negative number
        :returns: an approximation of the tensor with the specified accuracy
        :rtype: a tensor of the same type and shape
        :raises: :class:`AssertionError` if `accuracy` is negative

        This operation is intended to reduce the complexity of the internal
        representation of the tensor.

        The default implementation does not change the tensor.
        """
        assert accuracy >= 0
        return self

    @property
    def shape(self):
        """
        Shape of the tensor.

        The shape of a tensor is a tuple holding the sizes of the tensor along
        each dimension.

        .. note::
            The admissible sizes along all dimensions are guaranteed to form the
            same submonoid of the monoid of all positive integers under
            multiplication for all tensors, e.g. the set of all non-negative
            integer powers of 2, unless otherwise specified.
            Every size parameter supplied to this package is implicitly rounded
            up to the closest submonoid element, e.g.
            :func:`tensors.vector.Vector.range` might create a vector of length
            32, even though you request a vector of length 17.
        """
        raise NotImplementedError

    def sum(self):
        """
        Calculate the sum of all the elements of the tensor.
        """
        raise NotImplementedError

    @classmethod
    def zeros(Class, *shape):
        """
        Create a tensor with all zeros.

        :param shape: the required shape
        :type shape: a tuple of positive integers
        :returns: a tensor with all zeros
        :rtype: a tensor of the specified shape
        :raises: :class:`AssertionError` if `shape` has non-positive elements

        The default implementation evaluates ``Class.ones(*shape) * 0``.

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        return Class.ones(*shape) * 0
