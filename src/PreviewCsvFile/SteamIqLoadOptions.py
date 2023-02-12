from PySide6 import QtCore, QtWidgets


class SteamIqLoadOptions(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self._lyt_main = QtWidgets.QHBoxLayout(self)
        self._create_ui()
    
    def _create_ui(self):
        lbl_date_idx_col_name = QtWidgets.QLabel('Date/time index column')
        self._ltx_date_idx_col_name = QtWidgets.QLineEdit()
        self._ltx_date_idx_col_name.setText('Timestamp')
        lbl_leak_col_name = QtWidgets.QLabel('Leak (%) column')
        self._ltx_leak_col_name = QtWidgets.QLineEdit()
        self._ltx_leak_col_name.setText('Leak')
        lbl_cycle_col_name = QtWidgets.QLabel('Cycle count column')
        self._ltx_cycle_col_name = QtWidgets.QLineEdit()
        self._ltx_cycle_col_name.setText('Cycle Counts')
        lbl_col_sep = QtWidgets.QLabel('Column separator')
        self._cmb_col_sep = QtWidgets.QComboBox()
        self._cmb_col_sep.addItems([';', ':', 'Tab', ','])

        self._lyt_main.addWidget(lbl_date_idx_col_name)
        self._lyt_main.addWidget(self._ltx_date_idx_col_name)
        self._lyt_main.addWidget(lbl_leak_col_name)
        self._lyt_main.addWidget(self._ltx_leak_col_name)
        self._lyt_main.addWidget(lbl_cycle_col_name)
        self._lyt_main.addWidget(self._ltx_cycle_col_name)
        self._lyt_main.addWidget(lbl_col_sep)
        self._lyt_main.addWidget(self._cmb_col_sep)
    
    def make_file_load_params(self):
        params = {}
        params['date_col_name'] = self._ltx_date_idx_col_name.text()
        params['leak_col_name'] = self._ltx_leak_col_name.text()
        params['cycle_col_name'] = self._ltx_cycle_col_name.text()
        params['col_sep'] = self._cmb_col_sep.currentText()
        return params

    
