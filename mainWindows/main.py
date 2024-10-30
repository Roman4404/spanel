import sys
import io

from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtWidgets import QPushButton, QLabel


class Interface(QMainWindow): #Интерфейс
    def __init__(self):
        super().__init__()
        uic.loadUi("Base.ui", self)
        self.add_button.clicked.connect(self.add_sound)
        self.names_sound = []

    def add_sound(self):
        file_name = QFileDialog.getOpenFileNames(self, 'Open file', "C:\\Users\\rvlen")
        if file_name[0][0][-4:] == ".png":
            sound_name = file_name[0][0]
            sound_name_ui = QLabel(f'{sound_name}',self)
            sound_name_ui.resize(200, 50)
            self.verticalLayout_3.addWidget(sound_name_ui)
            self.verticalLayout_3.addStretch()
        else:
            print('No good')





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
