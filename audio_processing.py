import numpy as np
from scipy.signal import butter , filtfilt 
import wave
import pyaudio
import matplotlib.pyplot as plt
import threading

saved_audio_arr = [] #sound as array
recording_thread = None
button = True #Flag for while loop

def save_wav(audiodata, RATE = 44100, filename = "Recording.wav"):
    with wave.open(filename , "wb") as wf: #write binary mode
        wf.setnchannels(2) #stereo
        wf.setsampwidth(2) #2 bytes per sample
        wf.setframerate(RATE)
        wf.writeframes(audiodata.astype(np.int16).tobytes()) #array to bytes to a file



def recording_input(button, FRAMES_PER_BUFFER = 1024, FORMAT = pyaudio.paInt16, CHANNELS = 1, RATE = 44100,):
    global recording_thread
    global saved_audio_arr
    p = pyaudio.PyAudio() #acquire system resources for PortAudio
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=FRAMES_PER_BUFFER)
    
    print("Recording in progress")

    frames = [] #array for the frames

    while button is True: #recording
        data = stream.read(FRAMES_PER_BUFFER)
        frames.append(data)

    saved_audio_arr = np.frombuffer(b''.join(frames), dtype=np.int16) #combining chunks into a single byte string
    save_wav(np.array(saved_audio_arr), RATE) #saved audio as a wav file

    print("Finished!") #meaning stop button was pressed

    stream.stop_stream()   #finishing the usage of the function
    stream.close()
    p.terminate() #releasing system resources



def playing_back(filename = "Recording.wav"):
    CHUNK = 1024
    p = pyaudio.PyAudio()
    with wave.open(filename, "rb") as wf:
        #open streaming
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        print("Playing")
        
        while len(data := wf.readframes(CHUNK)):  # Looping over fixed length blocks - CHUNK
            stream.write(data)

        stream.close()
        p.terminate()



def start_recording():
    global recording_thread
    global button

    button = True  # start recording
    recording_thread = threading.Thread(target=recording_input, args=(button,))  # recording in a separate thread
    recording_thread.start()

def stop_recording():
    global button

    button = False  
    if recording_thread:
        recording_thread.join()  # ensure thread finishes before moving on





def low_pass_filter(cutoff, data = saved_audio_arr, RATE = 44100, order = 5): #order represents the power of a pole what will be the slope value at the pole value. order 1 -> -20db for decade
    nyquist = 0.5*RATE #highest freq we can sample with no errors 
    normal_cutoff = cutoff/nyquist
    b , a = butter(order, normal_cutoff, btype="low", analog=False) #Wn = normal_cutoff - knee frequancy, b and a are the filter coefficents
    
    filtered_data = filtfilt(b, a, data)

    save_wav(filtered_data)



def high_pass_filter(cutoff, data = saved_audio_arr, RATE = 44100, order = 5): #order represents the power of a pole what will be the slope value at the pole value. order 1 -> -20db for decade
    nyquist = 0.5*RATE #highest freq we can sample with no errors 
    normal_cutoff = cutoff/nyquist
    b , a = butter(order, normal_cutoff, btype="high", analog=False) #Wn = normal_cutoff - knee frequancy, b and a are the filter coefficents
    
    filtered_data = filtfilt(b, a, data)

    save_wav(filtered_data)

    return 


    
def band_pass_filter(f_low, f_high, data = saved_audio_arr, RATE = 44100, order = 5):
    nyquist = 0.5*RATE
    normal_lowcut = f_low / nyquist
    normal_highcut = f_high / nyquist
    b , a = butter(order,[normal_lowcut, normal_highcut], btype="band", analog=False )
    
    filtered_data = filtfilt(b, a, data)

    save_wav(filtered_data)

    return
