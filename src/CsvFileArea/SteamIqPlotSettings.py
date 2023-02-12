from PySide6 import QtWidgets

from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.utils.settings import LeakUnits

class SteamIqPlotSettings(IndPlotSettings):
    def __init__(self, df, leak_col_name, cycle_col_name):
        IndPlotSettings.__init__(self, df, leak_col_name)
        self._cycle_col_name = cycle_col_name



    def _create_ui(self):
        super()._create_ui()
        #---------------------Row 3---------------------------
        lbl_leak_units = QtWidgets.QLabel('Units for leakage')
        self._cmb_leak_units = QtWidgets.QComboBox()
        self._cmb_leak_units.addItems(LeakUnits)

        lyt_opts_three = QtWidgets.QHBoxLayout()
        lyt_opts_three .addWidget(lbl_leak_units)
        lyt_opts_three.addWidget(self._cmb_leak_units)
        #lyt_opts_three .addWidget()
        #lyt_opts_three.addWidget()

        #---------------------Row 4---------------------------
        lbl_is_integral_calc = QtWidgets.QLabel('Calc integral')
        self._cbx_is_integral_calc = QtWidgets.QCheckBox()
        lbl_is_integral_shown = QtWidgets.QLabel('Show on graph')
        self._cbx_is_integral_shown = QtWidgets.QCheckBox()
        lyt_opts_four = QtWidgets.QHBoxLayout()
        lyt_opts_four .addWidget(lbl_is_integral_calc)
        lyt_opts_four.addWidget(self._cbx_is_integral_calc)
        lyt_opts_four .addWidget(lbl_is_integral_shown)
        lyt_opts_four.addWidget(self._cbx_is_integral_shown)

        self._lyt_main.addLayout(lyt_opts_three)
        self._lyt_main.addLayout(lyt_opts_four)      