import glob
import time

import numpy as np
import wfdb
from scipy.signal import filtfilt, butter
import random
from define import *
import scipy.signal as spysig
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image


sample_rate = 250
cnt_s = 0
cnt = 0


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


@tf.function
def create_spectrogram(samples):
    return tf.abs(
        tf.signal.stft(samples, frame_length=16, frame_step=8)
    )


def plot_spectrogram(spectrogram, vmax=None):
    transposed_spectrogram = tf.transpose(spectrogram)

    fig = plt.figure(figsize=(8, 6))
    height = transposed_spectrogram.shape[0]
    X = np.arange(transposed_spectrogram.shape[1])
    Y = np.arange(height * int(sample_rate / 16), step=int(sample_rate / 16))

    im = plt.pcolormesh(X, Y, tf.transpose(spectrogram), vmax=vmax)

    fig.colorbar(im)
    plt.show()


def spect_data(signal):
    x = create_spectrogram(signal)
    # plot_spectrogram(x)
    # model = tf.keras.models.load_model("model_new/mobile.h5")
    # model.summary()
    spectrogram_data = x.numpy()
    spectrogram_data_normalized = ((spectrogram_data - np.min(spectrogram_data)) / (
            np.max(spectrogram_data) - np.min(spectrogram_data)) * 255).astype(np.uint8)
    height, width = spectrogram_data_normalized.shape

    # Create a 4-channel array with RGBA format
    rgba_data = np.zeros((height, width, 3), dtype=np.uint8)
    rgba_data[:, :, 0] = spectrogram_data_normalized
    rgba_data[:, :, 1] = spectrogram_data_normalized
    rgba_data[:, :, 2] = spectrogram_data_normalized

    top1 = 191
    bot1 = 127
    top2 = bot1
    bot2 = 63
    topn = bot2
    botn = 5
    if True in (spectrogram_data_normalized >= top1):
        mintop1 = int(np.min(spectrogram_data_normalized[spectrogram_data_normalized >= top1]))
        maxtop1 = int(np.max(spectrogram_data_normalized[spectrogram_data_normalized >= top1]))
        specttop1 = spectrogram_data_normalized[spectrogram_data_normalized >= top1].astype(np.uint32)
        rgba_data[:, :, 0][spectrogram_data_normalized >= top1] = 255
        rgba_data[:, :, 1][spectrogram_data_normalized >= top1] = 255
        rgba_data[:, :, 2][spectrogram_data_normalized >= top1] = (
                102 - (specttop1 - mintop1) * 102 / (maxtop1 - mintop1)).astype(np.uint8)
    if True in ((spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)):
        mintop1bot1 = int(np.min(
            spectrogram_data_normalized[(spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)]))
        maxtop1bot1 = int(np.max(
            spectrogram_data_normalized[(spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)]))
        specttop1bot1 = spectrogram_data_normalized[
            (spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)].astype(np.uint32)
        rgba_data[:, :, 0][(spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)] = (
                (specttop1bot1 - mintop1bot1) * 204 / (maxtop1bot1 - mintop1bot1)).astype(np.uint8)
        rgba_data[:, :, 1][(spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)] = 255
        rgba_data[:, :, 2][(spectrogram_data_normalized < top1) & (spectrogram_data_normalized >= bot1)] = 0
    if True in ((spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)):
        mintop2bot2 = int(np.min(
            spectrogram_data_normalized[(spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)]))
        maxtop2bot2 = int(np.max(
            spectrogram_data_normalized[(spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)]))
        specttop2bot2 = spectrogram_data_normalized[
            (spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)].astype(np.uint32)
        rgba_data[:, :, 0][(spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)] = 0
        rgba_data[:, :, 1][(spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)] = 255
        rgba_data[:, :, 2][(spectrogram_data_normalized < top2) & (spectrogram_data_normalized >= bot2)] = (
                153 - (specttop2bot2 - mintop2bot2) * 153 / (maxtop2bot2 - mintop2bot2) + 102).astype(np.uint8)
    if True in ((spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)):
        mintopnbotn = int(np.min(
            spectrogram_data_normalized[(spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)]))
        maxtopnbotn = int(np.max(
            spectrogram_data_normalized[(spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)]))
        specttopnbotn = spectrogram_data_normalized[
            (spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)].astype(np.uint32)
        rgba_data[:, :, 0][(spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)] = (
                153 - (specttopnbotn - mintopnbotn) * 153 / (maxtopnbotn - mintopnbotn) + 51).astype(np.uint8)
        rgba_data[:, :, 1][(spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)] = 255
        rgba_data[:, :, 2][(spectrogram_data_normalized < topn) & (spectrogram_data_normalized >= botn)] = 255

    rgba_data[:, :, 0][spectrogram_data_normalized < botn] = 255
    rgba_data[:, :, 1][spectrogram_data_normalized < botn] = 255
    rgba_data[:, :, 2][spectrogram_data_normalized < botn] = 255

    # rgba_data[3, 0, 1]=spectrogram_data_normalized[3,0]
    # rgba_data[:, :, 1]
    # Create a PIL Image from the normalized spectrogram data
    image = Image.fromarray(rgba_data, mode='RGB')
    image = image.rotate(90, expand=True)
    image = image.resize((112, 112))
    # Save the image as a file
    # image.save('spectrogram_image.png')
    # image.show()
    image_array = np.array(image)
    return image_array


