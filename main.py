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
import pyaudio
import darkdetect
import numpy as np
import wave
import time
import sqlite3
import webbrowser
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
        new_song_final = ['', str(key).upper(), name_sound, f'{int(len_sound_file // 60)}:{int(len_sound_file % 60)}', file_name, format_file]
        format_request = f'INSERT INTO {table_profile} (keyboards_key, song_name, run_song, file_name, format_file) VALUES (key_k, s_file, time_s, file_pyt, f_format);'
        format_request = format_request.replace('key_k', str('"' + new_song_final[1] + '"'))
        format_request = format_request.replace('s_file', str('"' + new_song_final[2] + '"'))
        format_request = format_request.replace('time_s', str('"' + new_song_final[3] + '"'))
        format_request = format_request.replace('file_pyt', str('"' + new_song_final[4] + '"'))
        format_request = format_request.replace('f_format', str('"' + new_song_final[5] + '"'))
        hot_key = WorkToHotKey(key)
        hot_key.add_hot_key_in_ram(file_name, format_file)
        with open('./mainWindows/date/busy_hot_key.txt', 'a', newline='', encoding="utf8") as f:
            print(key.upper(), file=f)
        con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        cur.execute(f'''{format_request}''').fetchall()
        con.commit()
        con.close()


class WorkToHotKey: #Государственный орган по отслеживанию деятельности горячих клавиш
    def __init__(self, hot_key):
        self.hot_key = hot_key

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


class Interface(QMainWindow): #Интерфейс
    def __init__(self):
        super().__init__()
        if not os.path.isfile("./mainWindows/date/profile_info.sqlite") or not os.path.isfile(
                './mainWindows/date/settings_app.txt') or not os.path.isfile('./mainWindows/date/busy_hot_key.txt'):
            self.start_program_create_files()
        uic.loadUi("./mainWindows/Interface/New_base.ui", self)
        self.setWindowTitle('SPanel 0.2(Alpha)')
        with open('./mainWindows/date/settings_profile.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            text = read_l[1]
            t = text.split('-')
            a = t[1][:t[1].find("\n")]
            b = t[0]
            self.profile_now = a
            self.profile_now_table = b
        self.btn_profile = dict()
        self.btn_group_profile = list()
        self.add_button.clicked.connect(self.add_sound)
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        self.names_sound = []
        if darkdetect.isDark():
            self.volume_up_icon = QPixmap('./mainWindows/Interface/image/volume_up_icon_white.png')
            # self.close_right_icon = QIcon('./mainWindows/Interface/image/right_icon_white.png')
            self.stop_icon = QPixmap('./mainWindows/Interface/image/stop_icon_white.png')
        else:
            self.volume_up_icon = QPixmap('./mainWindows/Interface/image/volume_up_icon_dark.png')
            # self.close_right_icon = QIcon('./mainWindows/Interface/image/right_icon_dark.png')
            self.stop_icon = QPixmap('./mainWindows/Interface/image/stop_icon_dark.png')
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
        volume_value = self.valuts_volums_verticalSlider.value()
        self.valuts_volums_verticalSlider.valueChanged.connect(self.update_volume_value)
        self.update_sound_table()
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        self.help_pushButton.clicked.connect(self.help)
        self.update_profile_tabel()
        global stop_valve
        stop_valve = 0
        global stream_active_now
        stream_active_now = False
        kb.add_hotkey('ctrl + f', lambda: WorkToHotKey('ctrl + f').stop_valve_sound())
        MicrofonOutput('micro')



    def start_program_create_files(self):
        subprocess.run(['./pyt/Scripts/python.exe', './Initial_Setup_Windows/Initial_setup_main.py'])

    def settings_profile(self):
        et = SettingsProfile()
        et.show()
        et.exec()
        self.update_profile_tabel()

    def start_program(self):
        with open('./mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            volume_value = int(read_l[1][:-1])
            self.valuts_volums_verticalSlider.setValue(volume_value)
        self.update_hot_key()

    def update_hot_key(self):
        con = sqlite3.connect("mainWindows/date/profile_info.sqlite")
        cur = con.cursor()
        result = cur.execute(f'''SELECT * FROM {self.profile_now_table}''').fetchall()
        con.close()
        for item in result:
            hot_key = WorkToHotKey(item[1])
            hot_key.add_hot_key_in_ram(item[2], item[5])

    def add_sound(self):
        try:
            file_name = QFileDialog.getOpenFileName(self, 'Выберите звук для добавления', '', 'Wave file (*.wav)')[0]
            if file_name == '':
                raise FileAddError('')
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
        volume_value = self.valuts_volums_verticalSlider.value()

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
                    i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 420)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 0)
        self.tableWidget.setColumnWidth(5, 0)

    def click_button(self):
        self.profile_now = self.sender().text()
        self.profile_now_table = self.btn_profile[self.profile_now]
        kb.unhook_all_hotkeys()
        self.update_hot_key()
        self.update_profile_tabel()
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
        new_sound_file = WorkToSoundFile(file_name)
        new_sound_file.add_file_in_bd(name_sound=self.name_sound_lineEdit.text(),table_profile=self.table_info[self.profile_selection_comboBox.currentText()])
        self.close()

    def stop(self):
        self.close()

    def record_hot_key(self):
        et = RecordHotKeyDialogWindow(self.file_name)
        et.show()
        et.exec()
        self.hot_key_lineEdit.setText(str(key).upper())

    def other_file(self):
        try:
            file_name = QFileDialog.getOpenFileName(self, 'Выберите звук для добавления', '', 'Wave file (*.wav)')[0]
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
        self.hot_key_view.setText(f'{str(self.key).upper()}')
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
        # audio_data = np.frombuffer(in_data, dtype=np.int16)
        # audio_data = (audio_data * 0.1).astype(np.int16)
        return (in_data, pyaudio.paContinue)

    def start_microphon(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        input=True,
                        output=True,
                        stream_callback=self.callback_input, input_device_index=index_input(), output_device_index=index_out_system())
        self.stream_n = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        input=True,
                        output=True,
                        stream_callback=self.callback_input, input_device_index=index_inp_system(), output_device_index=index_output())

    def stop(self):
        self.stream_n.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./mainWindows/Interface/image/icon.png'))
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
