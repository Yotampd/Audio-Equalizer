from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from scipy.signal import butter , filtfilt , lfilter
import wave
import pyaudio
import threading
import os
from pydub import AudioSegment  


### cutoff frequancy bands ###
bass_cutoff = 200 
mid_low_cutoff = 1000
mid_high_cutoff = 3000 
treble_cutoff = 3000 #continuty 
RATE = 44100

app = Flask(__name__)

saved_audio_arr = np.array([], dtype=np.int16) #sound as array
recording_thread = None
button = True #Flag for while loop
playback_button = False #Flag for playback loop

@app.route('/')
@app.route('/home')
def home():
    return render_template('homepage.html') 

@app.route('/process', methods=['POST']) #the page when a user sends a request
def process_audio():
    global button, saved_audio_arr, playback_button
    
    #reterive gain values from the form, default is 1 - how much will the filter effect
    bass_gain = float(request.form.get('bass_gain', 1.0))
    mid_low_gain = float(request.form.get('mid_low_gain', 1.0))
    mid_high_gain = float(request.form.get('mid_high_gain', 1.0))
    treble_gain = float(request.form.get('treble_gain', 1.0))
    action = request.form.get('action')
    print(bass_cutoff, treble_cutoff, mid_low_cutoff, mid_high_cutoff)

    if action == "upload_file":
        if "file" not in request.files:
            return render_template("homepage,html", error= "No file uploaded")
        
        file = request.files["file"] #requast.files is a dict storing uploaded files, "file" is the key
        output_filename = handle_file_upload(file)

        with wave.open(output_filename, "rb") as wf:
            saved_audio_arr = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        
        delete_file("filtered_data.wav")
        return redirect(url_for("home"))
    if action == 'record':
        bass_gain = 1.0 #resetting the sliders for a new recording
        mid_low_gain = 1.0
        mid_high_gain = 1.0
        treble_gain = 1.0
        delete_file("filtered_data.wav")
        start_recording()
    elif action == 'stop_recording':
        stop_recording()
    elif action == 'playback':
        playback_button = True #new thread
        playback_thread = threading.Thread(target=start_playback)
        playback_thread.start()
    elif action == 'apply_filters':
        apply_filters(bass_gain, mid_low_gain, mid_high_gain, treble_gain)    
        

    return redirect(url_for('home', bass_gain=bass_gain, mid_low_gain=mid_low_gain, mid_high_gain=mid_high_gain, treble_gain=treble_gain))
    
    

@app.route('/stop_playback', methods=['POST'])
def stop_playback():
    global playback_button
    playback_button = False  # Set flag to stop playback
    return redirect(url_for('home'))


##### Functions and Filters ####

def save_wav(audiodata, filename, RATE = 44100):
    with wave.open(filename , "wb") as wf: #write binary mode
        wf.setnchannels(1) #mono
        wf.setsampwidth(2) #2 bytes per sample
        wf.setframerate(RATE)
        wf.writeframes(audiodata.astype(np.int16).tobytes()) #array to bytes to a file

def recording_input(FRAMES_PER_BUFFER = 1024, FORMAT = pyaudio.paInt16, CHANNELS = 1, RATE = 44100):
    global button
    global recording_thread
    global saved_audio_arr
    p = pyaudio.PyAudio() #acquire system resources for PortAudio
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=FRAMES_PER_BUFFER)
    
    print("Recording in progress")

    for _ in range(5):  # to avoid delay
        stream.read(FRAMES_PER_BUFFER)


    frames = [] #array for the frames

    while button is True: #recording
        data = stream.read(FRAMES_PER_BUFFER)
        frames.append(data)

    saved_audio_arr = np.frombuffer(b''.join(frames), dtype=np.int16) #combining chunks into a single byte string - unfilttered audio data
    save_wav(np.array(saved_audio_arr), "Recording.wav", RATE) #saved audio as a wav file

    print("Finished!") #meaning stop button was pressed

    stream.stop_stream()   #finishing the usage of the function
    stream.close()
    p.terminate() #releasing system resources



def playing_back(filename):
    global playback_button
    CHUNK = 1024
    p = pyaudio.PyAudio()
    with wave.open(filename, "rb") as wf:
        #open streaming
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        print("Playing")
        data = wf.readframes(CHUNK)
        while data and playback_button:  # while data is not empty and playback button is false
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.close()
        p.terminate()


def start_recording():
    global recording_thread
    global button

    button = True  # start recording
    recording_thread = threading.Thread(target=recording_input)  # recording in a separate thread
    recording_thread.start()


def stop_recording():
    global button

    button = False  
    if recording_thread:
        recording_thread.join()  # ensure thread finishes before moving on

