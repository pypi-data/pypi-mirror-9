import math

class BuildDiagramsGraph:

    def __init__(self, diagram_a, diagram_b):
        self._diagram_a = diagram_a
        self._diagram_b = diagram_b

    @classmethod
    def enabled(cls):
        try:
            import igraph
            return True
        except ImportError:
            return False

    def __call__(self, valid_edge, distance):
        import igraph
        a_size = len(self._diagram_a)
        b_size = len(self._diagram_b)
        graph = igraph.Graph(2*(a_size + b_size)) # groups plus placeholders for diagonal

        def vertex_type(idx):
            if idx < a_size:
                return True
            elif idx >= a_size and idx < a_size + b_size:
                return False
            elif idx >= a_size + b_size and idx < a_size + b_size + a_size:
                return False
            elif idx >= a_size + b_size + a_size and idx < a_size + b_size + a_size + b_size:
                return True
            else:
                raise RuntimeError("Wrong index")

        graph.vs["type"] = map(vertex_type, xrange(len(graph.vs)))

        for idx_a in xrange(a_size):
            for idx_b in xrange(b_size):
                good_group = (math.isinf(self._diagram_a[idx_a][1]) ^ math.isinf(self._diagram_b[idx_b][1])) == 0
                if good_group and valid_edge(self._diagram_a[idx_a], self._diagram_b[idx_b]):
                    graph.add_edge(idx_a, a_size + idx_b, weight=distance(self._diagram_a[idx_a], self._diagram_b[idx_b]))
                # diagonal-diagonal always
                graph.add_edge(a_size + b_size + idx_a, a_size + b_size + a_size + idx_b, weight=0.0)

        def add_diagonal_projection(diagram, start_index):
            diagonal = lambda ((x, y)): (x, x)
            for idx in xrange(len(diagram)):
                if valid_edge(diagram[idx], diagonal(diagram[idx])):
                    graph.add_edge(start_index + idx, a_size + b_size + start_index + idx, weight=distance(diagram[idx], diagonal(diagram[idx])))

        add_diagonal_projection(self._diagram_a, 0)
        add_diagonal_projection(self._diagram_b, a_size)


        return graph
