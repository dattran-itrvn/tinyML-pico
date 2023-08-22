import wfdb
import numpy as np
import scipy.signal as spysig
import scipy.ndimage as spynd
from scipy.ndimage import maximum_filter1d
from scipy.signal import  butter, filtfilt
from define import *
import os
import matplotlib.pyplot as plt
np.seterr(divide='ignore')

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.
    output:
        the smoothed signal
    example:
    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    see also:
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    if x.ndim != 1:
        raise (ValueError, "smooth only accepts 1 dimension arrays.")
    if x.size < window_len:
        raise (ValueError, "Input vector needs to be bigger than window size.")
    if window_len < 3:
        return x
    if window_len % 2 == 0:
        window_len += 1
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise (ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')
    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[int(window_len / 2):-int(window_len / 2)]


def baseline_wander_remove(signal, fs=250, f1=0.2, f2=0.6):
    window1 = int(f1 * fs/2) + 1 if int(f1 * fs/2) % 2 == 0 else int(f1 * fs/2)
    window2 = int(f2 * fs/2) + 1 if int(f2 * fs/2) % 2 == 0 else int(f2 * fs/2)
    out1 = smooth(signal, window1)
    out2 = smooth(out1, window2)
    bwr_signal = signal - out2
    return bwr_signal


def normalize(raw, window_len, samp_from=-1, samp_to=-1):
    # The window size is the number of samples that corresponds to the time analogue of 2e = 0.5s
    if window_len % 2 == 0:
        window_len += 1
    abs_raw = abs(raw)
    # Remove outlier
    while True:
        g = maximum_filter1d(abs_raw, size=window_len)
        if np.max(abs_raw) < 5.0:
            break
        abs_raw[g > 5.0] = 0
    g_smooth = smooth(g, window_len, window='hamming')
    g_mean = max(np.mean(g_smooth) / 3.0, 0.1)
    g_smooth = np.clip(g_smooth, g_mean, None)
    # Avoid cases where the value is )
    g_smooth[g_smooth < 0.01] = 1
    nor_signal = np.divide(raw, g_smooth)
    return nor_signal



def preprocess_data(file_path, separate=None):
    # file_name = file_path.split('/')[-1][:-4]
    file_path = file_path[:-4]
    info = wfdb.rdheader(file_path)
    signal_length = info.sig_len
    if separate == 1:
        signal, _ = wfdb.rdsamp(file_path, channels=[0], sampfrom=0, sampto=signal_length//2)
        annotation = wfdb.rdann(file_path, 'atr', sampfrom=0, sampto=signal_length//2)
        signal_length = signal_length//2
    elif separate == 2:
        signal, _ = wfdb.rdsamp(file_path, channels=[0], sampfrom=signal_length//2, sampto=signal_length)
        annotation = wfdb.rdann(file_path, 'atr', sampfrom=signal_length//2, sampto=signal_length)
        annotation.sample = annotation.sample - (info.sig_len - info.sig_len // 2)
        signal_length = signal_length - signal_length // 2
    else:
        signal, _ = wfdb.rdsamp(file_path, channels=[0])
        annotation = wfdb.rdann(file_path, 'atr')

    signal.astype(DATA_TYPE)
    signal = np.squeeze(signal) #flatten all signal

    if info.fs != FREQUENCY_SAMPLING:
        signal_length = int(FREQUENCY_SAMPLING / info.fs * signal_length)
        signal = spysig.resample(signal, signal_length)
        annotation.sample = annotation.sample * FREQUENCY_SAMPLING / info.fs
        annotation.sample = annotation.sample.astype('int')

        # import matplotlib.pyplot as plt
        # plt.plot(np.linspace(1,100,signal[:annotation.sample[2]].shape[0]), signal[:annotation.sample[2]])
        # plt.plot(np.linspace(1,100,
        #          resample_signal[:int(annotation.sample[2] * FREQUENCY_SAMPLING / info['fs'])].shape[0]),
        #          resample_signal[:int(annotation.sample[2] * FREQUENCY_SAMPLING / info['fs'])])
        # plt.grid()
        # plt.show()
        # exit()
    signal.astype(DATA_TYPE)

    signal = butter_bandpass_filter(signal, 1, 30, 250, order=2)
    signal = baseline_wander_remove(signal, 250, 0.2, 0.6)
    signal = normalize(signal, int(0.5 * 250))

    input_scale = 0.003920781891793013
    input_zero_point = 0
    _signal = signal / input_scale + input_zero_point
    _signal = np.maximum(_signal, 0)
    _signal = _signal.astype(np.uint8)

    label = []
    for i in range(annotation.ann_len):
        if annotation.symbol[i] in ['+', '~', '|', '[', '!', ']', '"', 's', 'x']:
            continue
        if annotation.sample[i] >= int(len(signal) // (128*5))*(128*5):
            break
        t0 = annotation.sample[i] // 16
        t1 = annotation.sample[i] % 16
        if t1>=int(FREQUENCY_SAMPLING*0.04):
            if t1 >= (15 - int(FREQUENCY_SAMPLING*0.04)):
                label.append(t0)
                label.append(t0 + 1)
            else:
                label.append(t0)
        else:
            if t1<int(FREQUENCY_SAMPLING*0.04):
                label.append(t0 - 1)
                label.append(t0)

    # plt.plot(signal)
    # plt.grid(True)
    # plt.xlim(0, 1000)
    # plt.gcf().set_size_inches(20, 5)
    # plt.show()

    # Data and labelling
    # data_sample = []
    # for i in range(signal_length - (NEIGHBOUR_POINT - 1)):
    #     data_sample.append(signal[i:i + NEIGHBOUR_POINT])
    # data_sample = np.expand_dims(np.array(data_sample, dtype='float32'), axis=-1)
    #
    # label = np.zeros(signal_length, dtype='int8')
    # for i in range(annotation.ann_len):
    #     if annotation.symbol[i] in ['+', '~', '|', '[', '!', ']', '"', 's', 'x']:
    #         continue
    #     label[annotation.sample[i] - POSITIVE_RANGE:annotation.sample[i] + POSITIVE_RANGE + 1] = 1
    # label = np.array(label[int(0.1*FREQUENCY_SAMPLING):signal_length - int(0.3*FREQUENCY_SAMPLING)], dtype='int8')

    # print(np.sum(label))
    # # import matplotlib.pyplot as plt
    # ranged = 1000
    # inds = np.flatnonzero(label[:ranged])
    # seg = signal[int(0.1 * FREQUENCY_SAMPLING):ranged + int(0.1 * FREQUENCY_SAMPLING)]
    # plt.plot(seg)
    # plt.plot(inds, seg[inds], 'r*')
    # plt.grid()
    # plt.gcf().set_size_inches(20, 5)
    # plt.show()

    # return data_sample, label
    return signal, np.array(label)