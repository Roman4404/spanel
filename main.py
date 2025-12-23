# -*- coding: utf-8 -*-
import sys
import io
import os
import csv
import shutil
import subprocess
import sounddevice as sd
import soundfile as sf
from tinytag import TinyTag
import keyboard as kb
import soundcard as sc
import pyaudio
import darkdetect
import numpy as np
import wave
import shutil
import time
import sqlite3
import webbrowser
import edge_tts
import asyncio
import random
import librosa
from multiprocessing import Pool, Process
from PyQt6.QtCore import Qt, QSize


from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog, QInputDialog
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QIcon


class AddSoundError(Exception):
    pass


class FileAddError(AddSoundError):
    pass


class WorkToSoundFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.rus_keyboard = {"А": "F", "П": "G", "Р": "H", "О": "J", "Л": "K", "Д": "L", "Ж": ";", "Э": "'", "Й": "Q",
                             "Ц": "W", "У": "E", "К": "R", "Е": "T", "Н": "Y", "Г": "U", "Ш": "I", "Щ": "O",
                             "З": "P", "Х": "[", "Ъ": "]", "Я": "Z", "Ч": "X", "С": "C", "М": "V", "И": "B", "Т": "N",
                             "Ь": "M", "Б": ",", "Ю": ".", "Ё": "`", "Ф": "A", "Ы": "S", "В": "D"}
        global volume_value
        global key

    def copy_file(self):
        name_f = self.file_name[self.file_name.rfind('/') + 1:]
        shutil.copy2(f'{self.file_name}', f'./mainWindows/date/sound_vaults/{name_f}')
        return f'./mainWindows/date/sound_vaults/{name_f}'

    def add_file_in_bd(self, name_sound, table_profile):
        file_name = self.file_name
        # songs_file = open('./mainWindows/date/songs_info.csv', 'r', newline='', encoding="utf8")
        # read_song = csv.DictReader(songs_file, delimiter=';', quotechar='"')
        # read_song_sort = sorted(read_song, key=lambda x: int(x['id']), reverse=False)
        # if len(read_song_sort) == 0:
        #     last_id = 0
        # else:
        #     last_id = int(read_song_sort[-1]['id'])
        # songs_file.close()
        sound_file = TinyTag.get(file_name)
        len_sound_file = sound_file.duration
        format_file = file_name[-4:]
        key_final = str(key).upper()
        hot_key_old = WorkToHotKey(key_final)
        key_final = hot_key_old.rus_to_eng_keyboard()
        new_song_final = ["", key_final, name_sound, f'{int(len_sound_file // 60)}:{int(len_sound_file % 60)}', file_name, format_file]
        format_request = f'INSERT INTO {table_profile} (keyboards_key, song_name, run_song, file_name, format_file) VALUES (key_k, s_file, time_s, file_pyt, f_format);'
        format_request = format_request.replace('key_k', str('"' + new_song_final[1] + '"'))
        format_request = format_request.replace('s_file', str('"' + new_song_final[2] + '"'))
        format_request = format_request.replace('time_s', str('"' + new_song_final[3] + '"'))
        format_request = format_request.replace('file_pyt', str('"' + new_song_final[4] + '"'))
        format_request = format_request.replace('f_format', str('"' + new_song_final[5] + '"'))
        hot_key = WorkToHotKey(key_final)
        hot_key.add_hot_key_in_ram(file_name, format_file)
        con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        cur.execute(f'''{format_request}''').fetchall()
        con.commit()
        con.close()


