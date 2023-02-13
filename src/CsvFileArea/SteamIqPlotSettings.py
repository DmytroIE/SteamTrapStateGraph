from PySide6 import QtWidgets, QtCore, QtGui

import matplotlib as mpl

from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.utils.settings import LeakUnits

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.settings import LineColors, AuxLineColors, aux_line_colors_map, leak_units_symbol_map
from src.utils.utils import steam_Iq_make_cold_state_interval_list_for_series, extract_series_from_df, convert_sbs_to_pd_format, split_one_series_by_sb, resample_series

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
        self._lbl_calc_act_factor = QtWidgets.QLabel('Calc activity factor')
        self._cbx_calc_act_factor = QtWidgets.QCheckBox()
        self._lbl_num_of_points = QtWidgets.QLabel('Number of points')
        self._spb_num_of_points = QtWidgets.QSpinBox()
        self._spb_num_of_points.setRange(2, 24)
        self._lbl_use_act_factor_in_integr = QtWidgets.QLabel('Use in integral')
        self._cbx__use_act_factor_in_integr  = QtWidgets.QCheckBox()

        self._lyt_opts_three.addWidget(self._lbl_calc_act_factor)
        self._lyt_opts_three.addWidget(self._cbx_calc_act_factor )
        self._lyt_opts_three.addWidget(self._lbl_num_of_points )
        self._lyt_opts_three.addWidget(self._spb_num_of_points )
        self._lyt_opts_three.addWidget(self._lbl_use_act_factor_in_integr)
        self._lyt_opts_three.addWidget(self._cbx__use_act_factor_in_integr )

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
        if self._cbx_calc_act_factor.isChecked():
            for list_ in self._cold_state_interval_lists_list:
                for item in list_:
                    # x0, x1 = ax.get_xlim()
                    # start_x = (mpl.dates.date2num(item[0].to_pydatetime()) - x0) / (x1-x0)
                    # end_x = (mpl.dates.date2num(item[1].to_pydatetime()) - x0) / (x1-x0)
                    ax.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=aux_line_colors_map[AuxLineColors.Lime], alpha=0.3)

        return srs_list

    def _prepare_plot_data(self, resample_options, service_breaks):
        srs_list = super()._prepare_plot_data(resample_options, service_breaks)
        if self._cbx_calc_act_factor.isChecked():
            cycle_srs = extract_series_from_df(self._df, resample_options['plot_from'], resample_options['plot_to'], self._cycle_col_name)
            service_breaks = convert_sbs_to_pd_format(service_breaks)

            cycle_srs_list = split_one_series_by_sb(cycle_srs, service_breaks)
            cycle_srs_list = resample_series(cycle_srs_list, resample_options)
            self._cold_state_interval_lists_list = []
            num_of_points = self._spb_num_of_points.value()
            for csrs, srs in zip(cycle_srs_list, srs_list):
                l = steam_Iq_make_cold_state_interval_list_for_series(csrs, srs, num_of_points)
                self._cold_state_interval_lists_list.append(l)
            #print(self._cold_state_interval_lists_list)
        return srs_list
