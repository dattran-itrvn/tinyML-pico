import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import signal
import librosa
from scipy.signal import firwin, lfilter, butter, filtfilt, freqz, find_peaks
from Filter import *

def create_fir_filter_bandpass(num_taps, cutoff, fs, pass_zero=True):
    nyquist = 0.5 * fs
    normalized_cutoff_f1 = cutoff[0] / nyquist
    normalized_cutoff_f2 = cutoff[1] / nyquist

    taps = firwin(num_taps, [normalized_cutoff_f1, normalized_cutoff_f2], pass_zero=pass_zero, window='blackman')
    return taps


def fir_filter_bandpass(data, num_taps, cutoff, fs, pass_zero=True):
    filter_taps = create_fir_filter_bandpass(num_taps, cutoff, fs, pass_zero)
    if (pass_zero == False):
        for i in range(len(filter_taps)):
            if filter_taps[i] > 1:
                filter_taps[i] *= 5
    # Áp dụng bộ lọc FIR
    filtered_data = lfilter(filter_taps, 1.0, data)
    return np.array(filtered_data)


AUDIO_FILE = 'C:/Users/AI-DEV/Downloads/Audio_14_08_2023/origin/audio1.wav'
samples, sample_rate = librosa.load(AUDIO_FILE, sr=None)
bwr = baseline_wander_remove_each_file(samples, sample_rate, 0.1, 0.5)
sig_pow = np.power(bwr, 2)
bbp = butter_bandpass_filter(sig_pow, 10, 25, 16000, order=3)
# fs = 1000  # Tần số lấy mẫu
# t = np.arange(0, 10, 1/fs)  # Thời gian từ 0 đến 10 giây
# f = 50 # Tần số của tín hiệu
# f2= 20
# sample_rate = fs
# samples = np.sin(2 * np.pi * f * t)+ 2*np.sin(2 * np.pi * f2 * t)
# samples = fir_filter_bandpass(samples, 101, [80,110], 16000, pass_zero=False)
# clock2 = np.ones(len(bbp), dtype=np.int16)
# l = int(len(samples) / 4000)
# diff = np.zeros(l)
# i = 0
# j = 0
# while (i < l * 4000):
#     s = np.abs(np.diff(bbp[i:i + 4000]))
#     diff[j] = s.sum()
#     if diff[j] > 0.0045:
#         clock2[i:i + 4000] = 0
#     i += 4000
#     j += 1
#
# bbp *= clock2
# samples/=10
sgram = librosa.stft(bbp)
# librosa.display.specshow(sgram)
sgram_mag, _ = librosa.magphase(sgram)
mel_scale_sgram = librosa.feature.melspectrogram(S=sgram_mag, sr=sample_rate)
librosa.display.specshow(mel_scale_sgram)
mel_sgram = librosa.amplitude_to_db(mel_scale_sgram, ref=np.min)

bound = 964758 / 1885
# mel_sgram[8][:]=100
st_step=0.3*16000*len(mel_sgram[0][:])/ len(samples)

test = mel_sgram[1][:]
index = np.where(test > 22.7)[0]
rec = []
i = 0
indexf = []
indexe = []
while (i < len(index) - 1):
    f = index[i]
    indexf.append(f)
    e = 1
    while (i < len(index) - 1 and index[i] == index[i + 1] - 1):
        e += 1
        i += 1
    indexe.append(e)
    # if fl:
    i += 1
    rec.append(Rectangle((f * bound / 16000, -0.001), e * bound / 16000, 0.002, fill=False, edgecolor='r'))
index_f = np.array(indexf)
index_e = np.array(indexe)
i =0
cnt = 1
index_ff =[]
while (i < len(index_f)-1):
    f = index_f[i]
    index_ff.append(f)
    while  (i < len(index_f)-1 and index_f[i+1]-index_f[i]<st_step):
        i+=1
    i+=1
    cnt+=1
if index_f[-1]-index_f[-2]>st_step:
    index_ff.append(index_f[-1])
    cnt += 1
print(cnt)
# for i in index:
#     rec.append(Rectangle((i * bound / 16000, -0.6), bound / 16000, 1.2, fill=False, edgecolor='r'))
y = np.ones(len(index_ff))
for i in range(len(y)):
    y[i]=0.002
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
times = np.arange(len(bbp)) / sample_rate
ax1.plot(times, bbp)
for rectangle in rec:
    ax1.add_patch(rectangle)
ax1.plot(np.array(index_ff) * bound/ sample_rate, y, '*', markersize=6, label='HR')
ax1.set_ylabel('Amplitude')
ax1.set_title('Tín hiệu âm thanh và Spectrogram')

librosa.display.specshow(mel_sgram, sr=sample_rate, x_axis='time', y_axis='mel')
# plt.colorbar(format='%+2.0f dB')
plt.tight_layout()
plt.show()
