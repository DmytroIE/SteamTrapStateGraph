from PySide6 import QtCore, QtWidgets

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral_with_nans
from src.utils.settings import ResampOperations, LineColors


class CsvFileArea(QtWidgets.QWidget):
    def __init__(self, plt):
        QtWidgets.QWidget.__init__(self)

        self._gbx_options = QtWidgets.QGroupBox()
        self._gbx_options.setTitle('Draw options')

        self._txt_csv_view = QtWidgets.QTextBrowser()

        self._lbl_averaging_options = QtWidgets.QLabel('Averaging options')
        self._cmb_averaging_options = QtWidgets.QComboBox()
        self._cmb_averaging_options.addItems(ResampOperations)
        self._lbl_averaging_period = QtWidgets.QLabel('Hours of averaging')
        self._spb_averaging_period = QtWidgets.QSpinBox()
        self._spb_averaging_period.setRange(1, 24)
        self._lyt_averaging = QtWidgets.QHBoxLayout()
        self._lyt_averaging.addWidget(self._lbl_averaging_options)
        self._lyt_averaging.addWidget(self._cmb_averaging_options)
        self._lyt_averaging.addWidget(self._lbl_averaging_period)
        self._lyt_averaging.addWidget(self._spb_averaging_period)

        self._lbl_plot_from = QtWidgets.QLabel('From date/time')
        self._dt_plot_from = QtWidgets.QDateTimeEdit()
        self._lbl_plot_to = QtWidgets.QLabel('To date/time')
        self._dt_plot_to = QtWidgets.QDateTimeEdit()
        self._lyt_dt_limits = QtWidgets.QHBoxLayout()
        self._lyt_dt_limits.addWidget(self._lbl_plot_from)
        self._lyt_dt_limits.addWidget(self._dt_plot_from)
        self._lyt_dt_limits.addWidget(self._lbl_plot_to)
        self._lyt_dt_limits.addWidget(self._dt_plot_to)

        self._lbl_column_to_plot = QtWidgets.QLabel('Plot column')
        self._cmb_column_to_plot = QtWidgets.QComboBox()
        self._lbl_y_label = QtWidgets.QLabel('Y Axis name')
        self._ltx_y_label = QtWidgets.QLineEdit()
        self._lbl_line_color = QtWidgets.QLabel('Line color')
        self._cmb_line_color = QtWidgets.QComboBox()
        self._cmb_line_color.addItems(LineColors)
        self._cmb_column_to_plot.currentTextChanged.connect(self._ltx_y_label.setText)
        self._lyt_plot_opts_one = QtWidgets.QHBoxLayout()
        self._lyt_plot_opts_one.addWidget(self._lbl_column_to_plot)
        self._lyt_plot_opts_one.addWidget(self._cmb_column_to_plot)
        self._lyt_plot_opts_one.addWidget(self._lbl_y_label)
        self._lyt_plot_opts_one.addWidget(self._ltx_y_label)
        self._lyt_plot_opts_one.addWidget(self._lbl_line_color)
        self._lyt_plot_opts_one.addWidget(self._cmb_line_color)


        self._lbl_y_axis_from = QtWidgets.QLabel('Y axis start')
        self._spb_y_axis_from = QtWidgets.QSpinBox()
        self._spb_y_axis_from.setRange(-5, 100)
        self._spb_y_axis_from.setValue(0)
        self._lbl_y_axis_to = QtWidgets.QLabel('Y axis end')
        self._spb_y_axis_to = QtWidgets.QSpinBox()
        self._spb_y_axis_to.setRange(0, 100)
        self._spb_y_axis_to.setValue(50)
        self._lyt_plot_opts_two = QtWidgets.QHBoxLayout()
        self._lyt_plot_opts_two.addWidget(self._lbl_y_axis_from)
        self._lyt_plot_opts_two.addWidget(self._spb_y_axis_from)
        self._lyt_plot_opts_two.addWidget(self._lbl_y_axis_to)
        self._lyt_plot_opts_two.addWidget(self._spb_y_axis_to)


        self._options_layout = QtWidgets.QVBoxLayout(self._gbx_options)
        self._options_layout.addLayout(self._lyt_averaging)
        self._options_layout.addLayout(self._lyt_dt_limits)
        self._options_layout.addLayout(self._lyt_plot_opts_one)
        self._options_layout.addLayout(self._lyt_plot_opts_two)

        self._btn_plot_graph = QtWidgets.QPushButton('Plot graph')
        self._btn_plot_graph.clicked.connect(self._plot_graph)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addWidget(self._txt_csv_view)
        self._layout.addWidget(self._gbx_options)
        self._layout.addWidget(self._btn_plot_graph)

        self._data = None
        self._plt = plt

       
    def load_csv_file(self, path, params):
        try:
            date_col_name = params['date_col_name']
            col_sep = params['col_sep']
            if col_sep == 'Tab':
                col_sep = '\t' 
            
            self._data = pd.read_csv(path, sep=col_sep, header=0, parse_dates=[date_col_name], index_col=date_col_name)
            self._file_name = get_file_name_from_path(path)
            self._txt_csv_view.setText(str(self._data))

            dfrom = self._data.index[0]
            datetime_from = QtCore.QDateTime(dfrom.year, dfrom.month, dfrom.day, dfrom.hour, dfrom.minute, dfrom.second)
            self._dt_plot_from.setDateTime(datetime_from)
            self._dt_plot_from.setMinimumDateTime(datetime_from)

            dto = self._data.index[-1]
            datetime_to = QtCore.QDateTime(dto.year, dto.month, dto.day, dto.hour, dto.minute, dto.second)
            self._dt_plot_to.setDateTime(datetime_to)
            self._dt_plot_to.setMaximumDateTime(datetime_to)

            col_names = [col_name for col_name in self._data.columns]
            self._cmb_column_to_plot.addItems(col_names)
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

            integr, time_diff = calc_integral_with_nans(plot_data)
            if integr and time_diff:
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

