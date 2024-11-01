import pyaudio
import wave
import pygame
import tkinter as tk
import threading

filename = "recorded_audio.wav"
duration = 5
source_index = 4
thread_is_active = False

def change_source(arg1):
    global source_index

    new_index = arg1.split("-")[0]
    source_index = int(new_index.strip())

def create_ui():
    root = tk.Tk()
    root.title("Audio Streamer")

    device_list = list_audio_devices()
    device_names = [device[0] for device in device_list]

    device_var = tk.StringVar(root)
    device_var.set(device_names[0])

    device_dropdown = tk.OptionMenu(root, device_var, *device_names, command=change_source)
    device_dropdown.pack()

    record_button = tk.Button(root, command=record_audio, text="Record")
    record_button.pack()

    play_button = tk.Button(root, command=play_audio, text="Play")
    play_button.pack()

    global status_label
    status_label = tk.Label(root, text="Idling")
    status_label.pack()

    volume_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    volume_slider.pack()
    volume_slider.set(100.0)
    volume_slider.config(command=set_volume)

    root.mainloop()

def print_audio_devices():
    
    port_audio = pyaudio.PyAudio()

    for i in range(0, port_audio.get_device_count()):
        info = port_audio.get_device_info_by_index(i)
        print(f"Device index: {i}")
        print(f"Device name: {info['name']}")
        print(f"Sample rate: {info['defaultSampleRate']} Hz")
        print(f"Channels: {info['maxInputChannels']}")

def list_audio_devices():
    global device_info_list

    port_audio = pyaudio.PyAudio()
    device_info_list = []
    info = []

    for i in range(port_audio.get_device_count()):
        device_info = port_audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            device_info_list.append(device_info)
            full_name = device_info['name']
            full_name = (str(i) + " - " + full_name)
            info.append((full_name, i))

    port_audio.terminate()
    return info

def record_audio():
    global thread_is_active

    if(not thread_is_active):
        action_thread = threading.Thread(target=record_audio_thread)
        Thread_is_active = True
        action_thread.start()

def record_audio_thread():
    global filename
    global duration
    global thread_is_active
    global device_info_list

    status_label.config(text="Recording")

    active_device_info = device_info_list[source_index]

    FORMAT = pyaudio.paInt16
    CHANNELS = int(active_device_info['maxInputChannels'])
    RATE = int(active_device_info['defaultSampleRate'])
    CHUNK = 1024

    port_audio = pyaudio.PyAudio()

    stream = port_audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index = source_index,
        frames_per_buffer = CHUNK)

    # try:
    #     stream = port_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index = source_index, frames_per_buffer = CHUNK)
    #     stream_is_open = True
    #     print("Stream has started!")
    # except:
    #     print("An exception has occurred with source!")
    #     port_audio.terminate()
    #     status_label.config(text="Idling")
    #     thread_is_active = False

    print("It's working!")

    frames = []

    for i in range(int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
        print(f"Recording {i}")

    stream.stop_stream()
    stream.close()
    port_audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(port_audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    wf.writeframes(b''.join(frames))
    wf.close()
    
    status_label.config(text="Idling")
    thread_is_active = False
        
        

def play_audio():
    global thread_is_active

    if(not thread_is_active):
        action_thread = threading.Thread(target=play_audio_thread)
        thread_is_active = True
        action_thread.start()


def play_audio_thread():
    global filename
    global thread_is_active
    
    status_label.config(text="Playing")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    status_label.config(text="Idling")
    thread_is_active = False

def set_volume(value):
    pygame.mixer.music.set_volume(float(value))

if __name__ == "__main__":
    create_ui()
    # print_audio_devices()
    # record_audio(filename, duration=5)
    # play_audio(filename)