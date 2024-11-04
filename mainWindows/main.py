# -*- coding: utf-8 -*-
import sys
import argparse
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


from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog
from PyQt6.QtWidgets import QPushButton, QLabel


class AddSoundError(Exception):
    pass


class FileAddError(AddSoundError):
    pass


class WorkToSoundFile:
    def __init__(self, file_name):
        self.file_name = file_name

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
        t = WorkToOutputSoundInMicrophone(file_name)
        t.run()

        new_song_final = [last_id + 1, str(key).upper(), name_sound, f'{int(len_sound_file // 60)}:{int(len_sound_file % 60)}', file_name]
        with open('./date/songs_info.csv', 'a', newline='', encoding="utf8") as f:
            writer = csv.writer(
                f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(new_song_final)

class Interface(QMainWindow): #Интерфейс
    def __init__(self):
        super().__init__()
        uic.loadUi("./Interface/New_base.ui", self)
        self.add_button.clicked.connect(self.add_sound)
        self.names_sound = []
        if not os.path.isfile("./date/songs_info.csv"):
            self.start_program()
        self.update_sound_table('./date/songs_info.csv')


    def start_program(self):
        create_songs_file = open('./date/songs_info.csv', 'w', newline='', encoding="utf8")
        print('id;keyboards_key;song_name;run_song', file=create_songs_file)
        create_songs_file.close()

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
        self.ok_pushButton.clicked.connect(self.ok)

    def run(self):
        self.record_pushButton.hide()
        self.record_pushButton.setEnabled(False)
        self.key = kb.read_hotkey(suppress = False)
        self.hot_key_view.setText(f'{str(self.key).upper()}')
        self.reset_pushButton.setEnabled(True)

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

    def __init__(self, file_name):
        self.file_name = file_name

    def run(self):
        data, samplerate = sf.read(self.file_name)
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
        if len(self.file_name) < 2:
            print(f'Plays a wave file. Usage: {self.file_name} filename.wav')
            sys.exit(-1)

        with wave.open(self.file_name, 'rb') as wf:
            # Define callback for playback (1)
            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                # If len(data) is less than requested frame_count, PyAudio automatically
                # assumes the stream is finished, and the stream stops.
                return (data, pyaudio.paContinue)

            # Instantiate PyAudio and initialize PortAudio system resources (2)
            p = pyaudio.PyAudio()

            # Open stream using callback (3)
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            stream_callback=callback, output_device_index=42)
            print(sd.query_devices())
            # Wait for stream to finish (4)
            while stream.is_active():
                pass

            # Close the stream (5)
            stream.close()

            # Release PortAudio system resources (6)
            p.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
