import numpy as np
from scipy.signal import butter , lfilter 
import wave
import pyaudio
import matplotlib.pyplot as plt



def low_pass_filter(cutoff, sample_rate, order = 5):
    nyquist = 0.5*sample_rate  # minimum rate that needs to be sampled 
    normal_cutoff = cutoff / nyquist #normalize
    b , a = butter(order, normal_cutoff, btype = "low", analog = False)
    return b, a #the relevent coefficents 

def high_pass_filter(cutoff, sample_rate, order = 5):
    nyquist = 0.5*sample_rate  # minimum rate that needs to be sampled 
    normal_cutoff = cutoff / nyquist #normalize
    b , a = butter(order, normal_cutoff, btype = "high", analog = False)
    return b , a


def band_pass_filter(f_low , f_high , sample_rate , order = 5):
    nyquist = 0.5*sample_rate
    normal_lowcut = f_low / nyquist
    normal_highcut = f_high / nyquist
    b , a = butter(order , [normal_lowcut , normal_highcut], btype = "band" , analog = False)
    return b , a

def filter(inp ,b ,a):
    out = lfilter(b, a, inp)
    return out

def load_wav(filename):
    with wave.open(filename, 'rb') as wf:
        sample_rate = wf.getframerate()
        frames = wf.getnframes()
        audio_data = wf.readframes(frames)
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
    return audio_data, sample_rate


def save_wav(filename, audio_data, sample_rate):
    with wave.open(filename , "wb") as wf:
        wf.setnchannels(2) #stereo
        wf.setsampwidth(2) #2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.astype(np.int16).tobytes())


def plot_frequency_domain(data, sample_rate, title):
    # Perform DFT and calculate the magnitude spectrum
    dft = np.fft.fft(data)
    magnitude = np.abs(dft)
    frequency = np.fft.fftfreq(len(magnitude), 1/sample_rate)
    #print(dft)

    # Plotting only the positive frequencies
    plt.plot(frequency[:len(frequency)//2], magnitude[:len(magnitude)//2])
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.xlim(0,500)


def plot_time_domain(data , sample_rate, title):
    plt.plot(data)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.grid
    plt.xlim(0, min(16, len(data)/sample_rate))


def main():
    wav_filename = 'audio_test1.wav'
    output_filename = 'output_low_pass.wav'
    cutoff_frequency = 100
    f_low = 150
    f_high = 200

        
    audio_data, sample_rate = load_wav(wav_filename)



    time_vector = np.arange(len(audio_data)) / sample_rate


    print(time_vector[:10])


     # Plot original audio in frequency domain
    plt.figure(figsize=(12, 12))
    plt.subplot(3, 1, 1)
    plot_frequency_domain(audio_data, sample_rate, 'Original Audio in Frequency Domain')

    # Apply low-pass filter
    #b, a = low_pass_filter(cutoff_frequency, sample_rate)
    #filtered_data = filter(audio_data, b, a)

    # Apply high-pass filter
    #b, a = high_pass_filter(cutoff_frequency, sample_rate)
    #filtered_data = filter(audio_data, b, a)
    
    # Apply band-pass filter
    b, a = band_pass_filter(f_low, f_high, sample_rate)
    filtered_data = filter(audio_data, b, a)




    plt.subplot(3, 1, 2) #number of rows, columns, index
    plot_frequency_domain(filtered_data, sample_rate, 'Filtered Audio in Frequency Domain')

    plt.subplot(3, 1, 3)
    plot_time_domain(time_vector, sample_rate, "Unfilterd Audio in TIme Domain")
    
    
    # Display the plots
    plt.tight_layout()
    plt.show()



    # Save the filtered audio
    save_wav(output_filename, filtered_data, sample_rate)

    
if __name__ == "__main__":
    main()