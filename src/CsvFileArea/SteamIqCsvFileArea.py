from PySide6 import QtCore, QtWidgets

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral
from src.utils.settings import ResampOperations

from src.CsvFileArea.CsvFileArea import CsvFileArea
from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.CsvFileArea.SteamIqPlotSettings import SteamIqPlotSettings


class SteamIqCsvFileArea(CsvFileArea):
    def __init__(self, plt):
        CsvFileArea.__init__(self, plt)

    def _fill_params_area(self):
        wdg_leak = SteamIqPlotSettings(self._data, self._leak_col_name, self._cycle_col_name)
        self._lyt_params_area.addWidget(wdg_leak)
        self._param_widgets_map[self._leak_col_name] = wdg_leak

        wdg_cycle = IndPlotSettings(self._data, self._cycle_col_name)
        self._lyt_params_area.addWidget(wdg_cycle)
        self._param_widgets_map[self._cycle_col_name] = wdg_cycle
        
    def _load_csv_file(self, path, params):
        date_col_name = params['date_col_name']
        col_sep = params['col_sep']
        if col_sep == 'Tab':
            col_sep = '\t' 
        self._leak_col_name = params['leak_col_name']
        self._cycle_col_name = params['cycle_col_name']
            
        self._data = pd.read_csv(path, 
                                 sep=col_sep, 
                                 header=0, 
                                 usecols=[date_col_name, self._leak_col_name, self._cycle_col_name],
                                 dtype={self._leak_col_name:'float64', self._cycle_col_name: 'float64'},
                                 parse_dates=[date_col_name], 
                                 index_col=date_col_name)
        self._file_name = get_file_name_from_path(path)