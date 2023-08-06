import math

class DiagramMeasure(object):

    def __init__(self, diagram, power):
        self._intervals = diagram.finite_intervals
        self._power = power

    def __call__(self):
        measure = 0.0
        for interval in self._intervals:
            measure += (interval[1] - interval[0]) ** self._power

        return measure
