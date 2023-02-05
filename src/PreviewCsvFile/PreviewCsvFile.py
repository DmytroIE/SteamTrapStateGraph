from PySide6 import QtCore, QtWidgets


class PreviewCsvFile(QtWidgets.QWidget):
    def __init__(self, load_csv_func):
        QtWidgets.QWidget.__init__(self)

        self._btn_csv_preview = QtWidgets.QPushButton('Preview CSV file')
        self._txt_csv_preview = QtWidgets.QTextBrowser()

        self._lbl_date_idx_col_name = QtWidgets.QLabel('Date/time index column')
        self._ltxt_date_idx_col_name = QtWidgets.QLineEdit()
        self._ltxt_date_idx_col_name.setText('Timestamp')
        self._lbl_col_sep = QtWidgets.QLabel('Column separator')
        self._cmb_col_sep = QtWidgets.QComboBox()
        self._cmb_col_sep.addItems([';', ':', 'Tab', ','])
        self._lyt_import_options = QtWidgets.QHBoxLayout()
        self._lyt_import_options.addWidget(self._lbl_date_idx_col_name)
        self._lyt_import_options.addWidget(self._ltxt_date_idx_col_name)
        self._lyt_import_options.addWidget(self._lbl_col_sep)
        self._lyt_import_options.addWidget(self._cmb_col_sep)

        self._btn_csv_load = QtWidgets.QPushButton('Load CSV file')
        
        self._layout = QtWidgets.QVBoxLayout(self)
        
        self._layout.addWidget(self._btn_csv_preview)
        self._layout.addWidget(self._txt_csv_preview)
        self._layout.addLayout(self._lyt_import_options)
        self._layout.addWidget(self._btn_csv_load)
        self._btn_csv_load.setEnabled(False)

        self._btn_csv_preview.clicked.connect(self.preview_csv_file)  
        self._btn_csv_load.clicked.connect(self.load_csv_file)

        self._csv_file_path = ''
        self._load_csv_func = load_csv_func

    @QtCore.Slot()
    def preview_csv_file(self):
        self._csv_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "/home", 'CSV files (*.csv);;All files (*)')
        csv_preview = ''
        try:
            with open(self._csv_file_path, "r") as csvFile:
                for i in range(5):
                    try:
                        line = csvFile.readline()
                        csv_preview += line
                    except:
                        break
            self._btn_csv_load.setEnabled(True)
        except Exception as error:
            csv_preview = str(error)
            self._btn_csv_load.setEnabled(False)
        finally:
            self._txt_csv_preview.setText(csv_preview)

    @QtCore.Slot()
    def load_csv_file(self):
        params = {'date_col_name': self._ltxt_date_idx_col_name.text(), 
                  'col_sep': self._cmb_col_sep.currentText()}
        self._load_csv_func(self._csv_file_path, params)
