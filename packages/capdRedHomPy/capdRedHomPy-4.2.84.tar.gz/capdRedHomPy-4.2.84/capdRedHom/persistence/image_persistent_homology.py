from .diagram import *


class ImagePersistentHomology(object):

    def __init__(self, image):
        data = [ [p for p in row] for row in image]
        from capdRedHom.impl import capd_impl
        self._impl = capd_impl.ImagePersistentHomology(data)

    def __call__(self, shrink_to=None):
        intervals = self._impl()

        return self.diagram()

    def diagram(self, dim=None, shrink_to=None):
        if dim is None:
            intervals = self._impl.diagram()
        else:
            intervals = self._impl.diagramInDim(dim)

        diagram = Diagram()
        for interval in intervals:
            diagram.add_interval(interval)

        diagram(shrink_to)
        return diagram
