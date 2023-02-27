from PySide6 import QtWidgets, QtCore
import matplotlib.pyplot as plt
import matplotlib as mpl

from src.CsvFileArea.CsvFileArea import CsvFileArea
from src.CsvFileArea.SteamIqCsvFileArea import SteamIqCsvFileArea
from src.Communicate.Communicate import GlobalCommunicator
from src.PreviewCsvFile.SteamIqLoadOptions import SteamIqLoadOptions

from src.utils.utils import get_file_name_from_path
from src.utils.settings import CsvFileSources, PlotStyleSettings


class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)

        plt.ion()
        #print(str(mpl.rcParams))
        #plt.style.use('seaborn-v0_8-paper')
        #print(str(mpl.rcParams))
        #plt.rcParams.update(PlotStyleSettings)

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._create_ui()

        self._csv_file_tabs = []
        self._open_csv_files = []

    @QtCore.Slot()
    def load_csv_file(self):
        file_name = get_file_name_from_path(self._csv_file_path)
        
        if self._csv_file_path in self._open_csv_files:
            GlobalCommunicator.change_status_line.emit(f'File {file_name} is already open')
            return
        
        match self._cmb_csv_source.currentText():
            case CsvFileSources.SteamIQ:
                new_area = SteamIqCsvFileArea(plt)
            case _:
                GlobalCommunicator.change_status_line.emit(f'No template for such source')
                return
        params = self._wdg_import_options.make_file_load_params()
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
        if not self._csv_file_path:
            return
        
        file_name = get_file_name_from_path(self._csv_file_path)
        
        try:
            csv_preview = ''
            number_of_lines = 0
            
            with open(self._csv_file_path, "r") as csvFile:
                for line in csvFile:
                    if number_of_lines < 5:
                        csv_preview += line
                    number_of_lines += 1
            if number_of_lines == 0:
                GlobalCommunicator.change_status_line.emit(f'The file is empty')
                return
            else:
                self._btn_csv_load.setEnabled(True)
                self._txt_csv_preview.setText(csv_preview + f'...\nTotal lines: {number_of_lines}')
                GlobalCommunicator.change_status_line.emit(f'File {file_name} is open for preview')

        except Exception as error:
            csv_preview = str(error)
            self._btn_csv_load.setEnabled(False)
            GlobalCommunicator.change_status_line.emit(f'Cannot open file for preview')
    
    def _create_ui(self):
        
        self._tab_main = QtWidgets.QTabWidget()
        
        #--------Tab content--------------------
        self._btn_csv_preview = QtWidgets.QPushButton('Preview CSV file')
        self._txt_csv_preview = QtWidgets.QTextBrowser()

        lbl_date_idx_col_name = QtWidgets.QLabel('Date/time index column')
        self._ltx_date_idx_col_name = QtWidgets.QLineEdit()
        self._ltx_date_idx_col_name.setText('Timestamp')
        self._lbl_col_sep = QtWidgets.QLabel('Column separator')
        self._cmb_col_sep = QtWidgets.QComboBox()
        self._cmb_col_sep.addItems([';', ':', 'Tab', ','])
        lbl_csv_source = QtWidgets.QLabel('CSV Source')
        self._cmb_csv_source = QtWidgets.QComboBox()
        self._cmb_csv_source.addItems(CsvFileSources)
        self._cmb_csv_source.currentTextChanged.connect(self._change_import_optinons_wdg)
        lyt_import_options = QtWidgets.QHBoxLayout()
        lyt_import_options.addWidget(lbl_csv_source)
        lyt_import_options.addWidget(self._cmb_csv_source)

        self._btn_csv_load = QtWidgets.QPushButton('Load CSV file')
        self._btn_csv_load.setEnabled(False)

        wdg_tab_content = QtWidgets.QWidget()
        self._lyt_tab_content = QtWidgets.QVBoxLayout(wdg_tab_content)
        self._lyt_tab_content.addWidget(self._btn_csv_preview)
        self._lyt_tab_content.addWidget(self._txt_csv_preview)
        self._lyt_tab_content.addLayout(lyt_import_options)
        self._change_import_optinons_wdg(CsvFileSources.SteamIQ)
        self._lyt_tab_content.addWidget(self._btn_csv_load)

        self._btn_csv_preview.clicked.connect(self.preview_csv_file)  
        self._btn_csv_load.clicked.connect(self.load_csv_file)

        #----------Main layout------------
        
        self._tab_main.addTab(wdg_tab_content, 'Preview CSV file')
        self._lyt_main.addWidget(self._tab_main)

        self._wdg_status_line = QtWidgets.QLabel('Status')
        self._lyt_main.addWidget(self._wdg_status_line)
        GlobalCommunicator.change_status_line.connect(self._wdg_status_line.setText)

    def _change_import_optinons_wdg(self, text):
        if hasattr(self, '_wdg_import_options'):
            self._lyt_tab_content.removeWidget(self._wdg_import_options)
            self._wdg_import_options.deleteLater()
        match text:
            case CsvFileSources.SteamIQ:
                self._wdg_import_options = SteamIqLoadOptions()
                self._lyt_tab_content.addWidget(self._wdg_import_options)
            case _:
                self._wdg_import_options = QtWidgets.QPushButton('Temp button')
                self._lyt_tab_content.addWidget(self._wdg_import_options)

                
        




