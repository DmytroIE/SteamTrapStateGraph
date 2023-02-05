from PySide6 import QtCore, QtWidgets

import pandas as pd


class CsvFileArea(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.csv_preview_button = QtWidgets.QPushButton('CSV file loaded')

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.layout.addWidget(self.csv_preview_button)

    

    def load_csv_file(self, path):
        try:
            data = pd.read_csv(path, sep=';', header=0)
            print(data.head())
            # self.csv_preview.setText(data.head())
            return True, None
        except Exception as error:
            # self.text.setText(f'Error occured while opening file {text[0]}')
            print(error)
            return False, str(error)