class WorkToHotKey: #Государственный орган по отслеживанию деятельности горячих клавиш
    def __init__(self, hot_key):
        self.hot_key = hot_key
        self.rus_keyboard = {"А": "F", "П": "G", "Р": "H", "О": "J", "Л": "K", "Д": "L", "Ж": ";", "Э": "'", "Й": "Q", "Ц": "W", "У": "E", "К": "R", "Е": "T", "Н": "Y", "Г": "U", "Ш": "I", "Щ": "O",
                             "З": "P", "Х": "[", "Ъ": "]", "Я": "Z", "Ч": "X", "С": "C", "М": "V", "И": "B", "Т": "N", "Ь": "M", "Б": ",", "Ю": ".", "Ё": "`", "Ф": "A", "Ы": "S", "В": "D"}

        self.eng_keyboard = {'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л', 'L': 'Д', ';': 'Ж', "'": 'Э', 'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш',
                             'O': 'Щ', 'P': 'З', '[': 'Х', ']': 'Ъ', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М',
                             'B': 'И', 'N': 'Т', 'M': 'Ь', ',': 'Б', '.': 'Ю', '`': 'Ё', 'A': 'Ф', 'S': 'Ы', 'D': 'В'}

    def add_hot_key_busy(self):
        pass

    def remove_old_hot_key_busy(self):
        pass

    def remove_hot_key_busy(self):
        pass

    def add_hot_key_in_ram(self, file_name, format_file):
        if self.hot_key:
            t = WorkToOutputSoundInMicrophone(file_name, format_file)
            kb.add_hotkey(str(' '.join(map(str, str(self.hot_key).split()))).lower(), lambda: t.run())

    def stop_valve_sound(self):
        global res_volume_value
        global volume_value
        res_volume_value = 49
        volume_value = 0

    def rus_to_eng_keyboard(self):
        for i in self.hot_key:
            if i in self.rus_keyboard:
                self.hot_key = self.hot_key.replace(i, self.rus_keyboard[i])
        print(self.hot_key)
        return self.hot_key

