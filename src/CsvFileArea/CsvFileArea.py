from PySide6 import QtCore, QtWidgets

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral
from src.utils.settings import ResampleOperations

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
            self._file_name = get_file_name_from_path(path)
            self._create_ui()
            GlobalCommunicator.change_status_line.emit(f'File {self._file_name} loaded')
            return True
        except Exception as error:
            self._data = None
            GlobalCommunicator.change_status_line.emit(f'File loading failed, {error}')
            return False
        
    @QtCore.Slot()
    def _plot(self):
        self._plot_graph()

    def _load_csv_file(self, path, params):
        raise NotImplementedError
    
    def _plot_graph(self):
        raise NotImplementedError


    def _create_ui(self):
        #-Data text representation window-----------------------------
        self._txt_csv_view = QtWidgets.QTextBrowser()
        self._txt_csv_view.setText(str(self._data.head(50)))
        #-Draw options-----------------------------
        gbx_options = QtWidgets.QGroupBox()
        gbx_options.setTitle('Draw options')

        #---------------Plot From/To and Service break------------------
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

        lbl_service_break = QtWidgets.QLabel('Service break')
        self._cbx_service_break = QtWidgets.QCheckBox()
        self._dt_service_break = QtWidgets.QDateTimeEdit()
        self._dt_service_break.setMinimumDateTime(datetime_from)
        self._dt_service_break.setMaximumDateTime(datetime_to)
        self._dt_service_break.setDisabled(True)
        self._cbx_service_break.stateChanged.connect(lambda state: self._dt_service_break.setDisabled(not(bool(state))))

        lyt_dt_limits = QtWidgets.QHBoxLayout()
        lyt_dt_limits.addWidget(lbl_plot_from)
        lyt_dt_limits.addWidget(self._dt_plot_from)
        lyt_dt_limits.addWidget(lbl_plot_to)
        lyt_dt_limits.addWidget(self._dt_plot_to)
        lyt_dt_limits.addWidget(lbl_service_break)
        lyt_dt_limits.addWidget(self._cbx_service_break)
        lyt_dt_limits.addWidget(self._dt_service_break)
        #---------------Other plot options------------------

        lbl_plot_title = QtWidgets.QLabel('Title')
        self._ltx_plot_title = QtWidgets.QLineEdit()
        self._ltx_plot_title.setText(self._file_name)
        lyt_dt_other = QtWidgets.QHBoxLayout()
        lyt_dt_other.addWidget(lbl_plot_title)
        lyt_dt_other.addWidget(self._ltx_plot_title)

        options_layout = QtWidgets.QVBoxLayout(gbx_options)
        #options_layout.addLayout(lyt_resample)
        options_layout.addLayout(lyt_dt_limits)
        options_layout.addLayout(lyt_dt_other)

        #-Scroll parameter area (empty)-----------
        gbx_parameters = QtWidgets.QGroupBox()
        gbx_parameters.setTitle('Parameters')

        self._lyt_params_area = QtWidgets.QVBoxLayout(gbx_parameters)
        #self._param_widgets_map = {}

        self._fill_custom_area() # virtual function, must be implemented in

        scr_params_area = QtWidgets.QScrollArea()
        scr_params_area.setWidget(gbx_parameters)
        scr_params_area.setWidgetResizable(True)
        
        #-Plot button-----------------------------
        self._btn_plot_graph = QtWidgets.QPushButton('Plot graph')
        self._btn_plot_graph.clicked.connect(self._plot)

        #-Adding to the main layout-----------------------------
        self._lyt_main.addWidget(self._txt_csv_view)
        self._lyt_main.addWidget(gbx_options)
        self._lyt_main.addWidget(scr_params_area)
        self._lyt_main.addWidget(self._btn_plot_graph)

    def _fill_custom_area(self):
        raise NotImplementedError


