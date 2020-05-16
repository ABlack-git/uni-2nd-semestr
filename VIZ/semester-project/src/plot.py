import pyqtgraph as pg
import numpy as np

from palettable.palette import Palette
from pyqtgraph.Qt import QtGui, QtCore


class CustomPlot(pg.PlotItem):
    def __init__(self, palette: Palette, symbol=False, **kwargs):
        super().__init__(**kwargs)
        self.style = {
            'line_width': 2,
            'symbol_size': 3,
        }
        self.showGrid(y=True, alpha=0.5)
        self.palette = palette

    def plot(self, x: np.ndarray, y: np.ndarray, name=None):
        plot_item = CustomPlotItem(x, y, self.palette.colors[len(self.items)], self.style, name=name)
        self.addItem(plot_item)
        return plot_item

    def bar_plot(self):
        pass

    def scatter_plot(self):
        pass

class CustomPlotItem(pg.GraphicsObject):
    def __init__(self, x: np.ndarray, y: np.ndarray, pen_color, style, symbol=None, name=None, *args):
        super().__init__(*args)
        self.picture = QtGui.QPicture()
        self.opts = {
            'line_pen': pen_color,
            'symbol_pen': pen_color,
            'symbol': symbol,
        }
        self.name = name
        self.style = style
        self.x = x
        self.y = y
        self.generatePicture()

    def generatePicture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen(color=self.opts['line_pen'], width=self.style['line_width']))
        x1, y1 = self.x[0], self.y[0]
        for x, y in zip(self.x[1:], self.y[1:]):
            painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x, y))
            x1, y1 = x, y
        painter.end()

    def paint(self, p: QtGui.QPainter, *args):
        p.drawPicture(0, 0, self.picture)

    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        if ax == 0:
            data = self.x
            data_o = self.y
        else:
            data = self.y
            data_o = self.x
        if orthoRange is not None:
            mask = (data_o >= orthoRange[0]) * (data_o <= orthoRange[1])
            data = data[mask]

        if len(data) == 0:
            return None, None

        return np.nanmin(data), np.nanmax(data)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class CustomLegend(pg.GraphicsWidget, pg.GraphicsWidgetAnchor):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