def start_playback():
    global playback_button
    try:
        playing_back("filtered_data.wav")
        print("playing filtered")
    except FileNotFoundError:
        try:
            playing_back("Recording.wav")
            print("playing original")
        except FileNotFoundError:
            print("no recording")


def apply_filters(bass_gain, mid_low_gain, mid_high_gain, treble_gain):
    editable_saved_audio = saved_audio_arr.copy()
        
        
     # array to store the accumulate the audio
    filtered_data = np.zeros_like(saved_audio_arr, dtype=np.float64) #using 32 for precision and preventing overflow(too many bits)

    #LPF
    bass_filtered = low_pass_filter(cutoff=bass_cutoff, gain = bass_gain, data=editable_saved_audio)
    filtered_data += bass_filtered

    #BPF
    mid_low_filtered = band_pass_filter(f_low=bass_cutoff, f_high=mid_low_cutoff,  gain = mid_low_gain, data=editable_saved_audio)
    filtered_data += mid_low_filtered


    mid_high_filtered = band_pass_filter(f_low=mid_low_cutoff, f_high=mid_high_cutoff, gain = mid_high_gain, data=editable_saved_audio)
    filtered_data += mid_high_filtered

    #HPF
    treble_filtered = high_pass_filter(cutoff=treble_cutoff, gain= treble_gain, data=editable_saved_audio)
    filtered_data += treble_filtered

    filtered_data = apply_normalization(filtered_data)
    
    ### convert to int16
    filtered_data = np.clip(filtered_data , -32768 , 32767)  
    filtered_data = filtered_data.astype(np.int16)
    if check(filtered_data, saved_audio_arr):
        print("true")
    else:
        print("false")
    save_wav(filtered_data , "filtered_data.wav")

    print("Max amplitude before filtering:", np.max(np.abs(saved_audio_arr)))
    print("Max amplitude after filtering:", np.max(np.abs(filtered_data)))
    print(saved_audio_arr)
    print(filtered_data)
    



def low_pass_filter(cutoff, gain,  data, RATE = 44100, order = 5): #order represents the power of a pole what will be the slope value at the pole value. order 1 -> -20db for decade
    nyquist = 0.5*RATE #highest freq we can sample with no errors 
    normal_cutoff = cutoff/nyquist
    b , a = butter(order, normal_cutoff, btype="low", analog=False) #Wn = normal_cutoff - knee frequancy, b and a are the filter coefficents
    filtered_data = filtfilt(b, a, data)
    #apply gain
    filtered_data = filtered_data * gain
    return filtered_data



def high_pass_filter(cutoff, gain,  data, RATE = 44100, order = 5): #order represents the power of a pole what will be the slope value at the pole value. order 1 -> -20db for decade
    nyquist = 0.5*RATE #highest freq we can sample with no errors 
    normal_cutoff = cutoff/nyquist
    b , a = butter(order, normal_cutoff, btype="high", analog=False) #Wn = normal_cutoff - knee frequancy, b and a are the filter coefficents
    filtered_data = filtfilt(b, a, data) #giving only desired frequancy components 
    #apply gain
    filtered_data = filtered_data * gain #y[n] = K*(h[n]*x[n])
    return filtered_data


def band_pass_filter(f_low, f_high, gain, data, RATE = 44100, order = 5):
    nyquist = 0.5*RATE
    normal_lowcut = f_low / nyquist
    normal_highcut = f_high / nyquist
    b , a = butter(order,[normal_lowcut, normal_highcut], btype="band", analog=False )
    filtered_data = filtfilt(b, a, data)
    #apply gain
    filtered_data = filtered_data * gain
    return filtered_data

def apply_normalization(audio_data):
    max_value = np.max(np.abs(audio_data))
    if max_value > 12000:  # Set a threshold to avoid normalizing very low amplitude signals
        return (audio_data / max_value) * 32767  
    else:
        return audio_data 

def check(arr1, arr2):
    difference = np.abs(arr1 - arr2)
    max_diff = np.max(difference)
    print(f"Max difference between arrays: {max_diff}")
    return max_diff > 0  # True if there is any difference

def delete_file(filename):
    try:
        os.remove(filename)
    except: FileNotFoundError   
    return

def handle_file_upload(file):
    file_ext = os.path.splitext(file.filename)[1].lower() #getting the file type

    temp = "temp_audio" + file_ext
    file.save(temp)

    if file_ext != ".wav":
        audio = AudioSegment.from_file(temp)
        audio.export("Recording.wav", format = "wav") #converting 
        os.remove(temp)
    else:
        if os.path.exists("Recording.wav"):
            os.remove("Recording.wav")  
        os.rename(temp, "Recording.wav")
    
    return "Recording.wav"

if __name__ == '__main__':
    app.run(debug=True)


