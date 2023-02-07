from PySide6 import QtWidgets, QtCore
import matplotlib.pyplot as plt
import matplotlib as mpl

from src.CsvFileArea.CsvFileArea import CsvFileArea
from src.Communicate.Communicate import GlobalCommunicator

from src.utils.utils import get_file_name_from_path
from src.utils.settings import CsvFileSources, PlotStyleSettings


class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)

        plt.ion()
        #print(str(mpl.rcParams))
        #plt.style.use('seaborn-v0_8-paper')
        #print(str(mpl.rcParams))
        plt.rcParams.update(PlotStyleSettings)

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._tab_main = QtWidgets.QTabWidget()
        

        #--------Tab content--------------------
        self._btn_csv_preview = QtWidgets.QPushButton('Preview CSV file')
        self._txt_csv_preview = QtWidgets.QTextBrowser()

        self._lbl_date_idx_col_name = QtWidgets.QLabel('Date/time index column')
        self._ltx_date_idx_col_name = QtWidgets.QLineEdit()
        self._ltx_date_idx_col_name.setText('Timestamp')
        self._lbl_col_sep = QtWidgets.QLabel('Column separator')
        self._cmb_col_sep = QtWidgets.QComboBox()
        self._cmb_col_sep.addItems([';', ':', 'Tab', ','])
        self._lbl_csv_source = QtWidgets.QLabel('CSV Source')
        self._cmb_csv_source = QtWidgets.QComboBox()
        self._cmb_csv_source.addItems(CsvFileSources.values())
        self._lyt_import_options = QtWidgets.QHBoxLayout()
        self._lyt_import_options.addWidget(self._lbl_date_idx_col_name)
        self._lyt_import_options.addWidget(self._ltx_date_idx_col_name)
        self._lyt_import_options.addWidget(self._lbl_col_sep)
        self._lyt_import_options.addWidget(self._cmb_col_sep)
        self._lyt_import_options.addWidget(self._lbl_csv_source)
        self._lyt_import_options.addWidget(self._cmb_csv_source)

        self._btn_csv_load = QtWidgets.QPushButton('Load CSV file')
        self._btn_csv_load.setEnabled(False)

        self._wdg_tab_content = QtWidgets.QWidget()
        self._lyt_tab_content = QtWidgets.QVBoxLayout(self._wdg_tab_content)
        self._lyt_tab_content.addWidget(self._btn_csv_preview)
        self._lyt_tab_content.addWidget(self._txt_csv_preview)
        self._lyt_tab_content.addLayout(self._lyt_import_options)
        self._lyt_tab_content.addWidget(self._btn_csv_load)

        self._btn_csv_preview.clicked.connect(self.preview_csv_file)  
        self._btn_csv_load.clicked.connect(self.load_csv_file)

        #----------Main layout------------
        
        self._tab_main.addTab(self._wdg_tab_content, 'Preview CSV file')
        self._lyt_main.addWidget(self._tab_main)

        self._wdg_status_line = QtWidgets.QLabel('Status')
        self._lyt_main.addWidget(self._wdg_status_line)
        GlobalCommunicator.change_status_line.connect(self._wdg_status_line.setText)

        self._csv_file_tabs = []
        self._open_csv_files = []

    @QtCore.Slot()
    def load_csv_file(self):
        file_name = get_file_name_from_path(self._csv_file_path)
        if self._csv_file_path in self._open_csv_files:
            GlobalCommunicator.change_status_line.emit(f'File {file_name} is already open')
            return
        
        if self._cmb_csv_source.currentText() == CsvFileSources['STEAM_IQ']:
            new_area = CsvFileArea(plt)
        else:
            GlobalCommunicator.change_status_line.emit(f'No template for such source')
            return
        params = {'date_col_name': self._ltx_date_idx_col_name.text(), 
                  'col_sep': self._cmb_col_sep.currentText()}
        success = new_area.load_csv_file(self._csv_file_path, params)
        if success:
            self._csv_file_tabs.append(new_area)
            self._open_csv_files.append(self._csv_file_path)
            self._tab_main.addTab(new_area, file_name)
            
        else:
            del new_area
    
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
