import sys
import io
import os
import keyboard as kb
import numpy as np
import sounddevice as sd
from PyQt6.QtCore import Qt
from PyQt6 import uic, QtWidgets  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QIcon



class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        uic.loadUi("./Interface/Base.ui", self)
        background = QPixmap('./Interface/image/background.png')
        welcome_words = QPixmap('./Interface/image/Welcome_words_spanel.png')
        self.backgroand_img_label.setPixmap(background)
        self.Welcome_words_label.setPixmap(welcome_words)
        #self.text_welcome_label.setPixmap(text_welcome)
        self.start_pushButton.clicked.connect(self.go_to_next_stage)

    def go_to_next_stage(self):
        print(1)
        widget.setCurrentIndex(widget.currentIndex() + 1)



class Stage1SitingsMicrofon(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./Interface/stage_1_sitings_microfon.ui', self)
        background = QPixmap('./Interface/image/background.png')
        self.backgroand_img_label.setPixmap(background)
        self.update_list_divies()
        self.update_pushButton.clicked.connect(self.update_list_divies)
        self.next_pushButton.clicked.connect(self.next_step)

    def update_list_divies(self): #Функция обновления по кнопки не работает
        self.list_devices_comboBox.clear()
        devices = list(sd.query_devices())
        print(sd.query_devices())
        for device in devices:
            if device['index'] == 0:
                continue
            elif device['max_input_channels'] != 0:
                self.list_devices_comboBox.addItem(f'{device["index"]} {device["name"]}')
            elif device['max_output_channels'] != 0:
                break

    def next_step(self):
        with open('../mainWindows/date/settings_app.txt', 'w', newline='', encoding="utf8") as f:
            print(self.list_devices_comboBox.currentText(), file=f)
            print('99', file=f)
        widget.setCurrentIndex(2)


class WaitStage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./Interface/stage_wait.ui', self)
        background = QPixmap('./Interface/image/background.png')
        self.backgroand_img_label.setPixmap(background)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    Base = Interface()
    Stage1 = Stage1SitingsMicrofon()
    Stage2 = WaitStage()
    widget.addWidget(Base)
    widget.addWidget(Stage1)
    widget.addWidget(Stage2)
    Base.start_pushButton.clicked.connect(lambda: widget.setCurrentIndex(1))
    widget.show()
    sys.exit(app.exec())