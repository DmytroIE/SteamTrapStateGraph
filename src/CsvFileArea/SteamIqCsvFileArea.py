from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QObject, QThread, Signal
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral, split_one_series_by_sb, resample_series, convert_sbs_to_pd_format, extract_series_from_df
from src.utils.settings import LineColors, AuxLineColors, StatusColors, line_colors_map, status_colors_map, LeakUnits
from src.utils.SteamIqToolSet import SteamIqToolSet

from src.CsvFileArea.CsvFileArea import CsvFileArea


class WorkerSignals(QtCore.QObject):
    finished = Signal()
    error = Signal(object)
    result = Signal(object)


class SteamIqDataProcessor(QtCore.QRunnable):
    def __init__(self, path, params):
        super().__init__()
        self._path = path
        self._params = params
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        data = None
        try:
            # f = data['f']  # raise the error
            date_col_name = self._params['date_col_name']
            col_sep = self._params['col_sep']
            if col_sep == 'Tab':
                col_sep = '\t'
            leak_col_name = self._params['leak_col_name']
            cycle_col_name = self._params['cycle_col_name']

            data = pd.read_csv(self._path,
                               sep=col_sep,
                               header=0,
                               usecols=[date_col_name, leak_col_name, cycle_col_name],
                               dtype={leak_col_name: 'float64', cycle_col_name: 'float64'},
                               parse_dates=[date_col_name],
                               index_col=date_col_name)

            # Just in case if initially columns have different from 'Leak' and 'Cycle Counts' names
            data.rename(columns={leak_col_name: 'Leak', cycle_col_name: 'Cycle Counts'}, inplace=True)

            resample_interval = self._params['resample_interval']
            data = SteamIqToolSet.fill_data_gaps_with_nans(data, resample_interval)
            SteamIqToolSet.set_sample_statuses(data)
            SteamIqToolSet.set_averaged_sample_statuses(data)
            SteamIqToolSet.set_final_statuses(data)
            QThread.sleep(1)
            self.signals.result.emit(data)
        except Exception as error:
            self.signals.error.emit(error)
        finally:
            self.signals.finished.emit()


