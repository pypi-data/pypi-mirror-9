from .algorithms import *

class Complex(object):

    def __init__(self, impl):
        self._impl = impl

    @property
    def capd(self):
        return self._impl

    @property
    def dim(self):
        return self._impl.dim()

    def betti(self):
        return BettiNumbersOverZ(self)()
