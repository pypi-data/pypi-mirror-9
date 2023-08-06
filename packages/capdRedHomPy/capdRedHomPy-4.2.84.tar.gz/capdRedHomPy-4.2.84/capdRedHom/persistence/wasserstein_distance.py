from .diagram import Diagram
import argparse
from gzip import GzipFile
import math
from .build_diagrams_graph import BuildDiagramsGraph


class WassersteinDistance(object):
    INF = float('inf')

    def __init__(self, diagram_a, diagram_b, use_infinite):
        self._diagram_a = diagram_a.finite_intervals
        self._diagram_b = diagram_b.finite_intervals

        if use_infinite:
            self._diagram_a.extend(diagram_a.infinite_intervals)
            self._diagram_b.extend(diagram_b.infinite_intervals)

        self._max = max(diagram_a.max, diagram_b.max)

    @classmethod
    def enabled(cls):
        return BuildDiagramsGraph.enabled()

    def __call__(self):
        a_size = len(self._diagram_a)
        b_size = len(self._diagram_b)

        if a_size == 0 and b_size == 0:
            return 0.0

        build_graph = BuildDiagramsGraph(self._diagram_a, self._diagram_b)
        graph = build_graph(lambda (x1, y1), (x2, y2): True, self._distance)

        from munkres import Munkres
        munkres = Munkres()

        incidence_matrix, row_vertices, col_vertices = graph.get_incidence()
        adjacency = graph.get_adjacency(attribute='weight')

        for row_idx, row_v in enumerate(row_vertices):
            for col_idx, col_v in enumerate(col_vertices):
                if incidence_matrix[row_idx][col_idx]:
                    incidence_matrix[row_idx][col_idx] = adjacency[row_v][col_v]
                else:
                    incidence_matrix[row_idx][col_idx] = self.INF

        indexes = munkres.compute(incidence_matrix)
        assert len(indexes) == len(graph.vs)/2, (len(indexes), len(graph.vs)/2)

        total = 0
        for row, column in indexes:
            total += incidence_matrix[row][column]

        return total

    def _distance(self, (x1, y1), (x2, y2)):
        x = abs(x1 - x2)
        assert (not math.isnan(x)) and (not math.isinf(x))
        y = abs(y1 - y2)
        y = x if math.isnan(y) or math.isinf(y) else y
        d = max(x, y)
        return float(d)
