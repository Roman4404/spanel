import sys
import os
import subprocess
import requests
import zipfile
import sounddevice as sd
import sqlite3
import webbrowser
from PyQt6.QtCore import Qt
from PyQt6 import uic, QtWidgets  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QIcon
from Tools.scripts.pindent import start

def help():
    webbrowser.open('https://github.com/Roman4404/spanel/wiki')


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        uic.loadUi("./Initial_Setup_Windows/Interface/Base.ui", self)
        background = QPixmap('./Initial_Setup_Windows/Interface/image/background.png')
        welcome_words = QPixmap('./Initial_Setup_Windows/Interface/image/Welcome_words_spanel.png')
        os.makedirs('./mainWindows/date')
        os.makedirs('./mainWindows/date/sound_vaults')
        self.backgroand_img_label.setPixmap(background)
        self.Welcome_words_label.setPixmap(welcome_words)
        #self.text_welcome_label.setPixmap(text_welcome)
        self.start_pushButton.clicked.connect(self.go_to_next_stage)

    def go_to_next_stage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)



class Stage1SitingsMicrofon(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        uic.loadUi('./Initial_Setup_Windows/Interface/stage_1_sitings_microfon.ui', self)
        background = QPixmap('./Initial_Setup_Windows/Interface/image/background.png')
        self.backgroand_img_label.setPixmap(background)
        self.update_list_divies()
        self.update_pushButton.clicked.connect(self.update_list_divies)
        self.next_pushButton.clicked.connect(self.next_step)
        self.back_pushButton.clicked.connect(self.back_step)
        self.help_commandLinkButton.clicked.connect(help)

    def update_list_divies(self): #Функция обновления по кнопки не работает
        self.list_devices_comboBox.clear()
        devices = list(sd.query_devices())
        for device in devices:
            if device['index'] == 0:
                continue
            elif device['max_output_channels'] != 0:
                break
            elif device['max_input_channels'] != 0:
                self.list_devices_comboBox.addItem(f'{device["index"]} {device["name"]}')

    def next_step(self):
        with open('./mainWindows/date/settings_app.txt', 'w', newline='', encoding="utf8") as f:
            print(self.list_devices_comboBox.currentText(), file=f)
            print('99', file=f)
        Stage2 = WaitStage()
        widget.addWidget(Stage2)
        widget.setCurrentIndex(2)

    def back_step(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


class WaitStage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./Initial_Setup_Windows/Interface/stage_2_waiting_driver.ui', self)
        background = QPixmap('./Initial_Setup_Windows/Interface/image/background.png')
        self.backgroand_img_label.setPixmap(background)
        self.next_pushButton.clicked.connect(self.start_download)
        self.back_pushButton.clicked.connect(self.back_step)
        self.help_commandLinkButton.clicked.connect(help)


    def start_download(self):
        if self.next_pushButton.text() == 'Начать':
            self.next_pushButton.setEnabled(False)
            self.back_pushButton.setEnabled(False)
            self.download_vb_cable()
            self.extract_zip(self.output_file, "VBCABLE_Driver")
            self.install_vb_cable("VBCABLE_Driver\VBCABLE_Setup_x64.exe")
            self.process_label.setText("Установщик завершил работу.")
            self.next_pushButton.setEnabled(True)
            self.next_pushButton.setText('Продолжить')
            #print(sd.query_devices())
        elif self.next_pushButton.text() == 'Продолжить':
            Stage3 = FinishStage()
            widget.addWidget(Stage3)
            widget.setCurrentIndex(3)

    def install_vb_cable(self, installer_path):
        self.process_label.setText("Запуск установщика VB-CABLE...")
        try:
            subprocess.run(installer_path, shell=True, check=True)
            self.process_label.setText("Установщик завершил работу.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка выполнения установщика: {e}")

    def download_vb_cable(self):
        url_driver = 'https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip'
        self.output_file = 'VBCABLE_Driver_Pack45.zip'
        response = requests.get(url_driver, stream=True)
        if response.status_code == 200:
            with open(self.output_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            self.process_label.setText("VB-CABLE загружен")
        else:
            pass
            # print("Ошибка загрузки файла:", response.status_code)

    def extract_zip(self, file_path, extract_to):
        self.process_label.setText("Распаковка VB-CABLE...")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            self.process_label.setText("Распаковано")

    def back_step(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


class FinishStage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./Initial_Setup_Windows/Interface/stage_wait.ui', self)
        background = QPixmap('./Initial_Setup_Windows/Interface/image/background.png')
        done_words = QPixmap('./Initial_Setup_Windows/Interface/image/Done_words_spanel.png')
        self.Welcome_words_label.setPixmap(done_words)
        self.backgroand_img_label.setPixmap(background)
        with open('./mainWindows/date/busy_hot_key.txt', 'w', newline='', encoding="utf8") as f:
            pass
        connection = sqlite3.connect('./mainWindows/date/profile_info.sqlite')
        connection.close()
        with open('./mainWindows/date/settings_profile.txt', 'w', newline='', encoding="utf8") as f:
            print('1', file=f)
            print('profile1_info-Профель 1', file=f)
        con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        cur.execute('''CREATE TABLE profile1_info (
                                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                                keyboards_key TEXT    NOT NULL,
                                song_name     TEXT    NOT NULL,
                                run_song      TEXT    NOT NULL,
                                file_name     TEXT    NOT NULL,
                                format_file   TEXT    NOT NULL 
                            );''').fetchall()
        con.close()
        self.next_pushButton.clicked.connect(self.run)

    def run(self):
        widget.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./mainWindows/Interface/image/icon.png'))
    widget = QtWidgets.QStackedWidget()
    widget.setWindowTitle('Настройка SPanel')
    Base = Interface()
    Stage1 = Stage1SitingsMicrofon()
    widget.addWidget(Base)
    widget.addWidget(Stage1)
    Base.start_pushButton.clicked.connect(lambda: widget.setCurrentIndex(1))
    widget.show()
    sys.exit(app.exec())