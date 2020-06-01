from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pandas as pd
from src.plot import CustomGraph
from palettable.cartocolors.qualitative import Prism_10
import numpy as np

batting = pd.read_csv('data/batting.csv')
derek_jeter = batting.loc[(batting['First Name'] == 'Derek') & (batting['Last Name'] == 'Jeter')]
johnsma01 = batting.loc[batting['Player ID code'] == 'johnsma01']
print(derek_jeter.to_string())
print(johnsma01.to_string())

# years = derek_jeter['Year'].to_numpy()
# jet_ba = derek_jeter['BA'].to_numpy()
# joh_ba = johnsma01['BA'].to_numpy()
# jet_pa = derek_jeter['PA'].to_numpy()
# joh_pa = johnsma01['PA'].to_numpy()
#
# joh_year = johnsma01['Year']
#
# ba_frame = np.full(shape=(2, years.size), fill_value=np.nan)
# ba_frame[0, :] = jet_ba
# for i, year in enumerate(joh_year):
#     ba_frame[1, years == year] = joh_ba[i]
#
# print(ba_frame)

app = QtGui.QApplication([])
view = pg.GraphicsView(background='w')

layout = pg.GraphicsLayout()
view.setCentralItem(item=layout)
view.show()
view.setWindowTitle('test')
view.resize(800, 600)

# p1 = CustomPlot(Prism_10, title='BA')
# layout.addItem(p1.plot(years, ba_frame))

l = layout.addLabel('Derek Jeter', colspan=3, )
l.boundingRect()
layout.nextRow()
pg.setConfigOption('antialias', True)
p1 = CustomGraph(Prism_10, title='BA', antialias=True)
p2 = CustomGraph(Prism_10)
p3 = CustomGraph(Prism_10)
x = derek_jeter['Year'].to_numpy()
y1 = derek_jeter['BA'].to_numpy()
y2 = derek_jeter['PA'].to_numpy()
y3 = derek_jeter['TB'].to_numpy()

layout.addItem(p1.plot(x=x, y=y1))
layout.addItem(p2.plot(x=x, y=y2))
layout.addItem(p3.plot(x=x, y=y3))
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