class SteamIqCsvFileArea(CsvFileArea):
    def __init__(self, plt):
        CsvFileArea.__init__(self, plt)
        self._threadpool = QtCore.QThreadPool()
        # print("Multithreading with maximum %d threads" % self._threadpool.maxThreadCount())

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
        ##self._lbl_calc_integral = QtWidgets.QLabel('Calc integral')
        #self._cbx_calc_integral = QtWidgets.QCheckBox('Calc integral')
        ##self._lbl_calc_integral = QtWidgets.QLabel('Green zone')
        self._cbx_use_green_zone = QtWidgets.QCheckBox('Green zone')
        self._lbl_leak_units = QtWidgets.QLabel('Units for leakage')
        self._cmb_leak_units = QtWidgets.QComboBox()
        self._cmb_leak_units.addItems(LeakUnits)
        self._cmb_leak_units.setCurrentText(LeakUnits.Mass)
        self._lbl_co2factor = QtWidgets.QLabel('CO2 factor, kg/kWh')
        self._ltx_co2factor = QtWidgets.QLineEdit('0.184')
        self._ltx_co2factor.setValidator(QtGui.QDoubleValidator(0.0001, 1.0, 4, notation=QtGui.QDoubleValidator.StandardNotation))

        self._lbl_pressure = QtWidgets.QLabel('Pres, barg')
        self._ltx_pressure = QtWidgets.QLineEdit('5.0')
        self._ltx_pressure.setValidator(QtGui.QDoubleValidator(0.1, 999.9, 1, notation=QtGui.QDoubleValidator.StandardNotation))
        self._lbl_orifice_diam = QtWidgets.QLabel('Orif diam, mm')
        self._ltx_orifice_diam = QtWidgets.QLineEdit('4.0')
        self._ltx_orifice_diam.setValidator(QtGui.QDoubleValidator(0.1, 999.9, 1, notation=QtGui.QDoubleValidator.StandardNotation))
        self._lbl_efficiency = QtWidgets.QLabel('Efficiency, %')
        self._ltx_efficiency = QtWidgets.QLineEdit('80.0')
        self._ltx_efficiency.setValidator(QtGui.QDoubleValidator(0.1, 100.0, 0, notation=QtGui.QDoubleValidator.StandardNotation))
        self._lbl_entalpy = QtWidgets.QLabel('Entalpy, kJ/kg')
        self._ltx_entalpy = QtWidgets.QLineEdit('2700.0')
        self._ltx_entalpy.setValidator(QtGui.QDoubleValidator(0.1, 2800.0, 0, notation=QtGui.QDoubleValidator.StandardNotation))

        self._lyt_plot_leak_graph = QtWidgets.QVBoxLayout(self._gbx_plot_leak_graph)
        self._lyt_plot_leak_graph_one = QtWidgets.QHBoxLayout()
        self._lyt_plot_leak_graph_one.addWidget(self._lbl_y_label)
        self._lyt_plot_leak_graph_one.addWidget(self._ltx_y_label)
        self._lyt_plot_leak_graph_one.addWidget(self._cbx_amap_in_bg)
        #self._lyt_plot_leak_graph_one.addWidget(self._cbx_calc_integral)
        self._lyt_plot_leak_graph_one.addWidget(self._cbx_use_green_zone )
        self._lyt_plot_leak_graph_one.addWidget(self._lbl_leak_units)
        self._lyt_plot_leak_graph_one.addWidget(self._cmb_leak_units)
        self._lyt_plot_leak_graph_one.addWidget(self._lbl_co2factor)
        self._lyt_plot_leak_graph_one.addWidget(self._ltx_co2factor)


        self._lyt_plot_leak_graph_two = QtWidgets.QHBoxLayout()
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_pressure)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_pressure)
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_orifice_diam)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_orifice_diam)
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_efficiency)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_efficiency)
        self._lyt_plot_leak_graph_two.addWidget(self._lbl_entalpy)
        self._lyt_plot_leak_graph_two.addWidget(self._ltx_entalpy)


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
        self._file_name = get_file_name_from_path(path)
        worker = SteamIqDataProcessor(path, params)
        worker.signals.result.connect(self._receive_data)
        worker.signals.error.connect(self._receive_error)
        # worker.signals.finished.connect(lambda: print('complete'))
        self._threadpool.start(worker)

    def _receive_data(self, data):
        GlobalCommunicator.change_status_line.emit(f'File {self._file_name} loaded')
        GlobalCommunicator.load_successful.emit(True)
        self._data = data
        self._create_ui()

    def _receive_error(self, error):
        GlobalCommunicator.change_status_line.emit(f'File loading failed, {str(error)}')
        GlobalCommunicator.load_successful.emit(False)

    def _plot_graph(self):
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

                    self._txt_csv_view.setText(str(srs.head(50)))#str(srs))

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

                srs_perc = extract_series_from_df(self._data, plot_from, plot_to, 'Aver leak')
                     
                use_green_zone = self._cbx_use_green_zone.isChecked()
                pres = float(self._ltx_pressure.text())
                orif_d = float(self._ltx_orifice_diam.text())
                eff = float(self._ltx_efficiency.text())
                entalpy = float(self._ltx_entalpy.text())
                co2factor = float(self._ltx_co2factor.text())
                co2emission =  0                  

                # Integral calc
                result_string = ''

                srs_kw = SteamIqToolSet.transf_percent_leak_srs_to_kW(srs_perc, pres, orif_d, eff, entalpy)
                result_kwh = SteamIqToolSet.calculate_integral_values_using_sm(srs_kw, status_map, use_green_zone)
                is_green_zone_label = ''
                if use_green_zone:
                    is_green_zone_label = '2,'
                if result_kwh:
                    integral, cum_time = result_kwh
                    result_string += (f'{integral=}\n{cum_time=}\n'
                                       f'mean integral value, kW, for statuses {is_green_zone_label} 3 and 4 = {integral/cum_time}\n'
                                       f'kW*hour = {integral.total_seconds()/3600}\n'
                                       f'CO2 emission, kg = {integral.total_seconds()/3600*co2factor}\n\n')
                else:
                    result_string += (f'integral=0\ncum_time=0\n'
                                       f'mean integral value, kW for statuses {is_green_zone_label} 3 and 4 = 0\n'
                                       f'kW*hour = 0\n')
                srs_kg = SteamIqToolSet.transf_percent_leak_srs_to_kgh(srs_perc, pres, orif_d)
                result_kg = SteamIqToolSet.calculate_integral_values_using_sm(srs_kg, status_map, use_green_zone)
                is_green_zone_label = ''
                if use_green_zone:
                    is_green_zone_label = '2,'
                if result_kg:
                    integral, cum_time = result_kg
                    result_string += (f'{integral=}\n{cum_time=}\n'
                                f'mean integral value, kg/h, for statuses {is_green_zone_label} 3 and 4 = {integral/cum_time}\n'
                                f'kg/h*hour = {integral.total_seconds()/3600}\n')
                else:
                    result_string += (f'integral=0\ncum_time=0\n'
                                       f'mean integral value, kg/h, for statuses {is_green_zone_label} 3 and 4 = 0\n'
                                       f'kg/h*hour = 0\n')

                self._txt_csv_view.setText(result_string)

                leak_unit = '%' 
                srs_to_plot = srs_perc
                if self._cmb_leak_units.currentText()==LeakUnits.Mass:
                    leak_unit = 'kg/h'
                    srs_to_plot = srs_kg
                elif self._cmb_leak_units.currentText()==LeakUnits.Energy:
                    leak_unit = 'kW'
                    srs_to_plot = srs_kw

                color = line_colors_map[self._cmb_leak_graph_color.currentText()]
                srs_to_plot.plot(ax = axs, color=color)
                axs.fill_between(srs_to_plot.index, y1=srs_to_plot, alpha=0.4, color=color, linewidth=2)

                axs.set_ylabel(self._ltx_y_label.text()+', '+leak_unit)
            axs.set_xticks([plot_from, plot_to])
            axs.set_xticklabels([plot_from.strftime('%Y/%m/%d'), plot_to.strftime('%Y/%m/%d')], rotation=0, ha='center')
            axs.set_title(self._ltx_plot_title.text())
            axs.set(xlabel=None)
            axs.set_ylim([self._spb_y_axis_from.value(), self._spb_y_axis_to.value()])
            GlobalCommunicator.change_status_line.emit(f'Graph {self._ltx_plot_title.text()} plotted')
            

        except Exception as error:
            #print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')