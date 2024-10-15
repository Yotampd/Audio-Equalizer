import numpy as np
import scipy 
import pyaudio
import wave
import tkinter as tk
from threading import Thread


class Recorder:
    def __init__(self): #creating an audio file with all of these defult settings
        self.recording = False #audio recording active or not
        self.frames = []
        self.frames_per_buffer = 1024
        self.sample_rate = 44100 #44.1 Khz
        self.audio_format = pyaudio.paInt16 # every audio sample represented as 2 bytes
        self.channels = 1 #mono
        self.p = pyaudio.PyAudio() #audio object
        self.stream = None #opens a connection to audio I\O


    def start_recording(self):
        self.recording = True
        self.frames = [] #deleting previous data
        self.stream = self.p.open(format=self.audio_format,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.frames_per_buffer)
        
        print("Recording")


        while self.recording == True:
            data = self.stream.read(self.frames_per_buffer)
            self.frames.append(data)


    def stop_recording(self):
        self.recording = False
        self.stream.stop_stream() #stops processing data
        self.stream.close() #close audio stream
        self.p.terminate() #stopping all active audio streams and releasing all resources related to pyaudio - clean up everything
        print("Recording stopped")
        self.save_to_file("Out.wav")

    def save_to_file(self, fl_path):
        with wave.open(fl_path, "wb") as wf:  #wb = write binary
            wf.setnchannels(self.channels) #mono
            wf.setsampwidth(self.p.get_sample_size(self.audio_format)) #number of bytes for each sample
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames)) #writing the new data
        print(f"Audio save to {fl_path}")



class App:
    def __init__(self, root):
        self.recorder = Recorder()
        self.recording_thread = None
        self.rec_button = tk.Button(root, text="Start Recording" , command=self.toggle_recording)
        self.rec_button.pack(pady=20)
        self.root.protocol("WM_DELETE_WINDOW", self.closing)


    def toggle_recording(self):
        if not self.recorder.recording:
            self.rec_button.config(text="Stop Recording")
            self.recording_thread = Thread(target=self.recorder.start_recording)
            self.recording_thread.start()
        else:
            self.rec_button.config(text="Start Recording")
            self.recorder.stop_recording()
            if self.recording_thread:
                self.recording_thread.join()


    def closing(self):
        if self.recorder.recording:
            self.recorder.stop_recording()
            if self.rec_thread:
                self.rec_thread.join()
        self.root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio Recorder")
    app = App(root)
    root.mainloop()



        
    

