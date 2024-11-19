
import pyaudio
import sounddevice as sd

def index_input():
    with open('../mainWindows/date/settings_app.txt', 'r', encoding="utf8") as f:
        read_l = f.readlines()
        str_inp = read_l[0][2:-1]
        index_inp = 2
        devices = list(sd.query_devices())
        for device in devices:
            if device['name'] == str_inp:
                index_inp = device['index']
                print(index_inp)
                break
    return index_inp

def index_output():
    devices = list(sd.query_devices())
    for device in devices[::-1]:
        if device['name'] == 'Output (VB-Audio Point)':
            print(device['max_output_channels'])
            if device['max_output_channels'] == 16:
                print(device['index'])
                return device['index']

def index_out_system():
    index_inp = 5
    devices = list(sd.query_devices())
    for device in devices:
        if device['name'] == 'CABLE Input (VB-Audio Virtual C':
            index_inp = device['index']
            print(index_inp)
            break
    return index_inp

def index_inp_system():
    index_inp = 2
    devices = list(sd.query_devices())
    for device in devices:
        if device['name'] == 'Input (VB-Audio Point)':
            index_inp = device['index']
            print(index_inp)
            break
    return index_inp

def callback_input( in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

def start_microphon():
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    input=True,
                    output=True,
                    stream_callback=callback_input, input_device_index=index_input(), output_device_index=index_out_system())
    stream_n = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    input=True,
                    output=True,
                    stream_callback=callback_input, input_device_index=index_inp_system(), output_device_index=index_output())

    while stream.is_active():
        pass

def stop(self):
    pass

if __name__ == '__main__':
    start_microphon()