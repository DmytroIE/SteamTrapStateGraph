from PySide6 import QtWidgets

from src.PreviewCsvFile.PreviewCsvFile import PreviewCsvFile
from src.CsvFileArea.CsvFileArea import CsvFileArea

from src.utils.utils import get_file_name_from_path

class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._tab_main = QtWidgets.QTabWidget()

        self._wdg_preview_csv_file = PreviewCsvFile(self.load_csv_file)

        self._tab_main.addTab(self._wdg_preview_csv_file, 'Preview CSV file')
        self._lyt_main.addWidget(self._tab_main)

        self._wdg_status_widget = QtWidgets.QLabel('Status')
        self._lyt_main.addWidget(self._wdg_status_widget)

        self._csv_file_tabs = []

    def load_csv_file(self, path):
        new_area = CsvFileArea()
        file_name = get_file_name_from_path(path)

        success, error = new_area.load_csv_file(path)
        if success:
            self._csv_file_tabs.append(new_area)
            self._tab_main.addTab(new_area, file_name)
            self._wdg_status_widget.setText(f'File {file_name} loaded')
        else:
            self._wdg_status_widget.setText(f'File loading failed, {error}')
            del new_area
