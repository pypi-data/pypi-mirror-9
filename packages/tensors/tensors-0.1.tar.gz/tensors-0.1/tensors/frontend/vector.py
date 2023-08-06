import tensors.matrix
import tensors.tensor


class Vector(tensors.tensor.Tensor):
    """
    Vector (one-dimensional tensor) interface.

    The interface declares vector-specific operations.
    """

    def __init__(self, other):
        """
        Convert the object into a vector.

        :param other: the object to be converted
        :type other: a number, a scalar, or a vector
        :raises: :class:`TypeError` if `other` has the wrong type

        If `other` is a number or a scalar, creates an equivalent vector of
        length 1.
        """
        raise NotImplementedError

    def dot(self, other):
        """
        Calculate the inner product of the two vectors.

        :param other: the multiplier
        :type other: a vector of the same length
        :returns: the inner product of the two vectors
        :rtype: a number
        :raises: :class:`AssertionError` if `other` has the wrong length

        The default implementation evaluates ``(self * other).sum()``.
        """
        return (self * other).sum()

    @property
    def length(self):
        """
        Length of the vector.

        The default implementation evaluates ``self.shape[0]``.
        """
        return self.shape[0]

    @classmethod
    def range(Class, length):
        """
        Create a range vector.

        :param length: the required length
        :type length: a positive integer
        :returns: ``[0, 1, ..., length - 1]``
        :rtype: a vector of the specified length
        :raises: :class:`AssertionError` if `length` is not positive

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        raise NotImplementedError

    def replicate(self, count):
        """
        Create a matrix with the identical columns.

        :param count: the number of the columns of the resulting matrix
        :type count: a positive integer
        :returns: a matrix with `count` columns identical to the vector
        :rtype: a matrix of shape ``(self.length, count)``
        :raises: :class:`AssertionError` if `count` is not positive

        The default implementation evaluates ``self.times(self.ones(count))``

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        return self.times(self.ones(count))

    @property
    def shape(self):
        """
        The default implementation evaluates ``(self.length,)``.
        """
        return (self.length,)

    @classmethod
    def step(Class, length, origin=1):
        """
        Create a discretization of the Heaviside step function.

        :param length: the length of the resulting vector
        :type length: a positive integer
        :param origin: the position of the origin
        :type origin: an integer
        :returns: a vector ``[0, 0, ..., 0, 1, 1, ..., 1]`` with exactly
            ``max(0, min(length, origin))`` zeros
        :rtype: a vector of the specified length
        :raises: :class:`AssertionError` if `length` is not positive

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        raise NotImplementedError

    def sum(self):
        """
        The default implementation evaluates
        ``self.dot(self.ones(self.length))``.
        """
        return self.dot(self.ones(self.length))

    def times(self, other):
        """
        Calculate the outer product of the two vectors.

        :param other: the multiplier
        :type other: a vector
        :returns: the outer product of the two vectors
        :rtype: a matrix of shape ``(self.length, other.length)``

        The default implementation evaluates
        ``Matrix(self).dot(Matrix(other).transpose())``.
        """
        Matrix = tensors.matrix.Matrix
        return Matrix(self).dot(Matrix(other).transpose())
