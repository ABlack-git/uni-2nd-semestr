import copy

import pyqtgraph as pg
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt


class CustomStyle:
    def __init__(self):
        self.line_width = None
        self.line_pen = None
        self.line_brush = None

        self.symbol = None
        self.symbol_size = None
        self.symbol_pen = None
        self.symbol_brush = None


class CustomPlot(pg.PlotItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = CustomStyle()
        self.showGrid(y=True, alpha=0.5)
        self.setMouseEnabled(x=False, y=False)

    def plot(self, x: np.ndarray, y: np.ndarray, color=(0, 0, 0), name=None):
        plot_item = CustomPlotItem(x, y, color, self.style, name=name)
        self.addItem(plot_item)
        return plot_item

    def bar_plot(self, x: np.ndarray, y: np.ndarray, color=(0, 0, 0), name=None):
        bar_item = CustomBarItem(x, y, color, style=self.style, name=name)
        self.addItem(bar_item)
        return bar_item

    def scatter_plot(self):
        pass


class BaseCustomItem(pg.GraphicsObject):
    def __init__(self, x: np.ndarray, y: np.ndarray, pen_color, style: CustomStyle, symbol=None, name=None, *args):
        super().__init__(*args)
        self.picture = QtGui.QPicture()
        self.style = copy.deepcopy(style)
        self.style.line_pen = pen_color
        self.style.symbol_pen = pen_color
        self.style.symbol = symbol
        self.name = name
        self.x = x
        self.y = y

    def generatePicture(self):
        raise NotImplementedError()


class CustomBarItem(BaseCustomItem):
    def __init__(self, x: np.ndarray, y: np.ndarray, pen_color, style: CustomStyle, symbol=None, name=None, *args):
        super().__init__(x, y, pen_color, style, symbol, name, *args)
        self._width = 0.9
        self.generatePicture()

    def generatePicture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen(color=(0, 0, 0), width=self.style.line_width))
        painter.setBrush(pg.mkBrush(color=self.style.line_pen))

        for x, y in zip(self.x, self.y):
            x0 = x - (self._width / 2.0)
            rect = QtCore.QRectF(x0, 0, self._width, y)
            painter.drawRect(rect)

        painter.end()

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

    def paint(self, p: QtGui.QPainter, *args):
        p.drawPicture(0, 0, self.picture)

    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        if ax == 0:
            data = self.x
            data_o = self.y
            border = self._width / 2.0
        else:
            data = self.y
            data_o = self.x
            border = 0
        if orthoRange is not None:
            mask = (data_o >= orthoRange[0]) * (data_o <= orthoRange[1])
            data = data[mask]

        if len(data) == 0:
            return None, None

        return np.nanmin(data) - border, np.nanmax(data) + border

    def update_data(self, x, y):
        self.x = x
        self.y = y
        self.generatePicture()
        self.show()
        self.informViewBoundsChanged()


class CustomPlotItem(pg.GraphicsObject):
    def __init__(self, x: np.ndarray, y: np.ndarray, pen_color, style: CustomStyle, symbol=None, name=None, *args):
        super().__init__(*args)
        self.picture = QtGui.QPicture()
        self.style = copy.deepcopy(style)
        self.style.line_pen = pen_color
        self.style.symbol_pen = pen_color
        self.style.symbol = symbol
        self.name = name
        self.x = x
        self.y = y
        self.generatePicture()

    def generatePicture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen(color=self.style.line_pen, width=self.style.line_width))
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
    def __init__(self, size=None, offset=(1, 1)):
        pg.GraphicsWidget.__init__(self)
        pg.GraphicsWidgetAnchor.__init__(self)
        self.layout = QtGui.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.items = []
        self.offset = offset
        self.legend_height = 0
        self.legend_width = 0
        self.parent = None
        if size is not None:
            self.setGeometry(QtCore.QRectF(0, 0, self.size[0], self.size[1]))

    def setParentItem(self, p):
        ret = pg.GraphicsWidget.setParentItem(self, p)
        self.parent = p
        self.parent.sigResized.connect(self.updateSize)
        anchor = (0.5, 0.5)
        self.anchor(itemPos=anchor, parentPos=anchor)
        return ret

    def addItem(self, item):
        label = pg.LabelItem(item.name, color=(0, 0, 0), justify='right')
        sample = CustomLegendItem(item)
        self.items.append((sample, label))
        self.legend_height += max(sample.height(), label.height()) + 3
        self.legend_width = max(self.legend_width, sample.width() + label.width()) + 10
        row = self.layout.rowCount()
        self.layout.addItem(sample, row, 0)
        self.layout.addItem(label, row, 1)
        self.updateSize()

    def updateSize(self):
        self.setGeometry(0, 0, max(self.legend_width, self.parent.screenGeometry().width() - 10), self.legend_height)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width(), self.height())

    def paint(self, p, *args):
        p.setPen(pg.mkPen(0, 0, 0, 100))
        p.setBrush(pg.mkBrush(255, 255, 255, 50))
        p.drawRect(self.boundingRect())


class CustomLegendItem(pg.GraphicsWidget):
    def __init__(self, item):
        super(CustomLegendItem, self).__init__()
        self.item: CustomPlotItem = item

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        p.setPen(pg.mkPen(self.item.style.line_pen, width=self.item.style.line_width))
        p.drawLine(2, 18, 18, 2)


class Slider(QWidget):
    def __init__(self, minimum, maximum, interval=1, parent=None):
        super().__init__(parent)
        self.slider = QSlider(self)
        self.label = QLabel(self)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.label)
        self.h_layout.addWidget(self.slider)

        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(minimum)
        self.slider.setTickInterval(interval)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setOrientation(Qt.Horizontal)
        self.label.setText(str(self.slider.value()))
        self.slider.valueChanged.connect(self.set_value)
        self.resize(self.sizeHint())

    def set_value(self, value):
        self.label.setText(str(value))

    @property
    def value(self):
        return self.slider.value()


class CustomAxis(pg.AxisItem):
    def __init__(self, val_mapping: dict, orientation):
        super().__init__(orientation)
        self.val_mapping = val_mapping

    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            vs = v * scale
            if v in self.val_mapping:
                v_string = self.val_mapping[v]
            else:
                v_string = ""
            strings.append(v_string)
        return strings
