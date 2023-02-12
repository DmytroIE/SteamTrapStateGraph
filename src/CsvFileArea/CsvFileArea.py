from PySide6 import QtCore, QtWidgets

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral
from src.utils.settings import ResampOperations

from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.CsvFileArea.SteamIqPlotSettings import SteamIqPlotSettings


class CsvFileArea(QtWidgets.QWidget):
    def __init__(self, plt):
        QtWidgets.QWidget.__init__(self)

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._data = None
        self._plt = plt

       
    def load_csv_file(self, path, params):
        try:
            self._load_csv_file(path, params)
            self._create_ui()
            GlobalCommunicator.change_status_line.emit(f'File {self._file_name} loaded')
            return True
        except Exception as error:
            self._data = None
            GlobalCommunicator.change_status_line.emit(f'File loading failed, {error}')
            return False
        
    @QtCore.Slot()
    def _plot_graph(self):

        aver_period = self._spb_averaging_period.value()
        averaging_method = self._cmb_averaging_options.currentText()
        col_to_plot = self._cmb_column_to_plot.currentText()
        y_axis_name = self._ltx_y_label.text()

        plot_from = self._dt_plot_from.dateTime().toPython()
        plot_to = self._dt_plot_to.dateTime().toPython()

        plot_data = self._data[(self._data.index>=plot_from)&(self._data.index<=plot_to)]
        plot_data = plot_data[col_to_plot]

        if averaging_method == ResampOperations.Mean:
            plot_data = plot_data.resample(f'{aver_period}h', origin='start').mean()#.fillna(0) #, offset='-5m'

        self._txt_csv_view.setText(str(plot_data))
        # plot_data.info()
        # print(f'isnull={plot_data.isnull()}')


       
        if len(self._plt.get_fignums())<1:
            fig, axs = self._plt.subplots(figsize=(14, 2))
        else:
            self._plt.cla()
            fig = self._plt.gcf()
            axs = self._plt.gca()
        try:

            self._plt.grid(True)
            plot_data.plot(ax = axs, color=self._cmb_line_color.currentText(), label = y_axis_name)
            
            if y_axis_name:
                axs.set_ylabel(y_axis_name)
            else:
                axs.set_ylabel(col_to_plot)
            axs.set_title(self._file_name)
            y_axis_limits = [self._spb_y_axis_from.value(), self._spb_y_axis_to.value()]
            axs.set_ylim(y_axis_limits)
            axs.fill_between(plot_data.index, y1=plot_data, alpha=0.4, color=self._cmb_line_color.currentText(), linewidth=2)

            result = calc_integral(plot_data)
            if result:
                integr, time_diff = result
                mean_integr_value = integr/time_diff
                #print(f'Numpy integr={integr}')
                #print(f'time diff={time_diff}')
                #print(f'Mean integr ={mean_integr_value}')
                axs.axhline(integr/time_diff, ls='--', color='r', label = f'Mean = {mean_integr_value:.2f}')
                
            else:
                print('None')

            axs.legend()

        except Exception as error:
            print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')
            print(str(error))

    def _load_csv_file(self, path, params):
        raise NotImplementedError


    def _create_ui(self):

        self._txt_csv_view = QtWidgets.QTextBrowser()
        self._txt_csv_view.setText(str(self._data))
        #-Draw options-----------------------------
        gbx_options = QtWidgets.QGroupBox()
        gbx_options.setTitle('Draw options')
        #---------------Resample------------------
        lbl_averaging_options = QtWidgets.QLabel('Averaging options')
        self._cmb_averaging_options = QtWidgets.QComboBox()
        self._cmb_averaging_options.addItems(ResampOperations)
        self._cmb_averaging_options.setCurrentText(ResampOperations.Mean)
        lbl_averaging_period = QtWidgets.QLabel('Hours of averaging')
        self._spb_averaging_period = QtWidgets.QSpinBox()
        self._spb_averaging_period.setRange(1, 24)
        lbl_averaging_offset = QtWidgets.QLabel('Offset, min')
        self._spb_averaging_offset = QtWidgets.QSpinBox()
        self._spb_averaging_offset.setRange(-60, 60)
        self._spb_averaging_offset.setValue(0)
        lyt_averaging = QtWidgets.QHBoxLayout()
        lyt_averaging.addWidget(lbl_averaging_options)
        lyt_averaging.addWidget(self._cmb_averaging_options)
        lyt_averaging.addWidget(lbl_averaging_period)
        lyt_averaging.addWidget(self._spb_averaging_period)
        lyt_averaging.addWidget(lbl_averaging_offset)
        lyt_averaging.addWidget(self._spb_averaging_offset)
        #---------------Plot From/To------------------
        lbl_plot_from = QtWidgets.QLabel('From date/time')
        self._dt_plot_from = QtWidgets.QDateTimeEdit()
        lbl_plot_to = QtWidgets.QLabel('To date/time')
        self._dt_plot_to = QtWidgets.QDateTimeEdit()

        dfrom = self._data.index[0]
        datetime_from = QtCore.QDateTime(dfrom.year, dfrom.month, dfrom.day, dfrom.hour, dfrom.minute, dfrom.second)
        self._dt_plot_from.setDateTime(datetime_from)
        self._dt_plot_from.setMinimumDateTime(datetime_from)

        dto = self._data.index[-1]
        datetime_to = QtCore.QDateTime(dto.year, dto.month, dto.day, dto.hour, dto.minute, dto.second)
        self._dt_plot_to.setDateTime(datetime_to)
        self._dt_plot_to.setMaximumDateTime(datetime_to)

        lyt_dt_limits = QtWidgets.QHBoxLayout()
        lyt_dt_limits.addWidget(lbl_plot_from)
        lyt_dt_limits.addWidget(self._dt_plot_from)
        lyt_dt_limits.addWidget(lbl_plot_to)
        lyt_dt_limits.addWidget(self._dt_plot_to)

        options_layout = QtWidgets.QVBoxLayout(gbx_options)
        options_layout.addLayout(lyt_averaging)
        options_layout.addLayout(lyt_dt_limits)

        #-Scroll parameter area (empty)-----------
        gbx_parameters = QtWidgets.QGroupBox()
        gbx_parameters.setTitle('Parameters')

        self._lyt_params_area = QtWidgets.QVBoxLayout(gbx_parameters)
        self._param_widgets_map = {}

        self._fill_params_area() # virtual function, must be implemented in

        scr_params_area = QtWidgets.QScrollArea()
        scr_params_area.setWidget(gbx_parameters)
        scr_params_area.setWidgetResizable(True)
        
        #-Plot button-----------------------------
        self._btn_plot_graph = QtWidgets.QPushButton('Plot graph')
        self._btn_plot_graph.clicked.connect(self._plot_graph)

        #-Adding to the main layout-----------------------------
        self._lyt_main.addWidget(self._txt_csv_view)
        self._lyt_main.addWidget(gbx_options)
        self._lyt_main.addWidget(scr_params_area)
        self._lyt_main.addWidget(self._btn_plot_graph)

    def _fill_params_area(self):
        raise NotImplementedError


