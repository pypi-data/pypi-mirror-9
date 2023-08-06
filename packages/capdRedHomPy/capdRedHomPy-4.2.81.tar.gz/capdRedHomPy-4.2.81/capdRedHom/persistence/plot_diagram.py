import sys
from .diagram import Diagram
import argparse
from gzip import GzipFile

class PlotDiagram(object):
    MARKER = ['o','+']

    def __init__(self, diagram):
        self._diagram = diagram

    def __call__(self, plot):
        finite_intervals = self._diagram.finite_intervals
        infinite_intervals = [ (b, self._diagram.max * 2) for b, d in self._diagram.infinite_intervals]

        if len(finite_intervals) > 0:
            plot.scatter(*zip(*finite_intervals), marker='.', c='blue')

        if len(infinite_intervals) > 0:
            plot.scatter(*zip(*infinite_intervals), marker='+', c='red')

        plot.plot([self._diagram.min, self._diagram.max], [self._diagram.min, self._diagram.max])



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='N', nargs='+',
                        help='diagram files')
    parser.add_argument('--shrink', dest='shrink', type=int)
    args = parser.parse_args()

    nrows = len(args.files)
    shrink = args.shrink

    import matplotlib.pyplot as plt

    plt.figure(1)
    plt.gcf().set_size_inches(20, 10*len(args.files))

    for idx, filename in enumerate(args.files):
        print filename
        plt.subplot(nrows, 1, idx + 1)
        plt.title(filename)
        with open(filename) as _file:
            if filename.endswith('.gz'):
                file = GzipFile(fileobj=_file)
            else:
                file = _file
            diagram = Diagram.read_from(file, shrink)
            plot = PlotDiagram(diagram)
            plot(plt)

    plt.show()
    print "Save to out.png"
    plt.savefig('out.png', dpi=50)
