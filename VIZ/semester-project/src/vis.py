import pyqtgraph as pg
import numpy as np
import pandas as pd

from typing import Dict, Tuple, List, Union
from src.plot import CustomGraph, CustomLegend, Slider, CustomBarItem, CustomPlotItem, CustomAxis
from palettable.cartocolors.qualitative import Prism_10, Bold_10
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class TrellisStyle:
    def __init__(self):
        self.palette = None
        self.border_color = None

        self.title_color = None
        self.title_size = None

        self.text_color = None
        self.text_size = None

        self.subtitle_color = None
        self.subtitle_size = None

        self.line_width = None
        self.background_color = None


DEFAULT_STYLE = TrellisStyle()
DEFAULT_STYLE.palette = Bold_10
DEFAULT_STYLE.background_color = 'w'
DEFAULT_STYLE.line_width = 3
DEFAULT_STYLE.title_size = '20pt'
DEFAULT_STYLE.title_color = (0, 0, 0)
DEFAULT_STYLE.text_size = '12pt'
DEFAULT_STYLE.text_color = (0, 0, 0)
DEFAULT_STYLE.subtitle_color = (0, 0, 0)
DEFAULT_STYLE.subtitle_size = '14pt'


class Trellis:
    def __init__(self, style: TrellisStyle = DEFAULT_STYLE, title=''):
        self.title = title
        self.style = style
        self.view = pg.GraphicsView(background=self.style.background_color)
        self.layout = pg.GraphicsLayout(border=self.style.border_color)
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle(self.title)
        self.view.resize(800, 600)

    def show(self):
        self.view.show()

    def add_title(self, colspan):
        self.layout.addLabel(self.title, colspan=colspan, color=self.style.title_color, size=self.style.title_size)
        self.layout.nextRow()


