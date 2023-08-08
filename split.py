from scipy.io import wavfile
import noisereduce as nr

import scipy.io.wavfile
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, lfilter, butter, filtfilt

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return np.array(y,dtype=int)
def create_fir_filter(num_taps, cutoff, fs):
    nyquist = 0.5 * fs
    normalized_cutoff = cutoff / nyquist
    taps = firwin(num_taps, normalized_cutoff, window='hamming')
    return taps

def fir_filter(data, num_taps, cutoff, fs):
    filter_taps = create_fir_filter(num_taps, cutoff, fs)

    # Áp dụng bộ lọc FIR
    filtered_data = lfilter(filter_taps, 1.0, data)
    return np.array(filtered_data,dtype=np.int16)

# read ECG data from the WAV file
sampleRate, data = scipy.io.wavfile.read('audio_heart.wav')

times = np.arange(len(data)) / sampleRate
signal = data
# apply a 3-pole lowpass filter at 0.1x Nyquist frequency
# signal = nr.reduce_noise(y=data, sr=sampleRate)*5
for i in range(len(signal)):
   if signal[i] > 8000 :
       signal[i] = 8000
   if signal[i] < -8000 :
       signal[i] = -8000
# signal = nr.reduce_noise(y=signal, sr=sampleRate)*10
signal = fir_filter(signal,101,30,16000)*5
# signal1 = np.zeros(len(signal), dtype=int)
# for i in range(len(signal)):
#     signal1[i]= int(signal[i])
# signal = signal.astype(dtype=np.int32)
# signal = butter_bandpass_filter(data, 1, 380, 16000, order=2)
scipy.io.wavfile.write('audio_heart_out5.wav',sampleRate, signal)
plt.figure(figsize=(10, 4))

plt.subplot(2, 1, 1)
plt.plot(times, data, label='Tín hiệu đầu vào')
plt.plot(times, signal, label='Tín hiệu đầu ra')
plt.xlabel('Thời gian (s)')
plt.ylabel('Amplitude')
plt.title('Tín hiệu audio đầu vào và đầu ra sau bộ lọc FIR bandpass')
plt.legend()
plt.margins(0, .05)

# Vẽ phổ tần số của tín hiệu audio đầu vào và đầu ra cùng một lúc
plt.subplot(2, 2, 3)
spectrum = np.fft.fft(data)
freqs = np.fft.fftfreq(len(spectrum), d=1.0 / 16000)
magnitude = np.abs(spectrum)
plt.plot(freqs, magnitude, color='blue')
plt.title('Phổ tần số đầu vào')

plt.subplot(2, 2, 4)
spectrum = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(spectrum), d=1.0 / 16000)
magnitude = np.abs(spectrum)
plt.plot(freqs, magnitude, color='blue')
plt.title('Phổ tần số đầu ra')

plt.tight_layout()
plt.show()
