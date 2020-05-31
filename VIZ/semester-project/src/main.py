import pandas as pd

from pyqtgraph.Qt import QtCore, QtGui
from src.vis import SharedPlotsTrellis, MultiplePlotsTrellis, SideBySideTrellis, TrellisWithSlider

batting = pd.read_csv('data/batting.csv')
player_1: pd.DataFrame = batting.loc[(batting['First Name'] == 'Derek') & (batting['Last Name'] == 'Jeter')]
player_2: pd.DataFrame = batting.loc[batting['Player ID code'] == 'johnsma01']
p1_name = player_1['First Name'].iloc[0] + ' ' + player_1['Last Name'].iloc[0]
p2_name = player_2['First Name'].iloc[0] + ' ' + player_2['Last Name'].iloc[0]
col_names = ('Runs', 'Hits', 'Homeruns', 'BA', 'PA', 'TB', 'SlugPct', 'OBP', 'OPS', 'BABIP')

data = {p1_name: player_1, p2_name: player_2}
app = QtGui.QApplication([])
# plot = SharedPlotsTrellis("Demo")
# plot.plot('Year', col_names, **data)
# plot.add_legend()
# plot.show()
#
# plot2 = MultiplePlotsTrellis(title='Demo2')
# plot2.plot('Year', col_names, **data)
# plot2.show()
#
# plot3 = SideBySideTrellis(title='Demo3')
# plot3.plot('Year', col_names, scale='same_axis', **data)
# plot3.show()

plot3 = TrellisWithSlider.create_trellis_with_slider('Year', col_names, **data)
plot3.show()

if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
