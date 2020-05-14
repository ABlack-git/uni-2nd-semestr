import pandas as pd

from pyqtgraph.Qt import QtCore, QtGui
from src.vis import SharedPlotsTrellis

batting = pd.read_csv('data/batting.csv')
player_1: pd.DataFrame = batting.loc[(batting['First Name'] == 'Derek') & (batting['Last Name'] == 'Jeter')]
player_2: pd.DataFrame = batting.loc[batting['Player ID code'] == 'johnsma01']
p1_name = player_1['First Name'].iloc[0] + ' ' + player_1['Last Name'].iloc[0]
p2_name = player_2['First Name'].iloc[0] + ' ' + player_2['Last Name'].iloc[0]
col_names = ('Runs', 'Hits', 'Homeruns', 'BA', 'PA', 'TB', 'SlugPct', 'OBP', 'OPS', 'BABIP')

# for col_name in col_names:
#     data_y[col_name] = {p1_name: player_1[col_name].to_numpy(), p2_name: player_2[col_name].to_numpy()}

app = QtGui.QApplication([])
plot = SharedPlotsTrellis("Demo")
data = {p1_name: player_1, p2_name: player_2}
plot.plot('Year', col_names, cols=3, **data)
plot.show()
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()