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
        self.layout = pg.GraphicsLayout()
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle(self.title)
        self.view.resize(800, 600)

    def show(self):
        self.view.show()


class SharedPlotsTrellis(Trellis):
    def __init__(self, title=''):
        super().__init__(title=title)

    def plot(self, x_name: str, properties: Tuple[str, ...], cols=3, **kwargs: Dict[str, pd.DataFrame]):
        y: Dict[str, Dict[str, np.ndarray]] = {k: {} for k in properties}
        x: Dict[str, np.ndarray] = {}
        for item_name, item_frame in kwargs.items():
            x[item_name] = item_frame[x_name].to_numpy()
            for property_name in properties:
                y[property_name][item_name] = item_frame[property_name].to_numpy()
        self._plot(y=y, x=x, cols=cols)

    def _plot(self, y: Dict[str, Dict[str, np.ndarray]], x: Dict[str, np.ndarray], cols=3):
        """

        :param x: Dict[item_name, x]
        :param y: Dict[property: Dict[item_name: ndarray]]
        :param cols: number of columns in layout
        :return:
        """
        self.layout.addLabel(self.title, colspan=cols)
        self.layout.nextRow()
        x_axis_vals = np.sort(np.unique(np.concatenate([arr for arr in x.values()])))
        num_items = len(x)
        properties = {}
        item_index = {}
        for property_name, items in y.items():
            property_data = np.full(shape=(num_items, x_axis_vals.size), fill_value=np.nan)
            for i, (item_name, values) in enumerate(items.items()):
                item_index[item_name] = i
                item_x_values = x[item_name]
                for j, value in enumerate(values):
                    property_data[i, x_axis_vals == item_x_values[j]] = value

            properties[property_name] = property_data

        for i, (property_name, property_data) in enumerate(properties.items()):
            plot = CustomPlot(Prism_10, title=property_name)
            self.layout.addItem(plot.plot(x_axis_vals, property_data))
            if (i + 1) % cols == 0:
                self.layout.nextRow()
