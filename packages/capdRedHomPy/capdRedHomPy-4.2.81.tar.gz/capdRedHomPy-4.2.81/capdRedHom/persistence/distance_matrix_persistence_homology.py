from .diagram import *


class DistanceMatrixPersistentHomology(object):

    def __init__(self, distance_matrix, max_dim, degreeLimit):
        data = [ [p for p in row] for row in distance_matrix]
        from capdRedHom.impl import capd_impl
        self._impl = capd_impl.DistanceMatrixPersistentHomology(data, max_dim, degreeLimit)

    def __call__(self):
        self._impl()

    def diagram(self, dim=-1, shring_to=None):
        diagram = Diagram()

        for interval in self._impl.diagram(dim):
            diagram.add_interval(interval)

        diagram(shring_to)
        return diagram
