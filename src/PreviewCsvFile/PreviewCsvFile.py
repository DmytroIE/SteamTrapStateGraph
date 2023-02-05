from PySide6 import QtCore, QtWidgets


class PreviewCsvFile(QtWidgets.QWidget):
    def __init__(self, load_csv_func):
        QtWidgets.QWidget.__init__(self)

        self.csv_preview_button = QtWidgets.QPushButton('Preview CSV file')
        self.csv_preview = QtWidgets.QTextBrowser()
        self.csv_load_button = QtWidgets.QPushButton('Load CSV file')

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.layout.addWidget(self.csv_preview_button)
        self.layout.addWidget(self.csv_preview)
        self.layout.addWidget(self.csv_load_button)

        self.csv_preview_button.clicked.connect(self.preview_csv_file)
        self.csv_load_button.clicked.connect(self.load_csv_file)

        self.csv_file_path = ''
        self.load_csv_func = load_csv_func

    @QtCore.Slot()
    def preview_csv_file(self):
        self.csv_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "/home", 'CSV files (*.csv);;All files (*)')
        csv_preview = ''
        try:
            with open(self.csv_file_path, "r") as csvFile:
                for i in range(5):
                    try:
                        line = csvFile.readline()
                        # print(f'Line = {line}')
                        csv_preview += line

                    except:
                        break
        except Exception as error:
            csv_preview = str(error)
        finally:
            # print(f'{csv_preview=}')
            self.csv_preview.setText(csv_preview)

    @QtCore.Slot()
    def load_csv_file(self):
        self.load_csv_func(self.csv_file_path)
