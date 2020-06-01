import pandas as pd

from pyqtgraph.Qt import QtCore, QtGui
from src.vis import TrellisByStats, TrellisByPlayerAndStats, TrellisWithSlider

batting = pd.read_csv('data/batting.csv')
player_1: pd.DataFrame = batting.loc[(batting['First Name'] == 'Derek') & (batting['Last Name'] == 'Jeter')]
player_2: pd.DataFrame = batting.loc[batting['Player ID code'] == 'johnsma01']
player_3: pd.DataFrame = batting.loc[(batting['First Name'] == 'Kris') & (batting['Last Name'] == 'Bryant')]
player_4: pd.DataFrame = batting.loc[(batting['First Name'] == 'Josh') & (batting['Last Name'] == 'Hamilton')]
player_5: pd.DataFrame = batting.loc[(batting['First Name'] == 'Miguel') & (batting['Last Name'] == 'Cabrera')]
p1_name = player_1['First Name'].iloc[0] + ' ' + player_1['Last Name'].iloc[0]
p2_name = player_2['First Name'].iloc[0] + ' ' + player_2['Last Name'].iloc[0]
p3_name = player_3['First Name'].iloc[0] + ' ' + player_3['Last Name'].iloc[0]
p4_name = player_4['First Name'].iloc[0] + ' ' + player_4['Last Name'].iloc[0]
p5_name = player_5['First Name'].iloc[0] + ' ' + player_5['Last Name'].iloc[0]
col_names = ('Runs', 'Hits', 'Homeruns', 'BA', 'PA', 'TB', 'SlugPct', 'OBP', 'OPS', 'BABIP', 'Games', 'Runs Batted In')

data = {p1_name: player_1, p2_name: player_2, p3_name: player_3, p4_name: player_4, p5_name: player_5}
app = QtGui.QApplication([])
plot = TrellisByStats("Demo", cols=4)
plot.plot('Year', col_names, **data)
plot.add_legend()
plot.show()

plot3 = TrellisByPlayerAndStats(title='Demo3')
plot3.plot('Year', col_names, scale='same_axis', **data)
plot3.show()

plot3 = TrellisWithSlider.create_trellis_with_slider('Year', col_names, **data)
plot3.show()

if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
