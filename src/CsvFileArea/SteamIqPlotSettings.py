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
        #---------------------Row 3---------------------------
        self._lbl_consider_act_factor = QtWidgets.QLabel('Consider activity factor')
        self._cbx_sonsider_act_factor = QtWidgets.QCheckBox()

        self._lyt_opts_three.addWidget(self._lbl_consider_act_factor)
        self._lyt_opts_three.addWidget(self._cbx_sonsider_act_factor)

        #---------------------Row 4---------------------------
        self._lbl_leak_units = QtWidgets.QLabel('Units for leakage')
        self._cmb_leak_units = QtWidgets.QComboBox()
        self._cmb_leak_units.addItems(LeakUnits)

        self._lbl_conv_coef = QtWidgets.QLabel('Conversion coef')
        self._ltx_conv_coef = QtWidgets.QLineEdit('1.0')
        self._ltx_conv_coef.setValidator(QtGui.QDoubleValidator(0.0, 999999.999999, 6, notation=QtGui.QDoubleValidator.StandardNotation))

        self._lyt_opts_four = QtWidgets.QHBoxLayout()
        self._lyt_opts_four .addWidget(self._lbl_leak_units)
        self._lyt_opts_four.addWidget(self._cmb_leak_units)
        self._lyt_opts_four .addWidget(self._lbl_conv_coef)
        self._lyt_opts_four.addWidget(self._ltx_conv_coef)

        self._lyt_main.addLayout(self._lyt_opts_four)
    
    def _convert_series(self, srs):
        try:
            conv_coef = float(self._ltx_conv_coef.text())
            return srs*conv_coef
        except Exception as error:
            raise Exception(f'Conversion coefficient is wrong')
        
    def plot(self, ax, resample_options, service_breaks):
        srs_list = super().plot(ax, resample_options, service_breaks)
        ax.set_ylabel(ax.get_ylabel() + ', ' + leak_units_symbol_map[self._cmb_leak_units.currentText()])
        return srs_list


