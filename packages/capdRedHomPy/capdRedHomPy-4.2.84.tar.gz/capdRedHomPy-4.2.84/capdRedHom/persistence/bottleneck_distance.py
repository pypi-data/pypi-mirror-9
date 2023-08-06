from .diagram import Diagram
import argparse
from gzip import GzipFile
import math
from .build_diagrams_graph import BuildDiagramsGraph

class BottleneckDistance(object):

    def __init__(self, diagram_a, diagram_b, use_infinite, tolerance=0.01):
        self._diagram_a = diagram_a.finite_intervals
        self._diagram_b = diagram_b.finite_intervals

        if use_infinite:
            self._diagram_a.extend(diagram_a.infinite_intervals)
            self._diagram_b.extend(diagram_b.infinite_intervals)

        self.tolerance = tolerance

        self._max = max(diagram_a.max, diagram_b.max)

    @classmethod
    def enabled(cls):
        return BuildDiagramsGraph.enabled()

    def __call__(self):
        a_size = len(self._diagram_a)
        b_size = len(self._diagram_b)

        if a_size == 0 and b_size == 0:
            return 0.0

        return self._bisect_matching()


    def _validate_graph(self, graph):
        a_size = len(self._diagram_a)
        b_size = len(self._diagram_b)
        for idx_a in xrange(a_size):
            if len(graph.adjacent(idx_a)) == 0:
                return False
        for idx_b in xrange(b_size):
            if len(graph.adjacent(idx_b)) == 0:
                return False
        return True

    def _check_matching(self, distance_limit):
        def valid_edge((x1, y1), (x2, y2)):
            x = abs(x1 - x2)
            assert (not math.isnan(x)) and (not math.isinf(x))
            y = abs(y1 - y2)
            y = x if math.isnan(y) or math.isinf(y) else y
            d = max(x, y)

            return d <= distance_limit

        build_graph = BuildDiagramsGraph(self._diagram_a, self._diagram_b)
        graph = build_graph(valid_edge, lambda (a,b), (c,d): None)

        if self._validate_graph(graph):
            matching = graph.maximum_bipartite_matching()
            return len(matching) == len(graph.vs)/2
        else:
            return False

    def _bisect_matching(self):
        start, end = 0.0, self._max
#        assert self._check_matching(end)

        while ((end - start)/2.0 > self.tolerance):
            c = (start + end)/2.0
            if self._check_matching(c):
                end = c
            else:
                start = c

        return end

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--diagram-a', dest='diagram_a',
                        help='diagram file', required=True)
    parser.add_argument('--diagram-b', dest='diagram_b',
                        help='diagram file', required=True)
    parser.add_argument('--shrink', dest='shrink', type=int, required=True)
    parser.add_argument('--only-finite', dest='only_finite',action='store_true')
    args = parser.parse_args()

    diagrams = []

    for diagram_file in [args.diagram_a, args.diagram_b]:
        with open(diagram_file) as _file:
            if diagram_file.endswith('.gz'):
                file = GzipFile(fileobj=_file)
            else:
                file = _file
            diagram = Diagram.read_from(file, args.shrink)
            diagrams.append(diagram)


    distance = BottleneckDistance(diagrams[0], diagrams[1], not args.only_finite)
    print distance()
