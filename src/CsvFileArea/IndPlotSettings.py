from PySide6 import QtWidgets

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import split_one_series_by_sb, resample_series, calc_integral, convert_sbs_to_pd_format, extract_series_from_df
from src.utils.settings import LineColors, AuxLineColors, line_colors_map, aux_line_cycler

import matplotlib as mpl

class IndPlotSettings(QtWidgets.QGroupBox):
    def __init__(self, df, col_name, def_color=LineColors.Orange, def_is_plotted=False):
        QtWidgets.QGroupBox.__init__(self)
        self._df = df
        self._col_name = col_name

        self.setTitle(self._col_name)
        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._create_ui(def_color, def_is_plotted)

    def _prepare_plot_data(self, resample_options, service_breaks):
        #srs = self._extract_series_from_df(resample_options['plot_from'], resample_options['plot_to'])
        srs = extract_series_from_df(self._df, resample_options['plot_from'], resample_options['plot_to'], self._col_name)
        srs = self._convert_series(srs)
        service_breaks.sort()
        service_breaks = convert_sbs_to_pd_format(service_breaks)
            
        srs_list = split_one_series_by_sb(srs, service_breaks)
        srs_list = resample_series(srs_list, resample_options)

        if self._cbx_calc_integral.isChecked():
            for srs in srs_list:
                result = calc_integral(srs)
                if result:
                    srs.integral = result[0]
                    srs.cum_time = result[1]
                    srs.mean_integr_val = result[0]/result[1]
        return srs_list


    def plot(self, ax, resample_options, service_breaks):
        if not self._cbx_is_plotted.isChecked():
            return None
        try:

            srs_list = self._prepare_plot_data(resample_options, service_breaks)

            y_axis_name = self._ltx_y_label.text()
            color = line_colors_map[self._cmb_line_color.currentText()]
            #--------draw the main lines-------
            for srs in srs_list:
                srs.plot(ax = ax, color=color)
                ax.fill_between(srs.index, y1=srs, alpha=0.4, color=color, linewidth=2)

            #--------add mean integral value lines---------------
            if self._cbx_show_integral.isChecked():
                # x_st = resample_options['plot_from']
                # x_end = resample_options['plot_to']

                for srs in srs_list:
                    if hasattr(srs, 'mean_integr_val'):
                        x0, x1 = ax.get_xlim()
                        start_x = (mpl.dates.date2num(srs.index[0].to_pydatetime()) - x0) / (x1-x0)
                        end_x = (mpl.dates.date2num(srs.index[-1].to_pydatetime()) - x0) / (x1-x0)
                        ax.axhline(srs.mean_integr_val, start_x, end_x, ls='--', color=next(aux_line_cycler), label = f'Mean = {srs.mean_integr_val:.2f}')

            #-------add service break line-----------
            if len(service_breaks) > 0:
                for sb in service_breaks:
                    ax.axvline(sb, ls='--', color=next(aux_line_cycler), label = f'Service break {sb}')

            #-------axis decoration--------------------
            if y_axis_name:
                ax.set_ylabel(y_axis_name)
            else:
                ax.set_ylabel(self._col_name)

            y_axis_limits = [self._spb_y_axis_from.value(), self._spb_y_axis_to.value()]
            ax.set_ylim(y_axis_limits)


            return srs_list
        except Exception as error:
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')


    # def _extract_series_from_df(self, plot_from, plot_to):
    #     if plot_from < plot_to:
    #         srs = self._df[self._col_name]
    #         return srs[(srs.index>=plot_from)&(srs.index<=plot_to)]
    #     else:
    #         raise ValueError('Mismatch in the plot dates')
    
    def _convert_series(self, srs):
        return srs #in the case of the base class no conversion is made

    def _create_ui(self, def_color, def_if_plotted):
        
        #---------------------Row 1---------------------------
        self._lbl_is_plotted = QtWidgets.QLabel('Plot')
        self._cbx_is_plotted = QtWidgets.QCheckBox()
        self._cbx_is_plotted.setChecked(def_if_plotted)
        self._lbl_y_label = QtWidgets.QLabel('Y Axis name')
        self._ltx_y_label = QtWidgets.QLineEdit()
        self._ltx_y_label.setText(self._col_name)
        self._lbl_vert_scale = QtWidgets.QLabel('Vertical scale')
        self._spb_vert_scale = QtWidgets.QSpinBox()
        self._spb_vert_scale.setRange(20, 100)
        self._spb_vert_scale.setValue(100)
        self._lyt_opts_one = QtWidgets.QHBoxLayout()
        self._lyt_opts_one.addWidget(self._lbl_is_plotted)
        self._lyt_opts_one.addWidget(self._cbx_is_plotted)
        self._lyt_opts_one.addWidget(self._lbl_y_label)
        self._lyt_opts_one.addWidget(self._ltx_y_label)
        self._lyt_opts_one.addWidget(self._lbl_vert_scale)
        self._lyt_opts_one.addWidget(self._spb_vert_scale)

        #---------------------Row 2---------------------------
        self._lbl_y_axis_from = QtWidgets.QLabel('Y axis start')
        self._spb_y_axis_from = QtWidgets.QSpinBox()
        #self._spb_y_axis_from.setRange(-5, 100)
        self._spb_y_axis_from.setValue(0)
        self._lbl_y_axis_to = QtWidgets.QLabel('Y axis end')
        self._spb_y_axis_to = QtWidgets.QSpinBox()
        #self._spb_y_axis_to.setRange(0, 100)
        self._spb_y_axis_to.setValue(50)
        self._lbl_line_color = QtWidgets.QLabel('Line color')
        self._cmb_line_color = QtWidgets.QComboBox()
        self._cmb_line_color.addItems(LineColors)
        self._cmb_line_color.setCurrentText(def_color)
        self._lyt_opts_two = QtWidgets.QHBoxLayout()
        self._lyt_opts_two.addWidget(self._lbl_y_axis_from)
        self._lyt_opts_two.addWidget(self._spb_y_axis_from)
        self._lyt_opts_two.addWidget(self._lbl_y_axis_to)
        self._lyt_opts_two.addWidget(self._spb_y_axis_to)
        self._lyt_opts_two.addWidget(self._lbl_line_color)
        self._lyt_opts_two.addWidget(self._cmb_line_color)

        #---------------------Row self._3---------------------------
        self._lbl_calc_integral = QtWidgets.QLabel('Calc integral')
        self._cbx_calc_integral = QtWidgets.QCheckBox()
        self._lbl_show_integral = QtWidgets.QLabel('Show on graph')
        self._cbx_show_integral = QtWidgets.QCheckBox()
        self._lyt_opts_three = QtWidgets.QHBoxLayout()
        self._lyt_opts_three.addWidget(self._lbl_calc_integral)
        self._lyt_opts_three.addWidget(self._cbx_calc_integral)
        self._lyt_opts_three.addWidget(self._lbl_show_integral)
        self._lyt_opts_three.addWidget(self._cbx_show_integral)

        self._lyt_main.addLayout(self._lyt_opts_one)
        self._lyt_main.addLayout(self._lyt_opts_two)
        self._lyt_main.addLayout(self._lyt_opts_three)

