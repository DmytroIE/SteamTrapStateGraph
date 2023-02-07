from PySide6 import QtCore, QtWidgets

import pandas as pd

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path
from src.utils.settings import ResampOperations,YAxisLimits


class CsvFileArea(QtWidgets.QWidget):
    def __init__(self, plt):
        QtWidgets.QWidget.__init__(self)

        self._gbx_options = QtWidgets.QGroupBox()
        self._gbx_options.setTitle('Draw options')

        self._txt_csv_view = QtWidgets.QTextBrowser()

        self._lbl_averaging_options = QtWidgets.QLabel('Averaging options')
        self._cmb_averaging_options = QtWidgets.QComboBox()
        self._cmb_averaging_options.addItems(ResampOperations.values())
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
        self._lyt_other_opts = QtWidgets.QHBoxLayout()
        self._lyt_other_opts.addWidget(self._lbl_column_to_plot)
        self._lyt_other_opts.addWidget(self._cmb_column_to_plot)
        self._cmb_column_to_plot.currentTextChanged.connect(self._set_y_axis_name)
        self._lyt_other_opts.addWidget(self._lbl_y_label)
        self._lyt_other_opts.addWidget(self._ltx_y_label)

        self._options_layout = QtWidgets.QVBoxLayout(self._gbx_options)
        self._options_layout.addLayout(self._lyt_averaging)
        self._options_layout.addLayout(self._lyt_dt_limits)
        self._options_layout.addLayout(self._lyt_other_opts)

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

        if averaging_method == ResampOperations['MEAN']:
            plot_data = plot_data.resample(f'{aver_period}h', origin='start').mean()#.fillna(0) #, offset='-5m'

        self._txt_csv_view.setText(str(plot_data))
        # plot_data.info()
        
        if len(self._plt.get_fignums())<1:
            fig, axs = self._plt.subplots(figsize=(14, 4))
        else:
            self._plt.cla()
            fig = self._plt.gcf()
            axs = self._plt.gca()
        try:
            #index = pd.DatetimeIndex(['2014-06-04 14:56:33',
            #                          '2014-06-04 15:56:33', 
            #                          '2014-06-04 16:56:33',
            #              '2014-06-04 17:56:33', 
            #              '2014-06-04 18:56:33', 
            #              '2014-06-04 19:56:33',
            #              '2014-06-04 20:56:33'])
            #data = pd.Series(data=[1.2,3.555,6.178,9.369,7.14,3.72,6.05], index=index)
            #print(data.head())
            #data.plot(ax = axs)
            #print(plot_data.head())
            plot_data.plot(ax = axs)
            
            if y_axis_name:
                axs.set_ylabel(y_axis_name)
            else:
                axs.set_ylabel(col_to_plot)
            axs.set_title(self._file_name)
            axs.set_ylim(YAxisLimits)
            axs.fill_between(plot_data.index, y1=plot_data, label='aaa', alpha=0.5, color='tab:green', linewidth=2)
        except Exception as error:
            print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')
            print(str(error))


    @QtCore.Slot()
    def _set_y_axis_name(self, text):
        self._ltx_y_label.setText(text)
