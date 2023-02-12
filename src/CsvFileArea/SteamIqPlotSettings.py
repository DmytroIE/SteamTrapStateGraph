from PySide6 import QtWidgets, QtCore, QtGui

from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.utils.settings import LeakUnits

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.settings import LineColors, line_colors_map, leak_units_symbol_map

class SteamIqPlotSettings(IndPlotSettings):
    def __init__(self, 
                 df, 
                 leak_col_name, 
                 cycle_col_name, 
                 def_color=LineColors.Orange, 
                 def_is_plotted=False):
        
        IndPlotSettings.__init__(self, df, leak_col_name, def_color, def_is_plotted)
        self._cycle_col_name = cycle_col_name



    def _create_ui(self, def_color, def_if_plotted):
        super()._create_ui(def_color, def_if_plotted)
        #---------------------Row 1---------------------------
        lbl_leak_units = QtWidgets.QLabel('Units for leakage')
        self._cmb_leak_units = QtWidgets.QComboBox()
        self._cmb_leak_units.addItems(LeakUnits)

        lbl_conv_coef = QtWidgets.QLabel('Conversion coef')
        self._ltx_conv_coef = QtWidgets.QLineEdit('1.0')
        self._ltx_conv_coef.setValidator(QtGui.QDoubleValidator(0.0, 999999.999999, 6, notation=QtGui.QDoubleValidator.StandardNotation))

        lyt_opts_one = QtWidgets.QHBoxLayout()
        lyt_opts_one .addWidget(lbl_leak_units)
        lyt_opts_one.addWidget(self._cmb_leak_units)
        lyt_opts_one .addWidget(lbl_conv_coef)
        lyt_opts_one.addWidget(self._ltx_conv_coef)

        self._lyt_main.addLayout(lyt_opts_one)
    
    def _convert_series(self, srs):
        try:
            conv_coef = float(self._ltx_conv_coef.text())
            return srs*conv_coef
        except Exception as error:
            raise Exception(f'Conversion coefficient is wrong')
        
    def plot(self, ax, resample_options, service_breaks):
        super().plot(ax, resample_options, service_breaks)
        ax.set_ylabel(ax.get_ylabel() + ', ' + leak_units_symbol_map[self._cmb_leak_units.currentText()])


