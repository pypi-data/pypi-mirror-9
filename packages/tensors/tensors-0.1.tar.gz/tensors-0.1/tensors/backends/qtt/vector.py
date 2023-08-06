from tensors.frontend.vector import *

import numbers
import numpy
import tt

import tensors
import tensors.helpers
import tensors.settings


class Vector(Vector):

    def __add__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            return self + self.ones(self.length) * other
        assert other.length == self.length
        return self._from_qtt(self._qtt + other._qtt)

    def __init__(self, other):
        if isinstance(other, Vector):
            self._qtt = other._qtt
        elif isinstance(other, (numbers.Number, tensors.Scalar)):
            self._qtt = (self.ones(1) * other)._qtt
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            return self._from_qtt(other * self._qtt)
        assert other.length == self.length
        if self.length > 2:
            return self._from_qtt(self._qtt * other._qtt)
        s = tt.tensor.to_list(self._qtt)[0]
        o = tt.tensor.to_list(other._qtt)[0]
        return self._from_qtt(tt.tensor.from_list([s * o]))

    def __neg__(self):
        return self._from_qtt(-self._qtt)

    def __repr__(self):
        cars = [c.shape[1 : 2] for c in tt.tensor.to_list(self._qtt)]
        return ":".join("x".join(str(s) for s in c) for c in cars)

    def __sub__(self, other):
        if isinstance(other, (numbers.Number, tensors.Scalar)):
            return self - self.ones(self.length) * other
        assert other.length == self.length
        return self._from_qtt(self._qtt - other._qtt)

    @classmethod
    def _from_qtt(Class, qtt):
        result = Class.__new__(Class)
        result._qtt = qtt
        return result

    def _squeeze(self):
        cores = tt.tensor.to_list(self._qtt)
        squeezed_cores = [cores[0]]
        for core in cores[1:]:
            last_core = squeezed_cores[-1]
            if last_core.shape[1] == core.shape[1] == 2:
                squeezed_cores.append(core)
                continue
            convolved = numpy.tensordot(last_core, core, axes=1)
            squeezed_shape = (last_core.shape[0], -1, core.shape[2])
            squeezed = convolved.reshape(squeezed_shape, order="F")
            squeezed_cores[-1] = squeezed
        self._qtt = tt.tensor.from_list(squeezed_cores)
        return self

    @classmethod
    def approximate(Class, function, accuracy, *args, **kwargs):
        assert all(a.shape == args[0].shape for a in args)
        approximated_function = tensors.helpers.approximate(function, accuracy)
        qtt = approximated_function(*[a._qtt for a in args], **kwargs)
        return Class._from_qtt(qtt)

    def dot(self, other):
        assert other.length == self.length
        return tt.dot(self._qtt, other._qtt)

    def expand(self):
        return self._qtt.full().reshape(self.length, order="F")

    @property
    def length(self):
        mode_sizes = [int(s) for s in self._qtt.n]
        return tensors.helpers.product(mode_sizes)

    @classmethod
    def range(Class, length):
        assert length >= 1
        if length == 1:
            qtt = tt.tensor.from_list([numpy.array([[[0]]])])
        else:
            qtt = tt.xfun(2, tensors.helpers.ilog2(length))
        return Class._from_qtt(qtt)

    def round(self, accuracy=tensors.settings.DEFAULT_ACCURACY):
        assert accuracy >= 0
        if self._qtt.d > 2:
            return self._from_qtt(self._qtt.round(accuracy))
        return self

    @classmethod
    def ones(Class, length):
        assert length >= 1
        if length == 1:
            qtt = tt.tensor.from_list([numpy.array([[[1]]])])
        else:
            qtt = tt.ones(2, tensors.helpers.ilog2(length))
        return Class._from_qtt(qtt)

    @classmethod
    def step(Class, length, origin=1):
        assert length >= 1
        if origin <= 0:
            return Class.ones(length)
        elif origin >= length:
            return Class.zeros(length)
        qtt = tt.stepfun(2, tensors.helpers.ilog2(length), origin)
        return Class._from_qtt(qtt)
