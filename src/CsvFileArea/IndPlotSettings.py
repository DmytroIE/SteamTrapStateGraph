from PySide6 import QtWidgets

from src.utils.utils import split_one_series_by_sb, resample_series, calc_integral
from src.utils.settings import line_colors_map



class IndPlotSettings(QtWidgets.QGroupBox):
    def __init__(self, df, col_name):
        QtWidgets.QGroupBox.__init__(self)
        self._df = df
        self._col_name = col_name

        self.setTitle(self._col_name)
        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._create_ui()

    def _prepare_plot_data(self, resample_options, service_breaks):
        srs = self._prepare_series(self)
        srs = split_one_series_by_sb(srs, service_breaks)
        srs = resample_series(srs, resample_options)

        if self._cbx_integral_on.checked():
            for rs in srs:
                result = calc_integral(rs)
                if result:
                    rs.integral = result[0]
                    rs.cum_time = result[1]
                    rs.mean_integr = result[0]/result[1]


    def plot(self, ax):
        pass


    def _prepare_series(self):
        return self._df[self._col_name]

    def _create_ui(self):
        
        #---------------------Row 1---------------------------
        lbl_is_plotted = QtWidgets.QLabel('Plot')
        self._cbx_is_plotted = QtWidgets.QCheckBox()
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
        self._cmb_line_color.addItems(line_colors_map.keys())
        lyt_opts_two = QtWidgets.QHBoxLayout()
        lyt_opts_two.addWidget(lbl_y_axis_from)
        lyt_opts_two.addWidget(self._spb_y_axis_from)
        lyt_opts_two.addWidget(lbl_y_axis_to)
        lyt_opts_two.addWidget(self._spb_y_axis_to)
        lyt_opts_two.addWidget(lbl_line_color)
        lyt_opts_two.addWidget(self._cmb_line_color)

        self._lyt_main.addLayout(lyt_opts_one)
        self._lyt_main.addLayout(lyt_opts_two)

