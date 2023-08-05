import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sys

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import gtk

if __name__ == '__main__':

    file = sys.argv[1]
    points = []

    with open(file, 'r') as input:
        for line in input:
            points.append(map(float, line.split()))

    x = [p[0] for p in points]
    y = [p[1] for p in points]
    if len(points[0]) == 2:
        # 2-dim
        plt.plot(x, y, 'ro')
        plt.show()
    elif len(points[0]) == 3:
        # 3-dim

        z = [p[2] for p in points]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c='r', marker='o')
#        plt.show()
#        plt.savefig(name + ".png")

        win = gtk.Window()
        win.connect("destroy", lambda x: gtk.main_quit())
        win.set_default_size(400,300)
        win.set_title("Embedding in GTK")

        vbox = gtk.VBox()
        win.add(vbox)

        canvas = FigureCanvas(fig)  # a gtk.DrawingArea
        vbox.pack_start(canvas)
        toolbar = NavigationToolbar(canvas, win)
        vbox.pack_start(toolbar, False, False)

        win.show_all()
        gtk.main()
