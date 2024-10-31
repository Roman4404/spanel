import sys
import io
import os
import csv
from traceback import print_tb

from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt6.QtWidgets import QPushButton, QLabel

class AddSoundError(Exception):
    pass


class FileAddError(AddSoundError):
    pass


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
            elif file_name[-4:] != '.png':
                raise FileAddError('Выбран не подерживающися формат')
            songs_file = open('./date/songs_info.csv', 'r', newline='', encoding="utf8")
            read_song = csv.DictReader(songs_file, delimiter=';', quotechar='"')
            read_song_sort = sorted(read_song, key=lambda x: int(x['id']), reverse=False)
            if len(read_song_sort) == 0:
                last_id = 0
            else:
                last_id = int(read_song_sort[-1]['id'])
            songs_file.close()
            new_song_final = [last_id + 1, 'ALT+F4', file_name[file_name.rfind('/') + 1:], 'error']
            with open('./date/songs_info.csv', 'a', newline='', encoding="utf8") as f:
                writer = csv.writer(
                    f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(new_song_final)
            self.update_sound_table('./date/songs_info.csv')
        except AddSoundError as s:
            print(s)

    def update_sound_table(self, table_name):
        with open(table_name, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setColumnWidth(0, 50)
            self.tableWidget.setColumnWidth(1, 90)
            self.tableWidget.setColumnWidth(2, 2500)
            self.tableWidget.setColumnWidth(3, 90)
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Interface()
    ex.show()
    sys.exit(app.exec())
