# -*- coding: utf-8 -*-
import sys
import io
import os
import csv
import shutil
import sounddevice as sd
import soundfile as sf
from tinytag import TinyTag
import keyboard as kb
import pyaudio
import numpy as np
import wave
import time
from PyQt6.QtCore import Qt


from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog
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
        shutil.copy2(f'{self.file_name}', f'./date/sound_vaults/{name_f}')
        return f'./date/sound_vaults/{name_f}'

    def add_file_in_bd(self, name_sound):
        file_name = self.file_name
        songs_file = open('./date/songs_info.csv', 'r', newline='', encoding="utf8")
        read_song = csv.DictReader(songs_file, delimiter=';', quotechar='"')
        read_song_sort = sorted(read_song, key=lambda x: int(x['id']), reverse=False)
        if len(read_song_sort) == 0:
            last_id = 0
        else:
            last_id = int(read_song_sort[-1]['id'])
        songs_file.close()
        sound_file = TinyTag.get(file_name)
        len_sound_file = sound_file.duration
        format_file = file_name[-4:]
        new_song_final = [last_id + 1, str(key).upper(), name_sound, f'{int(len_sound_file // 60)}:{int(len_sound_file % 60)}', file_name, format_file]
        hot_key = WorkToHotKey(key)
        hot_key.add_hot_key_in_ram(file_name, format_file)
        with open('./date/busy_hot_key.txt', 'a', newline='', encoding="utf8") as f:
            print(key.upper(), file=f)
        with open('./date/songs_info.csv', 'a', newline='', encoding="utf8") as f:
            writer = csv.writer(
                f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(new_song_final)


class WorkToHotKey: #Государственный орган по отслеживанию деятельности горячих клавиш
    def __init__(self, hot_key):
        self.hot_key = hot_key

    def check_hot_key_busy_lite(self):
        with open('./date/busy_hot_key.txt', 'r', newline='', encoding="utf8") as f:
            read_file = f.readlines()
            for i in read_file:
                if str(self.hot_key).upper() == i[:-1]:
                    return True
            return False


    def add_hot_key_busy(self):
        pass

    def remove_old_hot_key_busy(self):
        pass

    def remove_hot_key_busy(self):
        pass

    def add_hot_key_in_ram(self, file_name, format_file):
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
        uic.loadUi("./Interface/New_base.ui", self)
        self.add_button.clicked.connect(self.add_sound)
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        self.names_sound = []
        self.volume_up_icon = QPixmap('./Interface/image/volume_up_icon_white.png')
        self.play_icon = QPixmap("./Interface/image/play_and_pause_icon_white.png")
        self.play_pushButton.setIcon(QIcon(self.play_icon))
        self.play_pushButton.setIconSize(self.play_icon.rect().size())
        self.stop_icon = QPixmap('./Interface/image/stop_icon_white.png')
        self.stop_pushButton.setIcon(QIcon(self.stop_icon))
        self.stop_pushButton.setIconSize(self.stop_icon.rect().size())
        self.volume_icon_label.setPixmap(self.volume_up_icon)
        if not os.path.isfile("./date/songs_info.csv") or not os.path.isfile('./date/settings_app.txt') or not os.path.isfile('./date/busy_hot_key.txt'):
            self.start_program_create_files()
        self.start_program('./date/songs_info.csv')
        global volume_value
        volume_value = self.valuts_volums_verticalSlider.value()
        self.valuts_volums_verticalSlider.valueChanged.connect(self.update_volume_value)
        self.update_sound_table('./date/songs_info.csv')
        self.stop_pushButton.clicked.connect(self.stop_valve_sound)
        global stop_valve
        stop_valve = 0
        kb.add_hotkey('ctrl + f', lambda: WorkToHotKey('ctrl + f').stop_valve_sound())



    def start_program_create_files(self):
        with open('./date/songs_info.csv', 'w', newline='', encoding="utf8") as create_songs_file:
            print('id;keyboards_key;song_name;run_song;file_name;format_file', file=create_songs_file)
            create_songs_file.close()
        with open('./date/settings_app.txt', 'w', newline='', encoding="utf8") as create_settings_file:
            print('volume_value', file=create_settings_file)
            print('99', file=create_settings_file)
        create_settings_file.close()
        with open('./date/busy_hot_key.txt', 'w', newline='', encoding="utf8") as f:
            pass
        self.valuts_volums_verticalSlider.setValue(99)


    def start_program(self, table_name):
        with open('./date/settings_app.txt', 'r', encoding="utf8") as f:
            read_l = f.readlines()
            volume_value = int(read_l[1][:-1])
            self.valuts_volums_verticalSlider.setValue(volume_value)
        with open(table_name, encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for song_info in list(reader):
                hot_key = WorkToHotKey(song_info['keyboards_key'])
                hot_key.add_hot_key_in_ram(song_info['file_name'], song_info['format_file'])


    def add_sound(self):
        try:
            file_name = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
            if file_name == '':
                raise FileAddError('')
            elif not TinyTag.is_supported(file_name):
                raise FileAddError('Выбран не подерживающися формат')
            et = FinalDialogWindowAddSound(file_name)
            et.show()
            et.exec()
            self.update_sound_table('./date/songs_info.csv')
        except AddSoundError as s:
            print(s)

    def update_volume_value(self):
        global volume_value
        volume_value = self.valuts_volums_verticalSlider.value()

    def stop_valve_sound(self):
        global res_volume_value
        global volume_value
        res_volume_value = self.valuts_volums_verticalSlider.value()
        volume_value = -1


    def update_sound_table(self, table_name):
        with open(table_name, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 540)
        self.tableWidget.setColumnWidth(3, 90)
        self.tableWidget.setColumnWidth(4, 0)
        self.tableWidget.setColumnWidth(5, 0)

    def closeEvent(self, event):
        with open('./date/settings_app.txt', 'w', newline='', encoding="utf8") as f:
            print('1', file=f)
            print(self.valuts_volums_verticalSlider.value(), file=f)
        event.accept()


class FinalDialogWindowAddSound(QDialog):

    def __init__(self, file_name):
        super().__init__()
        uic.loadUi("./Interface/final_add_sound.ui", self)
        self.file_name = file_name
        self.name_sound_lineEdit.setText(str(file_name[file_name.rfind('/') + 1:file_name.rfind('.')]))
        self.ok_pushButton.clicked.connect(self.run)
        self.file_select_other_pushButton.clicked.connect(self.other_file)
        self.cancel_pushButton.clicked.connect(self.stop)
        self.to_record_window_pushButton.clicked.connect(self.record_hot_key)
        global volume_value
        global key
        key = ''


    def run(self):
        new_sound_file = WorkToSoundFile(self.file_name)
        file_name = new_sound_file.copy_file()
        new_sound_file = WorkToSoundFile(file_name)
        new_sound_file.add_file_in_bd(name_sound=self.name_sound_lineEdit.text())
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
            file_name = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
            if file_name == '':
                raise FileAddError('')
            elif not TinyTag.is_supported(file_name):
                raise FileAddError('Выбран не подерживающися формат')
            self.file_name = file_name
            self.name_sound_lineEdit.setText(str(file_name))
        except AddSoundError as s:
            print(s)


class RecordHotKeyDialogWindow(QDialog):

    def __init__(self, file_name):
        super().__init__()
        uic.loadUi("./Interface/record_hot_key.ui", self)
        self.file_name = file_name
        self.cancel_pushButton.clicked.connect(self.stop)
        self.record_pushButton.clicked.connect(self.run)
        self.reset_pushButton.clicked.connect(self.other_hot_key)
        self.reset_pushButton.setEnabled(False)
        self.ok_pushButton.setEnabled(False)
        self.ok_pushButton.clicked.connect(self.ok)

    def run(self):
        self.record_pushButton.hide()
        self.record_pushButton.setEnabled(False)
        self.key = kb.read_hotkey(suppress = False)
        key_busy = WorkToHotKey(self.key)
        if key_busy.check_hot_key_busy_lite():
            self.hot_key_view.setText(f'Занята')
            self.ok_pushButton.setEnabled(False)

        else:
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


class WorkToOutputSoundInMicrophone:

    def __init__(self, file_name, format_file):
        self.file_name = file_name
        self.format_file = format_file

    def run(self):
        global volume_value
        global stop_valve
        global res_volume_value
        res_volume_value = volume_value
        # data, samplerate = sf.read(self.file_name)
        # format = pyaudio.paInt16
        # channels = 1
        # rate = 44100
        # chunk = 1024
        #
        # p = pyaudio.PyAudio()
        #
        # stream_input = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        # stream_output = p.open(format=format, channels=channels, rate=rate, output=True)
        #
        # try:
        #     while True:
        #         audio_data = np.frombuffer(data, dtype=np.int16)
        #         stream_output.write(data)
        #
        # except KeyboardInterrupt:
        #     pass
        #
        #
        # stream_input.stop_stream()
        # stream_input.close()
        # stream_output.stop_stream()
        # stream_output.close()
        # p.terminate()

        if self.format_file == '.wav':
            with wave.open(self.file_name, 'rb') as wf:

                def callback(in_data, frame_count, time_info, status):
                    data = wf.readframes(frame_count)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    self.volume_value = int(volume_value) / 100

                    if self.volume_value == float(-0.01):
                        stream.close()
                    audio_data = (audio_data * self.volume_value).astype(np.int16)

                    return (audio_data.tobytes(), pyaudio.paContinue)

                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True,
                                stream_callback=callback, output_device_index=50)


                print(sd.query_devices())
                try:
                    while stream.is_active():
                        pass
                except OSError:
                    pass

                stream.close()
                p.terminate()
                volume_value = res_volume_value

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
