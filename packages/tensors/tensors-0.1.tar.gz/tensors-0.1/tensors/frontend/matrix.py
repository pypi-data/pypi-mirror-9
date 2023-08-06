import tensors.tensor
import tensors.vector


class Matrix(tensors.tensor.Tensor):
    """
    Matrix (two-dimensional tensor) interface.

    The interface declares matrix-specific operations.
    """

    def __init__(self, other):
        """
        Convert the object into a matrix.

        :param other: the object to be converted
        :type other: a number, a scalar, a vector, or a matrix

        If `other` is a vector, creates an equivalent column-vector.
        If `other` is a number or a scalar, creates an equivalent 1-by-1 matrix.
        """
        raise NotImplementedError

    def dot(self, other):
        """
        Calculate a matrix-specific product of the two tensors.

        :param other: the multiplier
        :type other: a matrix, a vector, or a one-dimensional NumPy array
        :returns: the matrix-matrix product if `other` is a matrix, or the
            matrix-vector product otherwise
        :rtype: same as the type of `other`, the shape is adjusted accordingly
        :raises: :class:`AssertionError` if `other` has the wrong shape
        """
        raise NotImplementedError

    @property
    def height(self):
        """
        Number of the rows of the matrix.

        The default implementation evaluates ``self.shape[0]``.
        """
        return self.shape[0]

    @classmethod
    def identity(Class, order):
        """
        Create an identity matrix.

        :param order: the order of the resulting matrix
        :type order: a positive integer
        :returns: the identity matrix of the specified order
        :rtype: a matrix of shape ``(order, order)``
        :raises: :class:`AssertionError` if `order` is not positive

        .. seealso::
            :attr:`tensors.tensor.Tensor.shape`
        """
        raise NotImplementedError

    @classmethod
    def ones(Class, height, width):
        return Class(tensors.vector.Vector.ones(height).replicate(width))

    @property
    def shape(self):
        """
        The default implementation evaluates ``(self.height, self.width)``.
        """
        return (self.height, self.width)

    def sum(self):
        """
        The default implementation evaluates
        ``self.dot(Vector.ones(self.width)).sum()``.
        """
        Vector = tensors.vector.Vector
        return self.dot(Vector.ones(self.width)).sum()

    def times(self, other):
        """
        Calculate the Kronecker product of the two matrices.

        :param other: the multiplier
        :type other: a matrix
        :returns: the Kronecker product of the two matrices
        :rtype: a matrix of shape
            ``(self.height * other.height, self.width * other.width)``
        """
        raise NotImplementedError

    def transpose(self):
        """
        Calculate the transpose of the matrix.

        :returns: the transpose of the matrix
        :rtype: a matrix of shape ``(self.width, self.height)``
        """
        raise NotImplementedError

    @property
    def width(self):
        """
        Number of the columns of the matrix.

        The default implementation evaluates ``self.shape[1]``.
        """
        return self.shape[1]
