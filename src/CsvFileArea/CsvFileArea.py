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
    def _plot_graph(self):
        #print(self._plt.get_fignums())
        if len(self._plt.get_fignums())<1:
            fig, axs = self._plt.subplots(figsize=(14, 4))
        else:
            self._plt.cla()
            fig = self._plt.gcf()
            axs = self._plt.gca()

        aver_period = self._spb_resample_period.value()
        aver_method = self._cmb_resample_operations.currentText()
        plot_from = self._dt_plot_from.dateTime().toPython()
        plot_to = self._dt_plot_to.dateTime().toPython()
        offset = self._spb_resample_offset.value()
        resample_options = {'aver_period': aver_period, 
                            'aver_method': aver_method, 
                            'plot_from': plot_from,
                            'plot_to': plot_to,
                            'offset': offset}
        service_breaks = [] #in future there will be several service breaks, so we use the list
        sb = self._dt_service_break.dateTime().toPython()
        if sb > plot_from and sb < plot_to:
            service_breaks.append(sb)

        try:
            self._plt.grid(True)
            text_representation = []
            # ind = -255
            for wdg in self._param_widgets_map.values():
                # if ind > 0:
                #     ax = axs.twinx()
                #     ax.spines.right.set_position(("axes", 1+0.2*ind))
                # else:
                #     ax = axs
                srs_list = wdg.plot(axs, resample_options, service_breaks)
                # ind += 1
                if srs_list:
                    for srs in srs_list:
                        integral_str = 'N/A'
                        if hasattr(srs, 'integral'):
                            integral_str = str(srs.integral.total_seconds())
                        text_representation.append(str(srs)+f'\nIntegral = {integral_str} units*sec\n')
            
            self._txt_csv_view.setText('\n------------------\n'.join(text_representation))

            axs.set_title(self._ltx_plot_title.text())
            axs.legend()

        except Exception as error:
            #print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')

    def _load_csv_file(self, path, params):
        raise NotImplementedError


    def _create_ui(self):
        #-Data text representation window-----------------------------
        self._txt_csv_view = QtWidgets.QTextBrowser()
        self._txt_csv_view.setText(str(self._data))
        #-Draw options-----------------------------
        gbx_options = QtWidgets.QGroupBox()
        gbx_options.setTitle('Draw options')
        #---------------Resample------------------
        lbl_resample_operations = QtWidgets.QLabel('Resample operations')
        self._cmb_resample_operations = QtWidgets.QComboBox()
        self._cmb_resample_operations.addItems(ResampleOperations)
        self._cmb_resample_operations.setCurrentText(ResampleOperations.Mean)
        lbl_resample_period = QtWidgets.QLabel('Hours of averaging')
        self._spb_resample_period = QtWidgets.QSpinBox()
        self._spb_resample_period.setRange(1, 24)
        lbl_resample_offset = QtWidgets.QLabel('Offset, min')
        self._spb_resample_offset = QtWidgets.QSpinBox()
        self._spb_resample_offset.setRange(-60, 60)
        self._spb_resample_offset.setValue(0)
        lyt_resample = QtWidgets.QHBoxLayout()
        lyt_resample.addWidget(lbl_resample_operations)
        lyt_resample.addWidget(self._cmb_resample_operations)
        lyt_resample.addWidget(lbl_resample_period)
        lyt_resample.addWidget(self._spb_resample_period)
        lyt_resample.addWidget(lbl_resample_offset)
        lyt_resample.addWidget(self._spb_resample_offset)
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
        options_layout.addLayout(lyt_resample)
        options_layout.addLayout(lyt_dt_limits)
        options_layout.addLayout(lyt_dt_other)

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


