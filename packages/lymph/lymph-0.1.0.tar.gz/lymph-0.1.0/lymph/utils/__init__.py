from __future__ import absolute_import, division


import collections
import importlib
import math
import uuid


class Undefined(object):
    def __repr__(self):
        return "Undefined"

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False


Undefined = Undefined()


def import_object(module_name, object_path=None):
    if not object_path:
        if ':' not in module_name:
            raise ValueError("cannot import object %r" % module_name)
        module_name, object_path = module_name.split(':')
    mod = importlib.import_module(module_name)
    obj = mod
    for objname in object_path.split('.'):
        obj = getattr(obj, objname)
    return obj


def make_id():
    return uuid.uuid4().hex


_sqrt2 = math.sqrt(2)

class Accumulator(object):
    def __init__(self):
        self.n = 0
        self.sum = 0
        self.square_sum = 0
        self._mean = None
        self._stddev = None

    def add(self, value):
        self.n += 1
        self.sum += value
        self.square_sum += value * value
        self._mean = None
        self._stddev = None

    def remove(self, value):
        self.n -= 1
        self.sum -= value
        self.square_sum -= value * value
        self._mean = None
        self._stddev = None

    @property
    def mean(self):
        if not self.n:
            return 0.
        if self._mean is None:
            self._mean = self.sum / self.n
        return self._mean

    @property
    def stddev(self):
        if not self.n:
            return 0.
        if self._stddev is None:
            mean = self.mean
            self._stddev = math.sqrt(self.square_sum / self.n - mean * mean)
        return self._stddev

    @property
    def stats(self):
        return {'mean': self.mean, 'stddev': self.stddev, 'n': self.n}


class SampleWindow(Accumulator):
    def __init__(self, n=100, factor=1):
        super(SampleWindow, self).__init__()
        self.size = n
        self.factor = factor
        self.values = collections.deque([])
        self.total = Accumulator()

    def __len__(self):
        return len(self.values)

    def is_full(self):
        return len(self.values) == self.size

    def add(self, value):
        value = value * self.factor
        super(SampleWindow, self).add(value)
        self.total.add(value)
        if self.is_full():
            self.remove(self.values.popleft())
        self.values.append(value)

    def p(self, value):
        """
        returns the probability for samples greater than `value` given a normal
        distribution with mean and standard deviation derived from this window.
        """
        if self.stddev == 0:
            return 1. if value == self.mean else 0.
        return 1 - math.erf(abs(value * self.factor - self.mean) / (self.stddev * _sqrt2))
