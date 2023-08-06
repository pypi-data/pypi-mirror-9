from tensors.frontend.matrix import *

import numbers
import numpy
import tt

import tensors
import tensors.helpers
import tensors.settings


class Matrix(Matrix):

    def __add__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            ones = tensors.Vector.ones(self.height).replicate(self.width)
            return self + ones * other
        assert other.shape == self.shape
        return self._from_qtt(self._qtt + other._qtt)

    def __init__(self, other):
        if isinstance(other, Matrix):
            self._qtt = other._qtt
        elif isinstance(other, tensors.Vector):
            qtt = other._qtt
            self._qtt = tt.matrix(qtt, n=qtt.n, m=([1] * qtt.d))
        elif isinstance(other, (numbers.Number, tensors.Scalar)):
            self._qtt = (self.ones(1, 1) * other)._qtt
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            return self._from_qtt(other * self._qtt)
        assert other.shape == self.shape
        s, o = self._qtt, other._qtt
        if self.height > 2 or self.width > 2:
            qtt = tt.matrix(s.tt * o.tt, n=s.n, m=s.m)
        else:
            cores = [tt.matrix.to_list(s)[0] * tt.matrix.to_list(o)[0]]
            qtt = tt.matrix.from_list(cores)
        return self._from_qtt(qtt)

    def __neg__(self):
        return self._from_qtt(-self._qtt)

    def __repr__(self):
        cars = [c.shape[1 : 3] for c in tt.matrix.to_list(self._qtt)]
        return ":".join("x".join(str(s) for s in c) for c in cars)

    def __sub__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            ones = tensors.Vector.ones(self.height).replicate(self.width)
            return self - ones * other
        assert other.shape == self.shape
        return self._from_qtt(self._qtt - other._qtt)

    @classmethod
    def _from_qtt(Class, qtt):
        result = Class.__new__(Class)
        result._qtt = qtt
        return result

    def _squeeze(self):

        def convolve(left, right):
            return numpy.tensordot(left, right, axes=1)

        def swap_cores(left, right):
            n, m, k = 4 * left.shape[0], 2 * right.shape[3], 2 * left.shape[3]
            convolved = convolve(left, right)
            if left.shape[1] == 1:
                order = (0, 3, 2, 1, 4, 5)
            else:
                order = (0, 1, 4, 3, 2, 5)
            supercore = convolved.transpose(order).reshape(n, m, order="F")
            a, b = tensors.helpers.ab(supercore, k)
            new_left_shape = (left.shape[0], right.shape[1], right.shape[2], -1)
            new_left = a.reshape(new_left_shape, order="F")
            new_right_shape = (-1, left.shape[1], left.shape[2], right.shape[3])
            new_right = b.reshape(new_right_shape, order="F")
            return new_left, new_right

        def merge_cores(left, right):
            supercore = convolve(left, right).transpose(0, 1, 3, 2, 4, 5)
            left_shape = left.shape[:3] + (1,)
            right_shape = (1,) + right.shape[1:]
            merged_shape = [l * r for l, r in zip(left_shape, right_shape)]
            return supercore.reshape(merged_shape, order="F")

        cores = tt.matrix.to_list(self._qtt)
        i = 1
        while i < len(cores):
            left, right = cores[i - 1], cores[i]
            modes = left.shape[1 : 3], right.shape[1 : 3]
            impeccable = [((1, 2), (1, 2)), ((2, 1), (2, 1)),
                          ((2, 2), (1, 2)), ((2, 2), (2, 1)),
                          ((2, 2), (2, 2))]
            disordered = [((1, 2), (2, 2)), ((2, 1), (2, 2))]
            if modes in impeccable:
                i += 1
            else:
                if modes in disordered:
                    cores[i - 1], cores[i] = swap_cores(left, right)
                else:
                    cores[i - 1] = merge_cores(left, right)
                    del cores[i]
                i = max(1, i - 1)
        self._qtt = tt.matrix.from_list(cores)
        return self

    @classmethod
    def approximate(Class, function, accuracy, *args, **kwargs):
        assert all(a.shape == args[0].shape for a in args)
        approximated_function = tensors.helpers.approximate(function, accuracy)
        inner_tt = approximated_function(*[a._qtt.tt for a in args], **kwargs)
        qtt = tt.matrix(inner_tt, n=args[0]._qtt.n, m=args[0]._qtt.m)
        return Class._from_qtt(qtt)

    def dot(self, other):
        if isinstance(other, Matrix):
            assert other.height == self.width
            return self._from_qtt(self._qtt * other._qtt)._squeeze()
        if isinstance(other, tensors.Vector):
            assert other.length == self.width
            cores = tt.tensor.to_list(other._qtt)
            padding = len(self._qtt.m) - len(other._qtt.n)
            cores += [numpy.array([[[1]]])] * padding
            qtt = tt.matvec(self._qtt, tt.tensor.from_list(cores))
            return other._from_qtt(qtt)._squeeze()
        other = numpy.asanyarray(other, dtype=numpy.float, order="F")
        assert other.size == self.width
        return self._qtt * other

    def expand(self):
        return self._qtt.full()

    @property
    def height(self):
        mode_sizes = [int(s) for s in self._qtt.n]
        return tensors.helpers.product(mode_sizes)

    @classmethod
    def identity(Class, order):
        assert order >= 1
        if order == 1:
            qtt = tt.matrix.from_list([numpy.array([[[[1]]]])])
        else:
            qtt = tt.eye(2, tensors.helpers.ilog2(order))
        return Class._from_qtt(qtt)

    def round(self, accuracy=tensors.settings.DEFAULT_ACCURACY):
        assert accuracy >= 0
        if self._qtt.tt.d > 2:
            return self._from_qtt(self._qtt.round(accuracy))
        return self

    def times(self, other):
        return self._from_qtt(tt.kron(other._qtt, self._qtt))._squeeze()

    def transpose(self):
        cores = tt.matrix.to_list(self._qtt)
        transposed_cores = [c.transpose([0, 2, 1, 3]) for c in cores]
        return self._from_qtt(tt.matrix.from_list(transposed_cores))

    @property
    def width(self):
        mode_sizes = [int(s) for s in self._qtt.m]
        return tensors.helpers.product(mode_sizes)
