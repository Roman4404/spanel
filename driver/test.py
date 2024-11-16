import sys
import io
import os
import sounddevice as sd
import pyaudio
import time
from datetime import datetime
import subprocess
from multiprocessing import Pool


def index_input():
    with open('../mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
        read_l = f.readlines()
        str_inp = read_l[0][3:-1]
        index_inp = 2
        devices = list(sd.query_devices())
        for device in devices[::-1]:
            if device['hostapi'] != 3:
                break
            elif device['name'] == str_inp:
                index_inp = device['index']
                print(index_inp)
    return index_inp

def index_output():
    devices = list(sd.query_devices())
    for device in devices[::-1]:
        if device['name'] == 'Output (VB-Audio Point)':
            print(device['max_output_channels'])
            if device['max_output_channels'] == 16:
                print(device['index'])
                return device['index']

def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                input=True,
                output=True,
                stream_callback=callback, input_device_index=index_input(), output_device_index=int(index_output()))


while stream.is_active():
    pass

stream.close()
p.terminate()
