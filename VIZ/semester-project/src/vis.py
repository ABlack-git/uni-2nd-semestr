import pyqtgraph as pg
import numpy as np
import pandas as pd

from typing import Dict, Tuple
from src.plot import CustomPlot
from palettable.cartocolors.qualitative import Prism_10


class Trellis:
    def __init__(self, title=''):
        self.title = title
        self.style = {
            'background': 'w'
        }
        self.view = pg.GraphicsView(background=self.style['background'])
        self.layout = pg.GraphicsLayout(border='b')
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle(self.title)
        self.view.resize(800, 600)

    def show(self):
        self.view.show()


class SharedPlotsTrellis(Trellis):
    def __init__(self, title='', cols=3):
        super().__init__(title=title)
        self.plots = []
        self.cols = cols

    def plot(self, x_name: str, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
        self.layout.addLabel(self.title, colspan=self.cols)
        self.layout.nextRow()
        for i, property_name in enumerate(properties):
            plot = CustomPlot(Prism_10, title=property_name)
            self.plots.append(plot)
            self.layout.addItem(plot)
            for item_name, item_frame in kwargs.items():
                data_y = item_frame[property_name].to_numpy()
                data_x = item_frame[x_name].to_numpy()
                plot.plot(data_x, data_y, name=item_name)

            if (i + 1) % self.cols == 0:
                self.layout.nextRow()

    def add_legend(self):
        vb = pg.ViewBox()
        self.layout.addItem(vb, rowspan=self.layout.currentRow, col=self.cols + 1, row=1)
        print(self.layout.currentRow, self.layout.currentCol)
