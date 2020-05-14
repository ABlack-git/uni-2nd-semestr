import pyqtgraph as pg
import numpy as np

from palettable.palette import Palette
from pyqtgraph.Qt import QtGui, QtCore


class CustomPlot:
    def __init__(self, palette: Palette, **kwargs):
        self.style = {
            'width': 5,
            'ticks': '',
        }
        self.plt = pg.PlotItem(**kwargs)
        self.plt.showGrid(y=True, alpha=0.5)
        self.palette = palette

    def plot(self, x: np.ndarray, y: np.ndarray):
        plot_item = CustomMultiPLotItem(x, y, self.palette, self.style)
        self.plt.addItem(plot_item)
        return self.plt

    def bar_plot(self):
        pass

    def scatter_plot(self):
        pass


# class CustomPlotItem(pg.GraphicsObject):
#     def __init__(self, x: np.ndarray, y: np.ndarray, palette: Palette, style, *args):
#         super().__init__(*args)
#         self.picture = QtGui.QPicture()
#         order = np.argsort(x)
#         self.x = x[order]
#         self.y = y[order]
#         self.palette = palette
#         self.style = style
#
#         self.generatePicture()
#
#     def generatePicture(self):
#         painter = QtGui.QPainter(self.picture)
#         painter.setPen(pg.mkPen(color=self.palette.colors[0], width=self.style['width']))
#         x1, y1 = self.x[0], self.y[0]
#         for x, y in zip(self.x[1:], self.y[1:]):
#             painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x, y))
#             x1, y1 = x, y
#         painter.end()
#
#     def paint(self, p: QtGui.QPainter, *args):
#         p.drawPicture(0, 0, self.picture)
#
#     def dataBounds(self, ax, frac=1.0, orthoRange=None):
#         if ax == 0:
#             data = self.x
#             data_o = self.y
#         else:
#             data = self.y
#             data_o = self.x
#         if orthoRange is not None:
#             mask = (data_o >= orthoRange[0]) * (data_o <= orthoRange[1])
#             data = data[mask]
#
#         if len(data) == 0:
#             return None, None
#
#         return data.min(), data.max()
#
#     def boundingRect(self):
#         return QtCore.QRectF(self.picture.boundingRect())


class CustomMultiPLotItem(pg.GraphicsObject):
    def __init__(self, x: np.ndarray, y: np.ndarray, palette: Palette, style: dict, *args):
        super().__init__(*args)
        assert len(x.shape) == 1, f'X should be one dimensional vector, instead x.shape is {x.shape}'
        if len(y.shape) > 1:
            assert x.shape[0] >= y.shape[1], f'Y should have the same or fewer number of elemets as X, instead' \
                                             f' x.shape {x.shape} and y.shape {y.shape}'
            self.y = y
        else:
            self.y = np.expand_dims(y, 1).T

        self.style = style
        self.x = x
        self.palette = palette
        self.picture = QtGui.QPicture()
        self.generate_picture()

    def generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        for i, row in enumerate(self.y):
            painter.setPen(pg.mkPen(color=self.palette.colors[i], width=self.style['width']))
            x1, y1 = self.x[0], row[0]
            for x, y in zip(self.x[1:], row[1:]):
                if not np.isnan(x1) and not np.isnan(y1):
                    painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x, y))
                x1, y1 = x, y
        painter.end()

    def paint(self, p: QtGui.QPainter, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

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
