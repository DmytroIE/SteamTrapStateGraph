from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral, split_one_series_by_sb, resample_series, convert_sbs_to_pd_format, extract_series_from_df
from src.utils.settings import LineColors, AuxLineColors, StatusColors, line_colors_map, status_colors_map, LeakUnits
from src.utils.SteamIqToolSet import SteamIqToolSet

from src.CsvFileArea.CsvFileArea import CsvFileArea
from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.CsvFileArea.SteamIqPlotSettings import SteamIqPlotSettings



class SteamIqCsvFileArea(CsvFileArea):
    def __init__(self, plt):
        CsvFileArea.__init__(self, plt)

    def _fill_custom_area(self):
        
        #----Row 1---
        self._rbn_plot_activity_map = QtWidgets.QRadioButton('Plot activity map')
        self._rbn_plot_activity_map.setChecked(True)
        self._rbn_plot_activity_map.toggled.connect(lambda: self._change_plot_opts('Activity map'))
        self._what_to_print = 'Activity map'
 
        self._gbx_plot_activity_map  = QtWidgets.QGroupBox()
        #self._lbl_add_leak_graph = QtWidgets.QLabel('Add leak graph')
        # gbx_plot_activity_map.setTitle('Parameters')
        self._cbx_add_leak_graph = QtWidgets.QCheckBox('Add leak graph')


        self._lyt_plot_act_map = QtWidgets.QVBoxLayout(self._gbx_plot_activity_map)
        self._lyt_act_map_one = QtWidgets.QHBoxLayout()
        self._lyt_act_map_one.addWidget(self._rbn_plot_activity_map)
        self._lyt_act_map_one.addWidget(self._cbx_add_leak_graph)
        #self._lyt_act_map_one.addWidget(self._lbl_leak_graph_color)
        #self._lyt_act_map_one.addWidget(self._cmb_leak_graph_color)

        self._lyt_plot_act_map.addLayout(self._lyt_act_map_one)

        #----Row 2---
        self._rbn_plot_leak_graph = QtWidgets.QRadioButton('Plot leak graph')
        self._rbn_plot_leak_graph.toggled.connect(lambda: self._change_plot_opts('Leak graph'))

        self._gbx_plot_leak_graph  = QtWidgets.QGroupBox()
        self._lbl_y_label = QtWidgets.QLabel('Y Axis name')
        self._ltx_y_label = QtWidgets.QLineEdit()
        self._ltx_y_label.setText('Leak')
        self._cbx_amap_in_bg = QtWidgets.QCheckBox('Map in bg')
        #self._lbl_calc_integral = QtWidgets.QLabel('Calc integral')
        self._cbx_calc_integral = QtWidgets.QCheckBox('Calc integral')
        #self._lbl_calc_integral = QtWidgets.QLabel('Green zone')
        self._cbx_use_green_zone = QtWidgets.QCheckBox('Green zone')
        self._lbl_leak_units = QtWidgets.QLabel('Units for leakage')
        self._cmb_leak_units = QtWidgets.QComboBox()
        self._cmb_leak_units.addItems(LeakUnits)
        self._cmb_leak_units.setCurrentText(LeakUnits.Mass)
        self._lbl_pressure = QtWidgets.QLabel('Pres, barg')
        self._ltx_pressure = QtWidgets.QLineEdit('5.0')
        self._ltx_pressure.setValidator(QtGui.QDoubleValidator(0.0, 999.9, 1, notation=QtGui.QDoubleValidator.StandardNotation))
        self._lbl_orifice_diam = QtWidgets.QLabel('Orif diam, mm')
        self._ltx_orifice_diam = QtWidgets.QLineEdit('4.0')
        self._ltx_orifice_diam.setValidator(QtGui.QDoubleValidator(0.0, 999.9, 1, notation=QtGui.QDoubleValidator.StandardNotation))
        self._lbl_efficiency = QtWidgets.QLabel('Efficiency, %')
        self._ltx_efficiency = QtWidgets.QLineEdit('80.0')
        self._ltx_efficiency.setValidator(QtGui.QDoubleValidator(0.0, 100.0, 0, notation=QtGui.QDoubleValidator.StandardNotation))

        self._lyt_plot_leak_graph = QtWidgets.QVBoxLayout(self._gbx_plot_leak_graph)
        self._lyt_plot_leak_graph_one = QtWidgets.QHBoxLayout()
        self._lyt_plot_leak_graph_one.addWidget(self._lbl_y_label)
        self._lyt_plot_leak_graph_one.addWidget(self._ltx_y_label)
        self._lyt_plot_leak_graph_one.addWidget(self._cbx_amap_in_bg)
        self._lyt_plot_leak_graph_one.addWidget(self._cbx_calc_integral)
        self._lyt_plot_leak_graph_one.addWidget(self._cbx_use_green_zone )
        self._lyt_plot_leak_graph_one.addWidget(self._lbl_leak_units)
        self._lyt_plot_leak_graph_one.addWidget(self._cmb_leak_units)
        self._lyt_plot_leak_graph_two = QtWidgets.QHBoxLayout()
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_pressure)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_pressure)
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_orifice_diam)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_orifice_diam)
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_efficiency)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_efficiency)


        self._lyt_plot_leak_graph.addLayout(self._lyt_plot_leak_graph_one)
        self._lyt_plot_leak_graph.addLayout(self._lyt_plot_leak_graph_two)

        #----Row 3---
        self._gbx_other_opts  = QtWidgets.QGroupBox('Other options')
        self._lbl_y_axis_from = QtWidgets.QLabel('Y axis start')
        self._spb_y_axis_from = QtWidgets.QSpinBox()
        self._spb_y_axis_from.setRange(-5, 100)
        self._spb_y_axis_from.setValue(0)
        self._lbl_y_axis_to = QtWidgets.QLabel('Y axis end')
        self._spb_y_axis_to = QtWidgets.QSpinBox()
        self._spb_y_axis_to.setRange(0, 100)
        self._spb_y_axis_to.setValue(50)
        self._lbl_leak_graph_color = QtWidgets.QLabel('Leak line color')
        self._cmb_leak_graph_color = QtWidgets.QComboBox()
        self._cmb_leak_graph_color.addItems(LineColors)
        self._cmb_leak_graph_color.setCurrentText(LineColors.White)

        self._lyt_other_opts = QtWidgets.QVBoxLayout(self._gbx_other_opts)
        self._lyt_other_opts_one = QtWidgets.QHBoxLayout()
        self._lyt_other_opts_one.addWidget(self._lbl_y_axis_from)
        self._lyt_other_opts_one.addWidget(self._spb_y_axis_from)
        self._lyt_other_opts_one.addWidget(self._lbl_y_axis_to)
        self._lyt_other_opts_one.addWidget(self._spb_y_axis_to)
        self._lyt_other_opts_one.addWidget(self._lbl_leak_graph_color)
        self._lyt_other_opts_one.addWidget(self._cmb_leak_graph_color)

        self._lyt_other_opts.addLayout(self._lyt_other_opts_one)

        #-Adding to the main layout---
        self._lyt_params_area.addWidget(self._rbn_plot_activity_map)
        self._lyt_params_area.addWidget(self._gbx_plot_activity_map)
        self._lyt_params_area.addWidget(self._rbn_plot_leak_graph)
        self._lyt_params_area.addWidget(self._gbx_plot_leak_graph)
        self._lyt_params_area.addWidget(self._gbx_other_opts)
    
    def _change_plot_opts(self, opt):
        self._what_to_print = opt

        
    def _load_csv_file(self, path, params):
        date_col_name = params['date_col_name']
        col_sep = params['col_sep']
        if col_sep == 'Tab':
            col_sep = '\t' 
        self._leak_col_name = params['leak_col_name']
        self._cycle_col_name = params['cycle_col_name']
            
        data = pd.read_csv(path, 
                                 sep=col_sep, 
                                 header=0, 
                                 usecols=[date_col_name, self._leak_col_name, self._cycle_col_name],
                                 dtype={self._leak_col_name:'float64', self._cycle_col_name: 'float64'},
                                 parse_dates=[date_col_name], 
                                 index_col=date_col_name)
        # print('raw data')
        # print(data)
        self._data = SteamIqToolSet.fill_data_gaps_with_nans(data)
        # print('after filling gaps')
        # print(self._data)
        SteamIqToolSet.set_sample_statuses(self._data)
        # print('after statuses')
        # print(self._data)
        SteamIqToolSet.set_averaged_sample_statuses(self._data)
        # print('after average statuses')
        # print(self._data)
        SteamIqToolSet.set_final_statuses(self._data)
        # print('rafter final statuses')
        # print(self._data)

        #self._file_name = get_file_name_from_path(path)


    def _plot_graph(self):
        #print(self._plt.get_fignums())
        if len(self._plt.get_fignums())<1:
            fig, axs = self._plt.subplots(figsize=(14, 1), layout='constrained')
        else:
            self._plt.cla()
            fig = self._plt.gcf()
            axs = self._plt.gca()
        #axs.xaxis.set_major_formatter(mdates.ConciseDateFormatter(axs.xaxis.get_major_locator()))
        

        plot_from = self._dt_plot_from.dateTime().toPython()
        plot_to = self._dt_plot_to.dateTime().toPython()

        service_breaks = [] #in future there will be several service breaks, so we use the list
        sb = self._dt_service_break.dateTime().toPython()
        if sb > plot_from and sb < plot_to:
            service_breaks.append(sb)

        try:
            self._plt.grid(True)

            fsts = extract_series_from_df(self._data, plot_from, plot_to, 'Final status')
            status_map = SteamIqToolSet.prepare_status_map(fsts)
            
            leak_unit = '%'

            if self._what_to_print == 'Activity map':
                if self._cbx_add_leak_graph.isChecked():
                    srs = extract_series_from_df(self._data, plot_from, plot_to, 'Aver leak')
                    #print(srs)
                    color = line_colors_map[self._cmb_leak_graph_color.currentText()]
                    srs.plot(ax = axs, color=color)
                    axs.fill_between(srs.index, y1=srs, alpha=0.4, color=color, linewidth=2)

                    self._txt_csv_view.setText(str(srs))

                for item in status_map['0']:
                    axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Offline], alpha=0.8)
                for item in status_map['1']:
                    axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Cold], alpha=0.8)
                for item in status_map['2']:
                    axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Low], alpha=0.8)
                for item in status_map['3']:
                    axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Medium], alpha=0.8)
                for item in status_map['4']:
                    axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.High], alpha=0.8)

                

            elif self._what_to_print == 'Leak graph':
                if self._cbx_amap_in_bg.isChecked():
                    for item in status_map['0']:
                        axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Offline], alpha=0.3)
                    for item in status_map['1']:
                        axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Cold], alpha=0.3)
                    for item in status_map['2']:
                        axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Low], alpha=0.3)
                    for item in status_map['3']:
                        axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.Medium], alpha=0.3)
                    for item in status_map['4']:
                        axs.axvspan(item[0].to_pydatetime(), item[1].to_pydatetime(), 0, 1, facecolor=status_colors_map[StatusColors.High], alpha=0.3)


                srs = extract_series_from_df(self._data, plot_from, plot_to, 'Aver leak')
                leak_unit = '%'
                use_green_zone = self._cbx_use_green_zone.isChecked()
                pres = float(self._ltx_pressure.text())
                orif_d = float(self._ltx_orifice_diam.text())
                eff = float(self._ltx_efficiency.text())

                if self._cmb_leak_units.currentText()==LeakUnits.Mass:
                    srs = SteamIqToolSet.transf_percent_leak_srs_to_kgh(srs, pres, orif_d)
                    leak_unit = 'kg/h'
                
                elif self._cmb_leak_units.currentText()==LeakUnits.Energy:
                    srs = SteamIqToolSet.transf_percent_leak_srs_to_kW(srs, pres, orif_d, eff)
                    leak_unit = 'kW'

                color = line_colors_map[self._cmb_leak_graph_color.currentText()]
                srs.plot(ax = axs, color=color)
                axs.fill_between(srs.index, y1=srs, alpha=0.4, color=color, linewidth=2)

                if self._cbx_calc_integral.isChecked():
                    integral, cum_time = SteamIqToolSet.calculate_integral_values_using_sm(srs, status_map, use_green_zone)

                    self._txt_csv_view.setText(f'{integral=}\n{cum_time=}\n'
                                               f'mean integral value for active time={integral/cum_time}\n'
                                               f'{leak_unit}*hour={integral.total_seconds()/3600}')
                axs.set_ylabel(self._ltx_y_label.text()+', '+leak_unit)

            axs.set_xticks([plot_from, plot_to])
            axs.set_xticklabels([plot_from.strftime('%Y/%m/%d'), plot_to.strftime('%Y/%m/%d')], rotation=0, ha='center')
            axs.set_title(self._ltx_plot_title.text())
            axs.set(xlabel=None)
            axs.set_ylim([self._spb_y_axis_from.value(), self._spb_y_axis_to.value()])
            
            

        except Exception as error:
            #print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')