class TrellisByStats(Trellis):
    def __init__(self, title='', cols=3):
        super().__init__(title=title)
        self.plots = []
        self.cols = cols
        self.num_items = -1
        self.items = []

    def plot(self, x_name: str, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
        self.add_title(self.cols)
        self.num_items = len(kwargs)
        for i, property_name in enumerate(properties):
            plot = CustomGraph()
            plot.setTitle(title=property_name, color=self.style.text_color, size=self.style.text_size)
            plot.style.line_width = self.style.line_width
            self.plots.append(plot)
            self.layout.addItem(plot)
            for j, (item_name, item_frame) in enumerate(kwargs.items()):
                data_y = item_frame[property_name].to_numpy()
                data_x = item_frame[x_name].to_numpy()
                plot_item = plot.plot(data_x, data_y, name=item_name, color=self.style.palette.colors[j])
                self.items.append(plot_item)

            if (i + 1) % self.cols == 0:
                self.layout.nextRow()

    def add_legend(self):
        vb = pg.ViewBox()
        self.layout.addItem(vb, rowspan=self.layout.currentRow, col=self.cols + 1, row=1)
        legend = CustomLegend()
        legend.setParentItem(vb)
        for i in range(self.num_items):
            legend.addItem(self.items[i])
        self.layout.layout.setColumnMaximumWidth(self.cols + 1, max(200, legend.legend_width))
        self.layout.layout.setColumnMinimumWidth(self.cols + 1, legend.legend_width)


# class MultiplePlotsTrellis(Trellis):
#     def __init__(self, title, style=DEFAULT_STYLE):
#         super().__init__(title=title, style=style)
#
#     def plot(self, x_name: str, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
#         self.add_title(len(properties))
#         for i, (item_name, item) in enumerate(kwargs.items()):
#             self.layout.addLabel(text=item_name, colspan=len(properties), color=self.style.subtitle_color,
#                                  size=self.style.subtitle_size)
#             self.layout.nextRow()
#
#             for prop_name in properties:
#                 plot = CustomPlot()
#                 plot.setTitle(title=prop_name, color=self.style.text_color, size=self.style.text_size)
#                 plot.style.line_width = self.style.line_width
#                 self.layout.addItem(plot)
#                 data_x = item[x_name].to_numpy()
#                 data_y = item[prop_name].to_numpy()
#                 plot.plot(x=data_x, y=data_y, color=self.style.palette.colors[i])
#
#             self.layout.nextRow()


class TrellisByPlayerAndStats(Trellis):
    def __init__(self, title, style: TrellisStyle = DEFAULT_STYLE):
        super().__init__(title=title, style=style)
        self.scroll_area = pg.QtGui.QScrollArea()
        self.scroll_area.setWidget(self.view)
        self.view.setFixedHeight(2000)
        self.scroll_area_resize_event = self.scroll_area.resizeEvent
        self.scroll_area.resizeEvent = self._set_view_width

    def _set_view_width(self, event):
        self.scroll_area_resize_event(event)
        self.view.setFixedWidth(self.scroll_area.width())

    def _find_y_min_max(self, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
        min_max: Dict[str, List[float, float]] = {k: [float('inf'), -float('inf')] for k in properties}
        for prop_name in properties:
            for item in kwargs.values():
                min_max[prop_name][0] = min(min_max[prop_name][0], min(item[prop_name].to_numpy()))
                min_max[prop_name][1] = max(min_max[prop_name][1], max(item[prop_name].to_numpy()))
        return min_max

    def _scale_data(self, x_name: str, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
        min_max: Dict[str, List[float, float]] = self._find_y_min_max(properties, **kwargs)

        scaled_data = {item_name: item.copy() for item_name, item in kwargs.items()}

        for prop in properties:
            for item_name, item in kwargs.items():
                if min_max[prop][1] <= 1 and min_max[prop][0] >= 0:
                    continue
                scaled_data[item_name][prop] = (item[prop] - min_max[prop][0]) / min_max[prop][1]
        return scaled_data

    def plot(self, x_name: str, properties: Tuple[str, ...], scale: str = 'noscale', **kwargs: Dict[str, pd.DataFrame]):
        if scale == 'normalize':
            data = self._scale_data(x_name, properties, **kwargs)
        elif scale == 'same_axis':
            min_max = self._find_y_min_max(properties, **kwargs)
            data = kwargs
        else:
            data = kwargs
        self.add_title(len(data))

        for item_name in data.keys():
            self.layout.addLabel(text=item_name, colspan=1, color=self.style.subtitle_color,
                                 size=self.style.subtitle_size)
        self.layout.nextRow()
        for prop_name in properties:
            for i, (item_name, item) in enumerate(data.items()):
                plot = CustomGraph()
                if scale == 'normalize':
                    plot.setYRange(0, 1, padding=0)
                elif scale == 'same_axis':
                    plot.setYRange(0, min_max[prop_name][1], padding=0)
                plot.setTitle(title=prop_name, size=self.style.text_size, color=self.style.text_color)
                plot.style.line_width = self.style.line_width
                self.layout.addItem(plot)
                plot.bar_plot(x=item[x_name].to_numpy(), y=item[prop_name].to_numpy(),
                              color=self.style.palette.colors[i])
            self.layout.nextRow()

    def show(self):
        self.scroll_area.show()


class TrellisWithSlider(Trellis):
    def __init__(self, min_v, max_v, x_name, properties, data, title='', style=DEFAULT_STYLE):
        Trellis.__init__(self, title=title, style=style)
        self.widget = QWidget()
        self.v_layout = QVBoxLayout(self.widget)
        self.num_cols = 3
        self.slider = Slider(min_v, max_v)
        self.v_layout.addWidget(self.view)
        self.v_layout.addWidget(self.slider)
        self.properties: Tuple[str, ...] = properties
        self.x_name: str = x_name
        self.data: Dict[str, pd.DataFrame] = data

        self.x_dict_val_item_name = {k: v for k, v in enumerate(self.data.keys())}
        self.x_dict_item_name_val = {v: k for k, v in enumerate(self.data.keys())}
        self.item_dict: Dict[str, Dict[str, Union[CustomBarItem, CustomPlotItem, CustomGraph]]] = {}

        self.init_plot()
        self.slider.slider.valueChanged.connect(self.update_plots)

    def init_plot(self):
        for i, prop in enumerate(self.properties):
            plot = CustomGraph(
                axisItems={"bottom": CustomAxis(val_mapping=self.x_dict_val_item_name, orientation='bottom')})
            plot.style.line_width = self.style.line_width
            plot.setTitle(title=prop, size=self.style.text_size, color=self.style.text_color)
            self.layout.addItem(plot)
            if prop not in self.item_dict:
                self.item_dict[prop] = {}
            self.item_dict[prop]['plot'] = plot
            for j, (name, item) in enumerate(self.data.items()):
                year_df: pd.DataFrame = item.loc[item[self.x_name] == self.slider.value]
                if year_df.empty:
                    continue
                plot_item = plot.bar_plot(x=np.array([self.x_dict_item_name_val[name]]),
                                          y=year_df[prop].to_numpy(),
                                          color=self.style.palette.colors[j])
                self.item_dict[prop][name] = plot_item
            if (i + 1) % self.num_cols == 0:
                self.layout.nextRow()

    def update_plots(self):
        for prop in self.properties:
            for i, (name, item) in enumerate(self.data.items()):
                plot_item = self.item_dict[prop].get(name, None)
                year_df: pd.DataFrame = item.loc[item[self.x_name] == self.slider.value]
                if plot_item is None and year_df.empty:
                    continue
                elif plot_item is None and not year_df.empty:
                    plot = self.item_dict[prop]['plot']
                    self.item_dict[prop][name] = plot.bar_plot(x=np.array([self.x_dict_item_name_val[name]]),
                                                               y=year_df[prop].to_numpy(),
                                                               color=self.style.palette.colors[i])
                elif plot_item is not None and year_df.empty:
                    plot_item.update_data(x=np.array([self.x_dict_item_name_val[name]]), y=np.array([0]))
                else:
                    plot_item.update_data(x=np.array([self.x_dict_item_name_val[name]]), y=year_df[prop].to_numpy())

    @staticmethod
    def create_trellis_with_slider(x_name: str, properties: Tuple[str, ...], **kwargs: Dict[str, pd.DataFrame]):
        x_min = float('inf')
        x_max = -float('inf')
        for item in kwargs.values():
            x = item[x_name].to_numpy()
            x_min = min(x_min, min(x))
            x_max = max(x_max, max(x))

        return TrellisWithSlider(x_min, x_max, x_name, properties, kwargs)

    def show(self):
        self.widget.show()
