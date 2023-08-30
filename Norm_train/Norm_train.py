import numpy as np

from preprocess import *
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import random
from constantQ.timeseries import TimeSeries
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


def normalize_spectrogram(spectrogram):
    spectrogram_min = tf.reduce_min(spectrogram, axis=(1, 2), keepdims=True)
    spectrogram_max = tf.reduce_max(spectrogram, axis=(1, 2), keepdims=True)
    normalized_spectrogram = (spectrogram - spectrogram_min) / (spectrogram_max - spectrogram_min)
    return normalized_spectrogram

def exp(spec):
    spect = np.transpose(spec)
    d = np.zeros(80*10).reshape(10,80)
    # for i in range(4):
    d[1]=np.exp(spect[1])
    return np.transpose(d)

def getdata(DATA_DIR_STR, DIR_FOLDER, shape=True):
    signal_list = []
    label_list = []
    sample5s = 128 * 5
    for index in DATA_DIR_STR:
        # print(index)
        DATA_DIR = DIR_FOLDER + str(index) + ".atr"
        signal, label = preprocess_data(DATA_DIR)
        l = int(len(signal) // (sample5s))
        nlb = int(len(signal) // int(128 * 0.125))
        lb = np.transpose([[np.ones(nlb)], [np.zeros(nlb)]]).reshape(nlb, 2)
        for i in label:
            lb[i] = [0, 1]
        for i in range(l - 1):
            # print(i)
            # min_data = np.min(signal[sample5s * i:sample5s * (i + 1)])
            # max_data = np.max(signal[sample5s * i:sample5s * (i + 1)])

            # data = signal[sample5s * i:sample5s * (i + 1)]
            # mean = np.sum(data) / len(data)
            # standard_deviation = np.sqrt(np.sum((data - mean) ** 2) / len(data))
            # y = (data - mean) / standard_deviation
            # spectrogram = create_spectrogram(y)
            series = TimeSeries(signal[sample5s * i:sample5s * (i + 1)], dt=1/sample_rate, unit='m', name='test', t0=0)  # np.array --> gwpy.timeseries
            hdata = series
            # spectrogram = np.zeros(79*9).reshape(79,9)
            # spectrogram[:,1] = np.transpose(hdata.q_transform(search=None))[:,1]
            spectrogram = np.transpose(hdata.q_transform(search=None))
            # spectrogram = create_spectrogram(signal[sample5s * i:sample5s * (i + 1)])
            # for k in range(spectrogram.shape[1]):
            #     max = np.max(spectrogram.numpy()[:,k])
            #     min = np.min(spectrogram.numpy()[:,k])
            #     for m in range(spectrogram.shape[0]):
            #         new_value = (spectrogram[m][k] - min) / (max - min)
            #         spectrogram = tf.tensor_scatter_nd_update(spectrogram, [[m, k]], [new_value])
            #
            # # print(spectrogram.shape)
            # spectrogram = spectrogra.numpy()
            # min_values = np.min(spectrogram, axis=0)
            # max_values = np.max(spectrogram, axis=0)
            #
            # # Broadcasting the min and max values to the same shape as the spectrogram
            # min_broadcasted = min_values[np.newaxis, :]
            # max_broadcasted = max_values[np.newaxis, :]
            #
            # # Perform the element-wise operations
            # spectrogram = (spectrogram - min_broadcasted) / (max_broadcasted - min_broadcasted)
            if shape:
                new_row = np.zeros(spectrogram.shape[1])
                spectrogram = np.append(spectrogram, [new_row], axis=0)
                # # print(spectrogram.shape)
                new_col = np.zeros(spectrogram.shape[0])
                spectrogram = np.append(spectrogram, np.transpose([new_col]), axis=1)
                # plot_spectrogram(spectrogram)
                # spectrogram = np.transpose(spectrogram)
                # spectrogram = exp(spectrogram)
                # plot_spectrogram(spectrogram)
            spectrogram = spectrogram[:, :, np.newaxis]
            # print(spectrogram.shape)
            # plot_spectrogram(spectrogram)

            signal_list.append(spectrogram)
            lbs = lb[40 * i:40 * (i + 1)][:]
            label_list.append(lbs)
    return np.array(signal_list), np.array(label_list)


def clustering(data):
    positive_point = np.where(data == 1)[0]
    beat = []
    if len(positive_point) > 5:
        cluster = np.array([positive_point[0]])
        for i in range(1, len(positive_point)):
            if positive_point[i] - cluster[-1] > 0.08 * FREQUENCY_SAMPLING or i == len(positive_point) - 1:
                if i == len(positive_point) - 1:
                    cluster = np.append(cluster, positive_point[i])
                if cluster.shape[0] > 5:
                    beat.append(int(np.mean(cluster)))
                cluster = np.array([positive_point[i]])
            else:
                cluster = np.append(cluster, positive_point[i])

    return np.asarray(beat)


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


if __name__ == '__main__':
    path = r'C:\Users\AI-DEV\Documents\Train\CP\run-0\model.h5'
    detect_path = 'C:/Users/AI-DEV/Downloads/201.txt'
    DATA_DIR_FOLDER = "C:/Users/AI-DEV/Downloads/mit-bih-arrhythmia-database-1.0.0/"
    TRAIN_DATA_DIR_STR = [101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215,
                          220, 223, 230]
    VALID_DATA_DIR_STR = [100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231,
                          232, 233, 234]
    # _, _ = getdata(DATA_DIR_STR=[222], DIR_FOLDER=DATA_DIR_FOLDER, shape=True)
    train_data, train_label = getdata(DATA_DIR_STR=TRAIN_DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER, shape=True)
    valid_data, valid_label = getdata(DATA_DIR_STR=VALID_DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER, shape=True)

    # train_full_list = getdatafull(DATA_DIR_STR=TRAIN_DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER)
    # valid_full_list = getdatafull(DATA_DIR_STR=VALID_DATA_DIR_STR, DIR_FOLDER=DATA_DIR_FOLDER)
    # random.shuffle(train_data)
    # s = 0
    # plotdata(index=0, mode='train')
    # for i in range(len(TRAIN_DATA_DIR_STR)):
    #     plotdata(index=i, mode='train')
    # for i in range(len(VALID_DATA_DIR_STR)):
    #     plotdata(index=i, mode='valid')
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(80, 10, 1)),
        tf.keras.layers.Conv2D(128, kernel_size=(3, 3), strides=2, activation='relu', padding='same'),
        tf.keras.layers.Conv2D(1, kernel_size=(1, 4), strides=1, activation='sigmoid'),
        tf.keras.layers.Reshape((40, 2))
    ])
    model.summary()

    METRICS = [
        "accuracy",
    ]
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=METRICS,
    )


    def scheduler(epoch, lr):
        if epoch < 100:
            return lr
        else:
            return lr * tf.math.exp(-0.1)


    callbacks = [
        # tf.keras.callbacks.EarlyStopping(verbose=1, patience=25),
        tf.keras.callbacks.LearningRateScheduler(scheduler)
    ]
    EPOCHS = 200
    history = model.fit(
        train_data,
        train_label,
        shuffle=True,
        validation_data=(valid_data, valid_label),
        batch_size=32,
        epochs=EPOCHS,
        callbacks=callbacks,
    )
    model.save("model/model_v30.h5")
