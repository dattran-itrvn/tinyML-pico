import numpy as np
import tensorflow.python.keras.models
import math
from preprocess import *
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random
import time

sample_rate = 128


def getdatafull(DATA_DIR_STR, DIR_FOLDER):
    full_list = []
    sample5s = 128 * 5
    for index in DATA_DIR_STR:
        DATA_DIR = DIR_FOLDER + str(index) + ".atr"
        signal, label = preprocess_data(DATA_DIR)
        l = int(len(signal) // (sample5s))
        nlb = int(len(signal) // int(128 * 0.125))
        lb = np.zeros(nlb)
        for i in label:
            lb[i] = 1
        for i in range(l - 1):
            spectrogram = create_spectrogram(signal[sample5s * i:sample5s * (i + 1)])
            # print(spectrogram.shape)
            new_row = np.zeros(spectrogram.shape[1])
            spectrogram = np.append(spectrogram, [new_row], axis=0)
            # print(spectrogram.shape)
            new_col = np.zeros(spectrogram.shape[0])
            spectrogram = np.append(spectrogram, np.transpose([new_col]), axis=1)
            spectrogram = np.transpose(spectrogram)
            spectrogram = spectrogram[:, :, np.newaxis]
            # print(spectrogram.shape)
            # plot_spectrogram(spectrogram)
            full_list.append([spectrogram, lb[40 * i:40 * (i + 1)]])

    return full_list


def getdata(DATA_DIR_STR, DIR_FOLDER, shape=True):
    data_list = []
    label_list = []
    sample5s = 128 * 5
    signal_list = []
    for index in DATA_DIR_STR:
        DATA_DIR = DIR_FOLDER + str(index) + ".atr"
        signal, label = preprocess_data(DATA_DIR)
        l = int(len(signal) // (sample5s))
        nlb = int(len(signal) // int(128 * 0.125))
        lb = np.transpose([[np.ones(nlb)], [np.zeros(nlb)]]).reshape(nlb, 2)
        sn_list = []
        for i in label:
            lb[i] = [0, 1]
        for i in range(l - 1):
            spectrogram = create_spectrogram(signal[sample5s * i:sample5s * (i + 1)])
            # print(spectrogram.shape)
            new_row = np.zeros(spectrogram.shape[1])
            spectrogram = np.append(spectrogram, [new_row], axis=0)
            # # print(spectrogram.shape)
            new_col = np.zeros(spectrogram.shape[0])
            spectrogram = np.append(spectrogram, np.transpose([new_col]), axis=1)
            # plot_spectrogram(spectrogram)
            # spectrogram = np.transpose(spectrogram)
            spectrogram = spectrogram[:, :, np.newaxis]
            # print(spectrogram.shape)
            # plot_spectrogram(spectrogram)

            data_list.append(spectrogram)
            lbs = lb[40 * i:40 * (i + 1)][:]
            label_list.append(lbs)
            sn_list.append(spectrogram)
        signal_list.append(np.array(sn_list))
    return np.array(data_list), np.array(label_list), np.array(signal_list)


def ch_getdata(index, DIR_FOLDER, shape=True):
    data_list = []
    label_list = []
    sample5s = 128 * 5
    signal_list = []
    DATA_DIR = DIR_FOLDER + str(index) + ".atr"
    signal, label = preprocess_data(DATA_DIR)
    l = int(len(signal) // (sample5s))
    nlb = int(len(signal) // int(128 * 0.125))
    lb = np.transpose([[np.ones(nlb)], [np.zeros(nlb)]]).reshape(nlb, 2)
    sn_list = []
    for i in label:
        lb[i] = [0, 1]
    for i in range(l - 1):
        spectrogram = create_spectrogram(signal[sample5s * i:sample5s * (i + 1)])
        # print(spectrogram.shape)
        new_row = np.zeros(spectrogram.shape[1])
        spectrogram = np.append(spectrogram, [new_row], axis=0)
        # # print(spectrogram.shape)
        new_col = np.zeros(spectrogram.shape[0])
        spectrogram = np.append(spectrogram, np.transpose([new_col]), axis=1)
        # plot_spectrogram(spectrogram)
        # spectrogram = np.transpose(spectrogram)
        spectrogram = spectrogram[:, :, np.newaxis]
        # print(spectrogram.shape)
        # plot_spectrogram(spectrogram)

        data_list.append(spectrogram)
        lbs = lb[40 * i:40 * (i + 1)][:]
        label_list.append(lbs)
        sn_list.append(spectrogram)
    signal_list.append(np.array(sn_list))
    return np.array(data_list), np.array(label_list), np.array(signal_list)


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


def plotdata(index, mode='train'):
    rec = []
    bound = int(0.125 * 128)
    if mode == 'train':
        signal, label = preprocess_data(DATA_DIR_FOLDER + str(TRAIN_DATA_DIR_STR[index]) + ".atr")
    else:
        signal, label = preprocess_data(DATA_DIR_FOLDER + str(VALID_DATA_DIR_STR[index]) + ".atr")
    for i in label:
        # if label[i] == 0:
        #     continue
        rec.append(Rectangle((i * bound, -0.3), bound, 1.3, fill=False, edgecolor='r'))
    fig, ax = plt.subplots()
    ax.plot(signal, label='signal')
    for rectangle in rec:
        ax.add_patch(rectangle)
    plt.show()
    # plt.savefig("image/"+mode+str(index)+".png")


def test_model(model, mode='train', shape=True):
    model.summary()
    if mode == 'train':
        DATA_DIR_STR = TRAIN_DATA_DIR_STR
    elif mode == 'valid':
        DATA_DIR_STR = VALID_DATA_DIR_STR
    else:
        DATA_DIR_STR = ANOTHER_DATA_DIR_STR

    data, label, seg_signal = getdata(DATA_DIR_STR=DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER, shape=shape)
    label_post = []
    peek_post = []
    bound = int(0.125 * 128)
    for i in range(len(seg_signal)):
        signal, _ = preprocess_data(DATA_DIR_FOLDER + str(DATA_DIR_STR[i]) + ".atr")
        predict = np.zeros(len(seg_signal[i]) * 40)
        for j in range(len(seg_signal[i])):
            pre = model.predict(seg_signal[i][j:j + 1]).reshape(40, 2)
            for k in range(len(pre)):
                predict[j * 40 + k] = np.argmax(pre[k])
        # label_post.append(predict)
        peek = []
        for j in range(len(predict) - 1):
            if predict[j] == 0:
                if j == len(predict) - 2:
                    peek.append(np.argmax(np.abs(signal[(j + 1) * bound: (j + 2) * bound])) + (j + 1) * bound)
                continue
            if predict[j + 1] == 1:
                if signal[np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound] > signal[
                    np.argmax(np.abs(signal[(j + 1) * bound: (j + 2) * bound])) + (j + 1) * bound]:
                    predict[j + 1] = 0
                    peek.append(np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound)
                else:
                    predict[j] = 1
                    peek.append(np.argmax(np.abs(np.abs(signal[(j + 1) * bound: (j + 2) * bound]))) + (j + 1) * bound)
            else:
                peek.append(np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound)
        s = 0
        sbb = []
        for m in range(len(peek)):
            sbb.append('N')
            peek[m] = int(peek[m] * 360 / 128)

        annotation = wfdb.Annotation(record_name=str(DATA_DIR_STR[i]),
                                     extension='txt',
                                     sample=np.asarray(peek),
                                     symbol=np.asarray(sbb),
                                     fs=360)
        annotation.wrann(write_fs=True)
        # plotdata(signal, predict, peek)


# def testmodel(model, mode='train', shape=True):
#     model.summary()
#     if mode == 'train':
#         DATA_DIR_STR = TRAIN_DATA_DIR_STR
#
#     else:
#         DATA_DIR_STR = VALID_DATA_DIR_STR
#
#     data, label = getdata(DATA_DIR_STR=DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER, shape=shape)
#     pre_label = []
#     sb = []
#     for k in range(1):
#         pre_lb = []
#         sbb=[]
#         for j in range(data.shape[1]):
#             pre = model.predict(data[k][j:j + 1]).reshape(40, 2)
#             # # print(pre)
#             for i in range(len(pre)):
#                 # pre_label[j*40+i] = np.argmax(pre[i])
#                 if np.argmax(pre[i]) == 1:
#                     pre_lb.append(j*40+i)
#         pre_label.append(pre_lb)
#         for m in range(len(pre_lb)):
#             sbb.append('N')
#         sb.append(sbb)
#
#     for k in range(1):
#         annotation = wfdb.Annotation(record_name=str(DATA_DIR_STR[k]),
#                                       extension='txt',
#                                       sample=np.asarray(pre_label[k]),
#                                       symbol=np.asarray(sb[k]),
#                                       fs=360)
#         annotation.wrann(write_fs=True)

def anno(data):
    for i in data:
        annotation = wfdb.rdann("C:/Users/AI-DEV/Downloads/mit-bih-arrhythmia-database-1.0.0/" + str(i), 'atr')
        peek = []
        sbb = []
        for k in range(annotation.ann_len):
            if annotation.symbol[k] in ['+', '~', '|', '[', '!', ']', '"', 's', 'x']:
                continue
            peek.append(annotation.sample[k])
            sbb.append(annotation.symbol[k])
        # annotation2 = wfdb.Annotation(record_name=str(i),
        #                               extension='atr',
        #                               sample=np.asarray(peek),
        #                               symbol=np.asarray(sbb),
        #                               fs=360)
        # annotation2.wrann(write_fs=True)


def ch_test_model(model, index, shape=True):
    model.summary()

    data, label, seg_signal = ch_getdata(str(index), DIR_FOLDER=DATA_DIR_FOLDER, shape=shape)

    bound = int(0.125 * 128)
    signal, _ = preprocess_data(DATA_DIR_FOLDER + str(index) + ".atr")
    predict = np.zeros(len(seg_signal[0]) * 40)
    for j in range(len(seg_signal[0])):
        pre = model.predict(seg_signal[0][j:j + 1]).reshape(40, 2)
        for k in range(len(pre)):
            # if np.abs(math.log(pre[k][0] / pre[k][1])) < 0.7:
            #     predict[j * 40 + k] = 1
            # else:
                predict[j * 40 + k] = np.argmax(pre[k])
    # label_post.append(predict)
    peek = []
    for j in range(len(predict)):
        if predict[j] == 1:
            peek.append(np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound)
    # for j in range(len(predict) - 1):
    #     if predict[j] == 0:
    #         if j == len(predict) - 2:
    #             peek.append(np.argmax(np.abs(signal[(j + 1) * bound: (j + 2) * bound])) + (j + 1) * bound)
    #         continue
    #     if predict[j + 1] == 1:
    #         if signal[np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound] > signal[np.argmax(np.abs(signal[(j + 1) * bound: (j + 2) * bound])) + (j + 1) * bound]:
    #             predict[j + 1] = 0
    #             peek.append(np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound)
    #         else:
    #             predict[j] = 1
    #             peek.append(np.argmax(np.abs(np.abs(signal[(j + 1) * bound: (j + 2) * bound]))) + (j + 1) * bound)
    #     else:
    #         peek.append(np.argmax(np.abs(signal[j * bound: (j + 1) * bound])) + j * bound)
    s = 0
    sbb = []
    for m in range(len(peek)):
        sbb.append('N')
        peek[m] = int(peek[m] * 360 / 128)
    peek = np.array(peek)
    sbb = np.array(sbb)
    l = len(peek) - 1
    m = 0
    while (m < l):
        if np.abs(peek[m] - peek[m + 1]) < 27:
            peek = np.delete(peek, m)
            sbb = np.delete(sbb, m)
            m -= 1
            l -= 1
        m += 1

    annotation = wfdb.Annotation(record_name=str(index),
                                 extension='txt',
                                 sample=np.asarray(peek),
                                 symbol=np.asarray(sbb),
                                 fs=360)
    annotation.wrann(write_fs=True)
    # plotdata(signal, predict, peek)


def ch_anno(i):
    annotation = wfdb.rdann("C:/Users/AI-DEV/Downloads/mit-bih-arrhythmia-database-1.0.0/" + str(i), 'atr')
    peek = []
    sbb = []
    for k in range(annotation.ann_len):
        if annotation.symbol[k] in ['+', '~', '|', '[', '!', ']', '"', 's', 'x']:
            continue
        if annotation.sample[k] >= 648000:
            break
        peek.append(annotation.sample[k])
        sbb.append(annotation.symbol[k])
    annotation2 = wfdb.Annotation(record_name=str(i),
                                  extension='atr',
                                  sample=np.asarray(peek),
                                  symbol=np.asarray(sbb),
                                  fs=360)
    annotation2.wrann(write_fs=True)


if __name__ == '__main__':
    path = r'C:\Users\AI-DEV\Documents\Train\CP\run-0\model.h5'
    detect_path = 'C:/Users/AI-DEV/Downloads/201.txt'
    DATA_DIR_FOLDER = "C:/Users/AI-DEV/Downloads/mit-bih-arrhythmia-database-1.0.0/"
    TRAIN_DATA_DIR_STR = [101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215,
                          220, 223, 230]
    VALID_DATA_DIR_STR = [100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231,
                          232, 233, 234]
    ANOTHER_DATA_DIR_STR = [102, 104, 107, 117, 217]
    model = tf.keras.models.load_model('model/model_v24.h5')
    # test_model(model, mode='valid', shape=True)
    # test_model(model, mode='train', shape=True)
    # anno(VALID_DATA_DIR_STR)
    # ch_test_model(model, 100)
    # ch_anno(100)
    for i in TRAIN_DATA_DIR_STR:
        ch_test_model(model, i)
        ch_anno(i)
    for i in VALID_DATA_DIR_STR:
        ch_test_model(model, i)
        ch_anno(i)
    # anno(ANOTHER_DATA_DIR_STR)
    # data, label = getdata(DATA_DIR_STR=TRAIN_DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER)
    # pre = model.predict(data[0:1]).reshape(40,2)
    # print(pre)
    # predict = np.zeros(40)
    # # print(pre)
    # for i in range(len(pre)):
    #     predict[i]=np.argmax(pre[i])
    # print(predict)
    # result = label[0]
    # print(np.transpose(result)[1])
    # s=0
    # for i in range(len(pre)):
    #     if pre[i] == result[i]:
    #         s += 1
    # print(s)
    # print(s / (len(data) * 40))
