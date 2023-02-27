from PySide6 import QtCore, QtWidgets
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path, calc_integral, split_one_series_by_sb, resample_series, convert_sbs_to_pd_format, extract_series_from_df
from src.utils.settings import LineColors, AuxLineColors, StatusColors, line_colors_map, aux_line_colors_map, status_colors_map
from src.utils.SteamIqToolSet import SteamIqToolSet

from src.CsvFileArea.CsvFileArea import CsvFileArea
from src.CsvFileArea.IndPlotSettings import IndPlotSettings
from src.CsvFileArea.SteamIqPlotSettings import SteamIqPlotSettings



class SteamIqCsvFileArea(CsvFileArea):
    def __init__(self, plt):
        CsvFileArea.__init__(self, plt)

    def _fill_custom_area(self):
        self._lbl_plot_graph = QtWidgets.QLabel('Plot graph')
        self._cbx_plot_graph = QtWidgets.QCheckBox()
        self._lbl_add_legend = QtWidgets.QLabel('Add legend')
        self._cbx_add_legend = QtWidgets.QCheckBox()
        self._lbl_plot_activity_map = QtWidgets.QLabel('Plot activity map')
        self._cbx_plot_activity_map = QtWidgets.QCheckBox()
        self._lyt_opts_one = QtWidgets.QHBoxLayout()
        self._lyt_opts_one.addWidget(self._lbl_plot_graph)
        self._lyt_opts_one.addWidget(self._cbx_plot_graph)
        self._lyt_opts_one.addWidget(self._lbl_add_legend)
        self._lyt_opts_one.addWidget(self._cbx_add_legend)
        self._lyt_opts_one.addWidget(self._lbl_plot_activity_map)
        self._lyt_opts_one.addWidget(self._cbx_plot_activity_map)

        self._lyt_params_area.addLayout(self._lyt_opts_one)
        
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
        
        self._data = SteamIqToolSet.fill_data_gaps_with_nans(data)
        SteamIqToolSet.set_sample_statuses(self._data)
        SteamIqToolSet.set_averaged_sample_statuses(self._data)
        SteamIqToolSet.set_final_statuses(self._data)

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
            text_representation = []
            #axs.locator_params(nbins=3)
            if self._cbx_plot_graph.isChecked():
                srs = extract_series_from_df(self._data, plot_from, plot_to, 'Aver leak')
                color = 'w'#line_colors_map['LineColors.Orange']#[self._cmb_line_color.currentText()]
                srs.plot(ax = axs, color=color)
                axs.fill_between(srs.index, y1=srs, alpha=0.4, color=color, linewidth=2)
                if self._cbx_add_legend.isChecked():
                    axs.legend()
            if self._cbx_plot_activity_map.isChecked():
                fsts = extract_series_from_df(self._data, plot_from, plot_to, 'Final status')
                status_map = SteamIqToolSet.prepare_status_map(fsts)
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

            #axs.set_xticklabels(axs.get_xticklabels(), rotation=0, ha='center')
            axs.set_xticks([plot_from, plot_to])
            axs.set_xticklabels([plot_from.strftime('%Y/%m/%d'), plot_to.strftime('%Y/%m/%d')], rotation=0, ha='center')
            axs.set_title(self._ltx_plot_title.text())

            axs.set_ylim([0, 50])
            
            # xtick_locator = mdates.AutoDateLocator(minticks=9, maxticks=10)
            # xtick_formatter = mdates.AutoDateFormatter(xtick_locator)
            # axs.xaxis.set_major_locator(xtick_locator)
            # axs.xaxis.set_major_formatter(xtick_formatter)
            

        except Exception as error:
            #print(str(error))
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')