class Interface(QMainWindow): #Интерфейс
    def __init__(self):
        super().__init__()
        if not os.path.isfile("./mainWindows/date/profile_info.sqlite") or not os.path.isfile(
                './mainWindows/date/settings_app.txt') or not os.path.isfile('./mainWindows/date/busy_hot_key.txt'):
            self.start_program()
        uic.loadUi("./mainWindows/Interface/New_base.ui", self)
        self.setWindowTitle('SPanel 0.3(Alpha)')
        try:
            with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
                read_l = f.readlines()
                text = read_l[1]
                t = text.split('-')
                a = t[1][:t[1].find("\n")]
                b = t[0]
                self.profile_now = a
                self.profile_now_table = b
        except FileNotFoundError:
            et = Tech_Windows()
            et.show()
            et.exec()
            self.close()
        self.btn_profile = dict()
        self.btn_group_profile = list()
        self.add_button.clicked.connect(self.add_sound)
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        self.names_sound = []
        if darkdetect.isDark():
            self.volume_up_icon = QPixmap('./mainWindows/Interface/image/volume_up_icon_white.png')
            # self.close_right_icon = QIcon('./mainWindows/Interface/image/right_icon_white.png')
            self.stop_icon = QPixmap('./mainWindows/Interface/image/stop_icon_white.png')
            self.micro_icon = QPixmap("./mainWindows/Interface/image/micro_icon_white.png")
        else:
            self.volume_up_icon = QPixmap('./mainWindows/Interface/image/volume_up_icon_dark.png')
            # self.close_right_icon = QIcon('./mainWindows/Interface/image/right_icon_dark.png')
            self.stop_icon = QPixmap('./mainWindows/Interface/image/stop_icon_dark.png')
            self.micro_icon = QPixmap("./mainWindows/Interface/image/micro_icon_dark.png")
        # self.hiding_profile_right_pushButton.setIcon(self.close_right_icon)
        # self.hiding_profile_right_pushButton.setIconSize(QSize(32, 32))
        self.settings_pushButton.clicked.connect(self.settings_profile)
        # self.play_icon = QPixmap("./mainWindows/Interface/image/play_and_pause_icon_white.png")
        # self.play_pushButton.setIcon(QIcon(self.play_icon))
        # self.play_pushButton.setIconSize(self.play_icon.rect().size())
        self.stop_pushButton.setIcon(QIcon(self.stop_icon))
        self.stop_pushButton.setIconSize(self.stop_icon.rect().size())
        self.volume_icon_label.setPixmap(self.volume_up_icon)
        self.start_program()
        global volume_value
        global micro_value
        volume_value = self.valuts_volums_verticalSlider.value()
        micro_value = self.valuts_vol_micro_verticalSlider.value() / 100
        self.valuts_volums_verticalSlider.valueChanged.connect(self.update_volume_value)
        self.valuts_vol_micro_verticalSlider.valueChanged.connect(self.update_volume_value)
        self.update_sound_table()
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        self.help_pushButton.clicked.connect(self.help)
        self.update_profile_tabel()
        self.tableWidget.cellDoubleClicked.connect(self.info_table_cell)
        self.tableWidget.cellChanged.connect(self.edit_name_song)
        background = QPixmap('./mainWindows/Interface/image/background.png')
        self.backgroand_img_label.setPixmap(background)
        self.AI_img_button = QPixmap("./mainWindows/Interface/image/Button_img_AI_Lession_text.png")
        self.pushButton_AI_song.setIcon(QIcon(self.AI_img_button))
        self.pushButton_AI_song.setIconSize(self.AI_img_button.rect().size())
        self.label_2_ai.hide()
        self.label_3_ai.hide()
        self.label_4_ai.hide()
        self.label_on_ai.hide()
        self.label_text_ai.hide()
        self.label_welcome_ai.hide()
        self.lineEdit_name_audio.hide()
        self.lineEdit_text_generated.hide()
        self.pushButton_generated.hide()
        self.comboBox_sing.hide()
        self.pushButton_back.hide()
        self.label_5_ai.hide()
        self.pushButton_AI_song.clicked.connect(self.to_go_ai_studio)
        self.pushButton_back.clicked.connect(self.back_go_ai_studio)
        self.ai = AI_Studio()
        self.pushButton_generated.clicked.connect(self.ai_start_generate)
        self.vol_micro_icon_label.setPixmap(self.micro_icon)
        self.valuts_vol_micro_lineEdit.setReadOnly(True)
        self.setFixedSize(862, 672)

        self.disable_editing(self.tableWidget)
        global stop_valve
        stop_valve = 0
        global stream_active_now
        stream_active_now = False
        kb.add_hotkey('ctrl + f', lambda: WorkToHotKey('ctrl + f').stop_valve_sound())
        MicrofonOutput('micro')

    def info_table_cell(self, row, column):
        table = self.sender()
        item_id = table.item(row, 0).text()
        if column == 1:
            self.edit_hot_key(table, row, item_id)

    def settings_profile(self):
        et = SettingsProfile()
        et.show()
        et.exec()
        self.update_profile_tabel()

    def start_program(self):
        try:
            with open('./mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
                read_l = f.readlines()
                volume_value = int(read_l[1][:-1])
                self.valuts_volums_verticalSlider.setValue(volume_value)
            self.update_hot_key()
        except FileNotFoundError:
            et = Tech_Windows()
            et.show()
            et.exec()
            self.close()

    def update_hot_key(self):
        con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        result = cur.execute(f'''SELECT * FROM {self.profile_now_table}''').fetchall()
        con.close()
        for item in result:
            hot_key = WorkToHotKey(item[1])
            hot_key.add_hot_key_in_ram(item[4], item[5])

    def add_sound(self):
        try:
            file_name = QFileDialog.getOpenFileName(self, 'Выберите звук для добавления', '', 'Wave and MP3 file (*.wav; *mp3)')[0]
            if file_name == '':
                raise FileAddError('')
            elif file_name[file_name.rfind('.'):] == '.mp3':
                pass
            elif not TinyTag.is_supported(file_name):
                raise FileAddError('Выбран не подерживающися формат')
            et = FinalDialogWindowAddSound(file_name, self.btn_profile)
            et.show()
            et.exec()
            self.update_sound_table()
        except AddSoundError as s:
            pass
            # print(s)

    def update_volume_value(self):
        global volume_value
        global micro_value
        volume_value = self.valuts_volums_verticalSlider.value()
        micro_value = self.valuts_vol_micro_verticalSlider.value() / 100
        self.valuts_vol_micro_lineEdit.setText(str(self.valuts_vol_micro_verticalSlider.value()) + "%")

    def stop_valve_sound(self):
        global res_volume_value
        global volume_value
        global stream_active_now
        if stream_active_now:
            res_volume_value = self.valuts_volums_verticalSlider.value()
            volume_value = -1

    def update_profile_tabel(self):
        while self.profile_verticalLayout.count() > 0:
            widgetToRemove = self.profile_verticalLayout.takeAt(0).widget()
            if widgetToRemove == None:
                break
            else:
                widgetToRemove.setParent(None)
        con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        res = cur.execute('''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()
        res = res[:-1]
        con.close()
        with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            for text in read_l[1:]:
                t = text.split('-')
                a = t[1][:t[1].find("\n")]
                b = t[0]
                self.btn_profile[a] = self.btn_profile.get(a, b)
                btn = QPushButton(a, self)
                if a == self.profile_now:
                    btn.setEnabled(False)
                    btn.setDown(True)
                btn.clicked.connect(self.click_button)
                self.profile_verticalLayout.addWidget(btn)
                self.btn_group_profile.append(btn)
        self.profile_verticalLayout.addStretch()

    def update_sound_table(self):
        con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        result = cur.execute(f'''SELECT * FROM {self.profile_now_table}''').fetchall()
        con.close()
        title = ['id','Клавиши','Название аудио', 'Время','file_name','format_file']
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 420)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 0)
        self.tableWidget.setColumnWidth(5, 0)

    def disable_editing(self, tableWidget):
        for row in range(tableWidget.rowCount()):
            for column in range(tableWidget.columnCount()):
                if column != 2:
                    item = tableWidget.item(row, column)
                    if item is not None:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def edit_hot_key(self, table, row, item_id):
        global key
        key = ''
        et = RecordHotKeyDialogWindow("Test")
        et.show()
        et.exec()
        if key:
            item = QTableWidgetItem(str(key))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 1, item)
            con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
            cur = con.cursor()
            cur.execute(f'''UPDATE {self.profile_now_table} SET keyboards_key == "{str(key)}" WHERE id == "{str(item_id)}"''').fetchall()
            con.commit()
            con.close()

    def edit_name_song(self, row, column):
        if column == 2:
            table = self.sender()
            item_id = table.item(row, 0).text()
            name = table.item(row, column).text()
            con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
            cur = con.cursor()
            cur.execute(
                f'''UPDATE {self.profile_now_table} SET song_name == "{str(name)}" WHERE id == "{str(item_id)}"''').fetchall()
            con.commit()
            con.close()

    def click_button(self):
        self.profile_now = self.sender().text()
        self.profile_now_table = self.btn_profile[self.profile_now]
        kb.unhook_all_hotkeys()
        self.update_hot_key()
        self.update_profile_tabel()
        self.update_sound_table()

    def to_go_ai_studio(self):
        self.pushButton_AI_song.hide()
        self.label_welcome.hide()
        self.label_2_ai.show()
        self.label_3_ai.show()
        self.label_4_ai.show()
        self.label_on_ai.show()
        self.label_text_ai.show()
        self.label_welcome_ai.show()
        self.lineEdit_name_audio.show()
        self.lineEdit_text_generated.show()
        self.pushButton_generated.show()
        self.comboBox_sing.show()
        self.pushButton_back.show()
        self.label_5_ai.show()
        self.pushButton_back.setEnabled(True)
        self.lineEdit_name_audio.setEnabled(True)
        self.lineEdit_text_generated.setEnabled(True)
        self.comboBox_sing.setEnabled(True)
        self.label_on_ai.setEnabled(True)
        self.pushButton_generated.setEnabled(True)
        self.lineEdit_text_generated.setText('Хамстер крименал')
        self.lineEdit_name_audio.setText(f'name_audio{random.randint(0, 127899)}')

    def back_go_ai_studio(self):
        self.pushButton_AI_song.show()
        self.label_welcome.show()
        self.label_2_ai.hide()
        self.label_3_ai.hide()
        self.label_4_ai.hide()
        self.label_on_ai.hide()
        self.label_text_ai.hide()
        self.label_welcome_ai.hide()
        self.lineEdit_name_audio.hide()
        self.lineEdit_text_generated.hide()
        self.pushButton_generated.hide()
        self.comboBox_sing.hide()
        self.pushButton_back.hide()
        self.label_5_ai.hide()
        self.pushButton_back.setEnabled(False)
        self.lineEdit_name_audio.setEnabled(False)
        self.lineEdit_text_generated.setEnabled(False)
        self.comboBox_sing.setEnabled(False)
        self.label_on_ai.setEnabled(False)
        self.pushButton_generated.setEnabled(False)

    def ai_start_generate(self):
        file_name = self.ai.start_generate(str(self.lineEdit_text_generated.text()), str(self.lineEdit_name_audio.text()), str(self.comboBox_sing.currentText()))
        et = FinalDialogWindowAddSound(file_name, self.btn_profile)
        et.show()
        et.exec()
        self.update_sound_table()


    def help(self):
        webbrowser.open('https://github.com/Roman4404/spanel/wiki')

    def closeEvent(self, event):
        with open('./mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            device = read_l[0][:-1]
        with open('./mainWindows/date/settings_app.txt', 'w', newline='', encoding="utf8") as f:
            print(device, file=f)
            print(self.valuts_volums_verticalSlider.value(), file=f)
        event.accept()


class FinalDialogWindowAddSound(QDialog):

    def __init__(self, file_name, table_info):
        super().__init__()
        uic.loadUi("./mainWindows/Interface/final_add_sound.ui", self)
        self.file_name = file_name
        self.table_info = table_info
        self.name_sound_lineEdit.setText(str(file_name[file_name.rfind('/') + 1:file_name.rfind('.')]))
        self.ok_pushButton.clicked.connect(self.run)
        self.file_select_other_pushButton.clicked.connect(self.other_file)
        self.cancel_pushButton.clicked.connect(self.stop)
        self.to_record_window_pushButton.clicked.connect(self.record_hot_key)
        self.setWindowTitle('Добавление звука')
        self.start()
        global volume_value
        global key
        key = ''

    def start(self):
        con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        res = cur.execute('''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()
        res = res[:-1]
        con.close()
        with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            for text in read_l[1:]:
                t = text.split('-')
                a = t[1][:t[1].find("\n")]
                b = t[0]
                self.profile_selection_comboBox.addItem(a)

    def run(self):
        new_sound_file = WorkToSoundFile(self.file_name)
        file_name = new_sound_file.copy_file()
        if file_name[file_name.rfind('.'):] == '.mp3':
            self.convertor_mp3_to_wav(file_name)
            file_name = file_name[:file_name.rfind('.')] + '.wav'
        new_sound_file = WorkToSoundFile(file_name)
        new_sound_file.add_file_in_bd(name_sound=self.name_sound_lineEdit.text(),table_profile=self.table_info[self.profile_selection_comboBox.currentText()])
        print(self.profile_selection_comboBox.currentText())
        self.close()

    def stop(self):
        self.close()

    def record_hot_key(self):
        et = RecordHotKeyDialogWindow(self.file_name)
        et.show()
        et.exec()
        self.hot_key_lineEdit.setText(str(key).upper())

    def convertor_mp3_to_wav(self, file_name):
        # Загружаем MP3 файл
        audio, sr = librosa.load(file_name, sr=None)  # sr=None сохраняет оригинальную частоту

        # Сохраняем в WAV
        sf.write(f"{file_name[:file_name.rfind('.')]}.wav", audio, sr)

        os.remove(file_name)

    def other_file(self):
        try:
            file_name = QFileDialog.getOpenFileName(self, 'Выберите звук для добавления', '', 'Wave and MP3 file (*.wav; *mp3)')[0]
            if file_name == '':
                raise FileAddError('')
            elif not TinyTag.is_supported(file_name):
                raise FileAddError('Выбран не подерживающися формат')
            self.file_name = file_name
            self.name_sound_lineEdit.setText(str(file_name))
        except AddSoundError as s:
            pass
            # print(s)


class RecordHotKeyDialogWindow(QDialog):

    def __init__(self, file_name):
        super().__init__()
        uic.loadUi("./mainWindows/Interface/record_hot_key.ui", self)
        self.file_name = file_name
        self.cancel_pushButton.clicked.connect(self.stop)
        self.record_pushButton.clicked.connect(self.run)
        self.reset_pushButton.clicked.connect(self.other_hot_key)
        self.reset_pushButton.setEnabled(False)
        self.ok_pushButton.setEnabled(False)
        self.ok_pushButton.clicked.connect(self.ok)
        self.setWindowTitle('Запись клавиши')

    def run(self):
        self.record_pushButton.hide()
        self.record_pushButton.setEnabled(False)
        self.key = kb.read_hotkey(suppress = False)
        hot_key = WorkToHotKey(str(self.key).upper())
        self.key = hot_key.rus_to_eng_keyboard()
        self.hot_key_view.setText(f'{str(self.key)}')
        self.reset_pushButton.setEnabled(True)
        self.ok_pushButton.setEnabled(True)

    def stop(self):
        self.close()

    def ok(self):
        global key
        key = self.key
        self.close()

    def other_hot_key(self):
        self.key = set()
        self.record_pushButton.setVisible(True)
        self.record_pushButton.setEnabled(True)
        self.hot_key_view.setText(f'')

def index_input():
    with open('./mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
        read_l = f.readlines()
        str_inp = read_l[0][2:-1]
        index_inp = 2
        devices = list(sd.query_devices())
        for device in devices:
            if device['name'] == str_inp:
                index_inp = device['index']
                break
    return index_inp

def index_output():
    devices = list(sd.query_devices())
    for device in devices[::-1]:
        if device['name'] == 'Output (VB-Audio Point)':
            if device['max_output_channels'] == 16:
                return device['index']

def index_out_system():
    index_inp = 5
    devices = list(sd.query_devices())
    for device in devices:
        if device['name'] == 'CABLE Input (VB-Audio Virtual C':
            index_inp = device['index']
            break
    return index_inp

def index_inp_system():
    index_inp = 2
    devices = list(sd.query_devices())
    for device in devices:
        if device['name'] == 'Input (VB-Audio Point)':
            index_inp = device['index']
            break
    return index_inp

class SettingsProfile(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('./mainWindows/Interface/profile_settings.ui', self)
        self.update_profile_tabel()
        self.ok_pushButton.clicked.connect(self.close_window)
        self.profile_listWidget.itemClicked.connect(self.click_profile)
        self.edit_name_pushButton.setEnabled(False)
        self.del_pushButton.setEnabled(False)
        self.edit_name_pushButton.clicked.connect(self.edit_name_profile)
        self.add_button.clicked.connect(self.add_profile)
        self.del_pushButton.clicked.connect(self.del_profile)
        self.setWindowTitle('Настройки профелей')

    def update_profile_tabel(self):
        self.profile_listWidget.clear()
        con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        res = cur.execute('''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()
        res = res[:-1]
        con.close()
        with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            for text in read_l[1:]:
                t = text.split('-')
                a = t[1][:t[1].find("\n")]
                b = t[0]
                self.profile_listWidget.addItem(a)

    def click_profile(self, item):
        self.click_profile_label.setText(item.text())
        n_profile = self.profile_listWidget.count()
        self.edit_name_pushButton.setEnabled(True)
        if n_profile != 1:
            self.del_pushButton.setEnabled(True)

    def add_profile(self):
        text, ok = QInputDialog.getText(self, 'Новый профиль:', 'Название профиля:')
        if ok and text:
            current_row = self.profile_listWidget.currentRow()
            self.profile_listWidget.insertItem(current_row + 1, text)
            with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
                old_d = f.read()
            num = int(old_d[:old_d.find('\n')]) + 1
            old_d = old_d.replace(old_d[:old_d.find('\n')], str(str(num)), 1)
            with open('./mainWindows/date/settings_profile.txt', 'w', encoding="utf8") as f:
                f.write(old_d + str(f'profile{num}_info' + '-' + text +'\n'))
            con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
            cur = con.cursor()
            cur.execute(f'''CREATE TABLE profile{num}_info (
                                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                                    keyboards_key TEXT    NOT NULL,
                                    song_name     TEXT    NOT NULL,
                                    run_song      TEXT    NOT NULL,
                                    file_name     TEXT    NOT NULL,
                                    format_file   TEXT    NOT NULL 
                                );''').fetchall()
            con.close()
            self.click_profile_label.setText(text)

    def edit_name_profile(self):
        t = self.click_profile_label.text()
        text, ok = QInputDialog.getText(self, 'Переминовка:', 'Новое название:')
        if ok and text:
            with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
                old_d = f.read()

            new_d = old_d.replace(t, text)

            with open('./mainWindows/date/settings_profile.txt', 'w', encoding="utf8") as f:
                f.write(new_d)

            self.update_profile_tabel()
            self.click_profile_label.setText(text)

    def del_profile(self):
        t = self.click_profile_label.text()
        with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
            data = f.read()
        name_table = data[data[:data.find(t) - 1].rfind('\n') + 1 :data.find(t) - 1]
        step_table = data[data[:data.find(t) - 1].rfind('\n') :data[data[:data.find(t) - 1].rfind('\n') + 1].find('\n')]
        num = int(data[:data.find('\n')]) - 1
        data = data.replace(str(str(num + 1)), str(str(num)), 1)
        data = data.replace(step_table, "")
        with open('./mainWindows/date/settings_profile.txt', 'w', encoding="utf8") as f:
            f.write(data)
        con = sqlite3.connect("./mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        cur.execute(f'''DROP TABLE {name_table}''')
        self.click_profile_label.setText('')
        self.update_profile_tabel()

    def close_window(self):
        self.close()

class WorkToOutputSoundInMicrophone:

    def __init__(self, file_name, format_file):
        self.file_name = file_name
        self.format_file = format_file

    def run(self):
        global volume_value
        global stop_valve
        global res_volume_value
        global stream_active_now
        stream_active_now = True
        res_volume_value = volume_value
        if self.format_file == '.wav':
            wf = wave.open(self.file_name, 'rb')

        def callback(in_data, frame_count, time_info, status):
            if self.format_file != 'read':
                data = wf.readframes(frame_count)
                audio_data = np.frombuffer(data, dtype=np.int16)
                self.volume_value = int(volume_value) / 100

                if self.volume_value == float(-0.01):
                    stream.close()
                audio_data = (audio_data * self.volume_value).astype(np.int16)
            else:
                pass
            return (audio_data.tobytes(), pyaudio.paContinue)


        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback, output_device_index=index_out_system())

        try:
            while stream.is_active():
                pass
        except OSError:
            pass

        stream.close()
        p.terminate()
        volume_value = res_volume_value
        stream_active_now = False
        wf.close()


class MicrofonOutput:
    def __init__(self, status):
        if status == 'micro':
            self.start_microphon()


    def callback_input(self, in_data, frame_count, time_info, status):
        global micro_value
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        audio_data = (audio_data * micro_value).astype(np.int16)
        return (audio_data, pyaudio.paContinue)

    def start_microphon(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        input=True,
                        output=True,
                        stream_callback=self.callback_input, input_device_index=index_input(), output_device_index=index_out_system())

    def stop(self):
        self.stream_n.close()


class Tech_Windows(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('./mainWindows/Interface/tech_windows.ui', self)
        self.setWindowTitle('Техническое окно')
        self.ok_pushButton.clicked.connect(self.stop)

    def stop(self):
        shutil.rmtree('./mainWindows/date')
        self.close()


class AI_Studio:
    def __init__(self):
        self.SUPPORTED_VOICES = {
            'DmitryNeural-Руский(муж.)': 'ru-RU-DmitryNeural',
            'SvetlanaNeural-Русский(жен.)': 'ru-RU-SvetlanaNeural',
        }

    async def generate_audio(self, text, name_file, voice_name):
        communicate = edge_tts.Communicate(text,
                                           self.SUPPORTED_VOICES[voice_name],
                                           # rate=rates,
                                           # volume=volumes,
                                           proxy=None)
        await communicate.save(str(name_file + ".mp3"))

    def start_generate(self, text, name_file, voice_name):
        asyncio.run(self.generate_audio(text, name_file, voice_name))
        return str(name_file + ".mp3")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./mainWindows/Interface/image/icon.png'))
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
