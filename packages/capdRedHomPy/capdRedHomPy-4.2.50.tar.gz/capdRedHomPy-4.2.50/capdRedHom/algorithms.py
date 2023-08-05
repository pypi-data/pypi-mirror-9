class BettiNumbersOverZ(object):

    def __init__(self, complex):
        self._complex = complex

    def __call__(self):
        from .impl import capd_impl
        complex_impl = self._complex.capd
        betti = capd_impl.BettiNumbersOverZ(complex_impl)()
        return dict(enumerate(betti))

class FundamentalGroup(object):

    def __init__(self, complex):
        self._complex = complex

    def __call__(self):
        from .impl import capd_impl
        complex_impl = self._complex.capd
        relators = capd_impl.FundamentalGroup(complex_impl)()
        return relators