def preprocessing(data_path):
    input_data = []
    input_data_gray = []
    label = []
    for part in data_path:
        if len(glob.glob(part.replace('\\', '/') + '*')) > 3:
            print(part)
            continue
        tmp = glob.glob(part.replace('\\', '/') + '*')[0].replace('\\', '/')
        tmp = tmp.split('.')[0]
        info = wfdb.rdheader(tmp)
        signal, _ = wfdb.rdsamp(tmp, channels=[0])
        annotation = wfdb.rdann(tmp, 'atr')
        signal = signal[:, 0]
        signal = butter_bandpass_filter(signal, 1, 40, 250, order=3)
        input_data.append(spect_data(signal))
        input_data_gray.append(spect_data_gray(signal))
        # input = spect_data(signal)
        # input = spect_data_gray(signal)
        label.append(get_label(annotation))
    return np.array(input_data), np.array(input_data_gray), np.array(label)


def spect_data_gray(signal):
    x = create_spectrogram(signal)
    # plot_spectrogram(x)
    # model = tf.keras.models.load_model("model_new/mobile.h5")
    # model.summary()
    spectrogram_data = x.numpy()
    spectrogram_data_normalized = ((spectrogram_data - np.min(spectrogram_data)) / (
            np.max(spectrogram_data) - np.min(spectrogram_data)) * 255).astype(np.uint8)
    height, width = spectrogram_data_normalized.shape

    # Create a 4-channel array with RGBA format
    rgba_data = np.zeros((height, width, 3), dtype=np.uint8)
    rgba_data[:, :, 0] = spectrogram_data_normalized
    rgba_data[:, :, 1] = spectrogram_data_normalized
    rgba_data[:, :, 2] = spectrogram_data_normalized

    image = Image.fromarray(rgba_data, mode='RGB')
    image = image.rotate(90, expand=True)
    image = image.resize((112, 112))
    # Save the image as a file
    # image.save('spectrogram_image.png')
    # image.show()
    image_array = np.array(image)
    return image_array


def get_label(annotation):
    sb = np.zeros((100, 4))
    sb[:, 0] = 1
    ann = annotation.sample
    j = 0
    for i in ann:
        t0 = i // 25
        if annotation.symbol[j] == 'N':
            sb[t0][0] = 0
            sb[t0][1] = 1
        elif annotation.symbol[j] == 'S':
            sb[t0][0] = 0
            sb[t0][2] = 1
        elif annotation.symbol[j] == 'V':
            sb[t0][0] = 0
            sb[t0][3] = 1
        j += 1
    sb = sb.reshape(400)
    return sb


folder_path = glob.glob('C:/Users/AI-DEV/Downloads/OneDrive_2_10-2-2023/*/')
data_path = glob.glob(folder_path[0].replace('\\', '/') + '*/')
data_path.extend(glob.glob(folder_path[1].replace('\\', '/') + '*/'))
# data_path.extend(glob.glob(folder_path[1].replace('\\','/')+'*/'))
V_data_part = glob.glob(folder_path[2].replace('\\', '/') + '*/')
V_data_path = []
for part in V_data_part:
    path = glob.glob(part.replace('\\', '/') + '*/')
    for i in path:
        V_data_path.append(i.replace('\\', '/'))
data_path.extend(V_data_path)
input_data, input_data_gray, label=preprocessing(data_path)
# np.save("numpy_file/label_mobilenet_400.npy", input_data)
# s=0
np.save("numpy_file/input_data_mobilenet.npy", input_data)
np.save("numpy_file/input_data_mobilenet_gray.npy", input_data_gray)
np.save("numpy_file/label_mobilenet_4.npy", label)



