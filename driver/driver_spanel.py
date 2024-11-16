import sys
import io
import os
import sounddevice as sd
import pyaudio
from time import sleep
from datetime import datetime
import subprocess
from multiprocessing import Pool

def foo(t):
    sleep(5)
    print(f"Я спал {t}")



if __name__ == "__main__":
    subprocess.run(["python", "chrome.exe"])
    start = datetime.now()
    with Pool(5) as pool:
        pool.map(foo, range(5))
    print(datetime.now() - start)
