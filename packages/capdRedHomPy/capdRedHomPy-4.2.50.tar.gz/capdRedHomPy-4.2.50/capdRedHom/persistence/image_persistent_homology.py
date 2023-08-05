from .diagram import *


class ImagePersistentHomology(object):

    def __init__(self, image):
        data = [ [p for p in row] for row in image]
        from capdRedHom.impl import capd_impl
        self._impl = capd_impl.ImagePersistentHomology(data)

    def __call__(self, shring_to=None):
        intervals = self._impl()

        diagram = Diagram()
        for interval in intervals:
            diagram.add_interval(interval)

        diagram(shring_to)
        return diagram
