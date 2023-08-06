from .complex import *

class SimplicialComplex(Complex):
    pass

    def __init__(self, simplices):
        super(SimplicialComplex, self).__init__(SimplicialComplex._create(simplices))

    @classmethod
    def _create(cls, simplices):
        from .impl import capd_impl
        impl = capd_impl.SimplicialComplex()
        for s in simplices:
            impl.insert(sorted(s))

        return impl
