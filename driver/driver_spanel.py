import pyaudio
import numpy as np

class VirtualMicrophone:
    def __init__(self, rate=44100, channels=1, frames_per_buffer=1024):
        self.rate = rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)
        self.stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        # Здесь можно обработать аудио данные
        return (audio_data.tobytes(), pyaudio.paContinue)

    def stop(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == '__main__':
    mic = VirtualMicrophone()
    try:
        mic.start()
        while True:
            pass
    except KeyboardInterrupt:
        mic.stop()