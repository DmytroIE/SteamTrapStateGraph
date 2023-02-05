from PySide6 import QtCore, QtWidgets

import pandas as pd

import matplotlib.pyplot as plt



class CsvFileArea(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self._txt_csv_view = QtWidgets.QTextBrowser()

        self._lbl_averaging_options = QtWidgets.QLabel('Averaging options')
        self._cmb_averaging_options = QtWidgets.QComboBox()
        self._cmb_averaging_options.addItems(['Mean', '??'])
        self._lbl_averaging_samples = QtWidgets.QLabel('Hours of averaging')
        self._spb_averaging_samples = QtWidgets.QSpinBox()
        self._spb_averaging_samples.setRange(1, 12)
        self._lyt_averaging = QtWidgets.QHBoxLayout()
        self._lyt_averaging.addWidget(self._lbl_averaging_options)
        self._lyt_averaging.addWidget(self._cmb_averaging_options)
        self._lyt_averaging.addWidget(self._lbl_averaging_samples)
        self._lyt_averaging.addWidget(self._spb_averaging_samples)

        self._lbl_print_from = QtWidgets.QLabel('From date/time')
        self._dt_print_from = QtWidgets.QDateTimeEdit()
        self._lbl_print_to = QtWidgets.QLabel('To date/time')
        self._dt_print_to = QtWidgets.QDateTimeEdit()
        self._lyt_dt_limits = QtWidgets.QHBoxLayout()
        self._lyt_dt_limits.addWidget(self._lbl_print_from)
        self._lyt_dt_limits.addWidget(self._dt_print_from)
        self._lyt_dt_limits.addWidget(self._lbl_print_to)
        self._lyt_dt_limits.addWidget(self._dt_print_to)

        self._btn_plot_graph = QtWidgets.QPushButton('Plot graph')
        self._btn_plot_graph.clicked.connect(self._plot_graph)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addWidget(self._txt_csv_view)
        self._layout.addLayout(self._lyt_averaging)
        self._layout.addLayout(self._lyt_dt_limits)
        self._layout.addWidget(self._btn_plot_graph)

        self._data = None

        
    def load_csv_file(self, path, params):
        try:
            print(params)
            date_col_name = params['date_col_name']
            col_sep = params['col_sep']
            if col_sep == 'Tab':
                col_sep = '\t' 
            
            self._data = pd.read_csv(path, sep=col_sep, header=0, parse_dates=[date_col_name], index_col=date_col_name)

            self._txt_csv_view.setText(str(self._data))


            dfrom = self._data.index[0]
            self._datetime_from = QtCore.QDateTime(dfrom.year, dfrom.month, dfrom.day, dfrom.hour, dfrom.minute, dfrom.second)
            self._dt_print_from.setDateTime(self._datetime_from)
            self._dt_print_from.setMinimumDateTime(self._datetime_from)


            dto = self._data.index[-1]
            self._datetime_to = QtCore.QDateTime(dto.year, dto.month, dto.day, dto.hour, dto.minute, dto.second)
            self._dt_print_to.setDateTime(self._datetime_to)
            self._dt_print_to.setMaximumDateTime(self._datetime_to)

            #self._dt_print_from.setMaximumDateTime(self._datetime_to.addSecs(-3600))
            #self._dt_print_to.setMinimumDateTime(self._datetime_from.addSecs(3600))          


            return True, None
        except Exception as error:
            self._data = None
            return False, str(error)
        
    @QtCore.Slot()
    def _plot_graph(self):
        # plot_data = self._data['Leak']
        plot_from = self._dt_print_from.dateTime().toPython()
        plot_to = self._dt_print_to.dateTime().toPython()#.toString('yyyy-MM-dd hh:mm')
        print(plot_from)
        print(plot_to)
        plot_data = self._data[(self._data.index>=plot_from)&(self._data.index<=plot_to)]
        plot_data = plot_data['Leak']

        sample_hours = self._spb_averaging_samples.value()
        averaging_method = self._cmb_averaging_options.currentText()
        if sample_hours > 1:
            if averaging_method == 'Mean':
                plot_data = plot_data.resample(f'{sample_hours}H', origin='start', offset=f'{sample_hours/2}H').mean()

        self._txt_csv_view.setText(str(plot_data))
        

        plt.plot(plot_data.index, plot_data)
        plt.show()