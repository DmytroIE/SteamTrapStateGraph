from PySide6 import QtWidgets

from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import split_one_series_by_sb, resample_series, calc_integral, convert_sbs_to_pd_format
from src.utils.settings import LineColors, line_colors_map



class IndPlotSettings(QtWidgets.QGroupBox):
    def __init__(self, df, col_name, def_color=LineColors.Orange, def_is_plotted=False):
        QtWidgets.QGroupBox.__init__(self)
        self._df = df
        self._col_name = col_name

        self.setTitle(self._col_name)
        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._create_ui(def_color, def_is_plotted)

    def _prepare_plot_data(self, resample_options, service_breaks):
        srs = self._extract_series_from_df(resample_options['plot_from'], resample_options['plot_to'])
        srs = self._convert_series(srs)
        service_breaks.sort()
        service_breaks = convert_sbs_to_pd_format(service_breaks)
            
        srs_list = split_one_series_by_sb(srs, service_breaks)
        srs_list = resample_series(srs_list, resample_options)

        if self._cbx_calc_integral.isChecked():
            for rs in srs_list:
                result = calc_integral(rs)
                if result:
                    rs.integral = result[0]
                    rs.cum_time = result[1]
                    rs.mean_integr = result[0]/result[1]
        return srs_list


    def plot(self, ax, resample_options, service_breaks):
        if not self._cbx_is_plotted.isChecked():
            return
        try:
            srs_list = self._prepare_plot_data(resample_options, service_breaks)

            y_axis_name = self._ltx_y_label.text()
            color = line_colors_map[self._cmb_line_color.currentText()]

            for srs in srs_list:
                #print(srs)
                srs.plot(ax = ax, color=color, label = y_axis_name)

            if y_axis_name:
                ax.set_ylabel(y_axis_name)
            else:
                ax.set_ylabel(self._col_name)

            y_axis_limits = [self._spb_y_axis_from.value(), self._spb_y_axis_to.value()]
            ax.set_ylim(y_axis_limits)
            ax.fill_between(srs.index, y1=srs, alpha=0.4, color=color, linewidth=2)

            #--service break line
            if len(service_breaks) > 0:
                for sb in service_breaks:
                    ax.axvline(sb, ls='--', color='tab:cyan', label = f'Service break {sb}')
        except Exception as error:
            GlobalCommunicator.change_status_line.emit(f'Cannot plot, {error}')


    def _extract_series_from_df(self, plot_from, plot_to):
        if plot_from < plot_to:
            srs = self._df[self._col_name]
            return srs[(srs.index>=plot_from)&(srs.index<=plot_to)]
        else:
            raise ValueError('Mismatch in the plot dates')
    
    def _convert_series(self, srs):
        return srs #in the most simple case no conversion is made

    def _create_ui(self, def_color, def_if_plotted):
        
        #---------------------Row 1---------------------------
        lbl_is_plotted = QtWidgets.QLabel('Plot')
        self._cbx_is_plotted = QtWidgets.QCheckBox()
        self._cbx_is_plotted.setChecked(def_if_plotted)
        lbl_y_label = QtWidgets.QLabel('Y Axis name')
        self._ltx_y_label = QtWidgets.QLineEdit()
        self._ltx_y_label.setText(self._col_name)
        lbl_vert_scale = QtWidgets.QLabel('Vertical scale')
        self._spb_vert_scale = QtWidgets.QSpinBox()
        self._spb_vert_scale.setRange(20, 100)
        self._spb_vert_scale.setValue(100)
        lyt_opts_one = QtWidgets.QHBoxLayout()
        lyt_opts_one.addWidget(lbl_is_plotted)
        lyt_opts_one.addWidget(self._cbx_is_plotted)
        lyt_opts_one.addWidget(lbl_y_label)
        lyt_opts_one.addWidget(self._ltx_y_label)
        lyt_opts_one.addWidget(lbl_vert_scale)
        lyt_opts_one.addWidget(self._spb_vert_scale)

        #---------------------Row 2---------------------------
        lbl_y_axis_from = QtWidgets.QLabel('Y axis start')
        self._spb_y_axis_from = QtWidgets.QSpinBox()
        #self._spb_y_axis_from.setRange(-5, 100)
        self._spb_y_axis_from.setValue(0)
        lbl_y_axis_to = QtWidgets.QLabel('Y axis end')
        self._spb_y_axis_to = QtWidgets.QSpinBox()
        #self._spb_y_axis_to.setRange(0, 100)
        self._spb_y_axis_to.setValue(50)
        lbl_line_color = QtWidgets.QLabel('Line color')
        self._cmb_line_color = QtWidgets.QComboBox()
        self._cmb_line_color.addItems(LineColors)
        self._cmb_line_color.setCurrentText(def_color)
        lyt_opts_two = QtWidgets.QHBoxLayout()
        lyt_opts_two.addWidget(lbl_y_axis_from)
        lyt_opts_two.addWidget(self._spb_y_axis_from)
        lyt_opts_two.addWidget(lbl_y_axis_to)
        lyt_opts_two.addWidget(self._spb_y_axis_to)
        lyt_opts_two.addWidget(lbl_line_color)
        lyt_opts_two.addWidget(self._cmb_line_color)

        #---------------------Row 3---------------------------
        lbl_calc_integral = QtWidgets.QLabel('Calc integral')
        self._cbx_calc_integral = QtWidgets.QCheckBox()
        lbl_show_integral = QtWidgets.QLabel('Show on graph')
        self._cbx_show_integral = QtWidgets.QCheckBox()
        lyt_opts_three = QtWidgets.QHBoxLayout()
        lyt_opts_three .addWidget(lbl_calc_integral)
        lyt_opts_three.addWidget(self._cbx_calc_integral)
        lyt_opts_three .addWidget(lbl_show_integral)
        lyt_opts_three.addWidget(self._cbx_show_integral)

        self._lyt_main.addLayout(lyt_opts_one)
        self._lyt_main.addLayout(lyt_opts_two)
        self._lyt_main.addLayout(lyt_opts_three)

