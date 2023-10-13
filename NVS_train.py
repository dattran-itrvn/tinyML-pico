import glob
import time

import numpy as np
import wfdb
from scipy.signal import filtfilt, butter
import random
# from define import *
import scipy.signal as spysig
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image
# from sklearn.utils.class_weight import compute_class_weight

sample_rate = 250
cnt_s = 0
cnt = 0


def check(data):
    if data >= 2 and data < 2.6:
        return True
    else:
        return False


def custom_loss3(y_true, y_pred):
    # print((y_true.numpy()).shape)
    y_true_custom = y_true
    y_pred_custom = y_pred
    # print(y_pred[0])
    # print(y_true_custom)
    # y_true_custom_No = tf.convert_to_tensor(y_true_custom[y_true_custom[:, :, 0] == 1])
    # y_true_custom_No = tf.convert_to_tensor(y_true_custom.reshape((len(y_true_custom_No)//4,4)))
    # y_true_custom_N = y_true_custom[y_true_custom[:, :, 1] == 1]
    # y_true_custom_N = tf.convert_to_tensor(y_true_custom.reshape((len(y_true_custom_N) // 4, 4)))
    # y_true_custom_S = y_true_custom[y_true_custom[:, :, 2] == 1]
    # y_true_custom_S = tf.convert_to_tensor(y_true_custom.reshape((len(y_true_custom_S) // 4, 4)))
    # y_true_custom_V = y_true_custom[y_true_custom[:, :, 3] == 1]
    # y_true_custom_V = tf.convert_to_tensor(y_true_custom.reshape((len(y_true_custom_V) // 4, 4)))
    y_true_custom_No = tf.convert_to_tensor(y_true_custom[y_true_custom[:, :, 0] == 1])
    y_pred_custom_No = tf.convert_to_tensor(y_pred_custom[y_true_custom[:, :, 0] == 1])
    y_true_custom_N = tf.convert_to_tensor(y_true_custom[y_true_custom[:, :, 1] == 1])
    y_pred_custom_N = tf.convert_to_tensor(y_pred_custom[y_true_custom[:, :, 1] == 1])
    y_true_custom_S = tf.convert_to_tensor(y_true_custom[y_true_custom[:, :, 2] == 1])
    y_pred_custom_S = tf.convert_to_tensor(y_pred_custom[y_true_custom[:, :, 2] == 1])
    y_true_custom_V = tf.convert_to_tensor(y_true_custom[y_true_custom[:, :, 3] == 1])
    y_pred_custom_V = tf.convert_to_tensor(y_pred_custom[y_true_custom[:, :, 3] == 1])
    # print("true ",len(y_true_No))
    # print("true ", y_true[y_true[:, :, 0] == 1][0,:])
    epsilon = 1e-15
    # print(y_pred.numpy())
    # lossNo = np.mean(np.)
    # lossNo = -tf.reduce_sum(y_true_No * tf.math.log(y_pred_No + 1e-15))
    # lossN = -tf.reduce_sum(y_true_N * tf.math.log(y_pred_N + 1e-15))
    # lossS = -tf.reduce_sum(y_true_S * tf.math.log(y_pred_S + 1e-15))
    # lossV = -tf.reduce_sum(y_true_V * tf.math.log(y_pred_V + 1e-15))
    loss = 0
    s = 0
    # print()
    # print(y_true_No.shape)

    if len(y_true_custom_No) != 0 and len(y_pred_custom_No) != 0:
        # print(y_pred_custom_No.shape)
        # print("pred No1 ", y_pred[y_true[:, :, 0] == 1][0, :])
        # print("pred No2 ", 1/(y_true_No.shape[0]*y_true_No.shape[1])*tf.reduce_sum(abs(y_true_No - y_pred_No)))

        # loss+=tf.reduce_mean(tf.square(y_true_No - y_pred_No))
        # print(y_true_No.shape)
        loss += (1 / (y_true_custom_No.shape[0] * y_true_custom_No.shape[1])) * tf.reduce_sum((y_true_custom_No - y_pred_custom_No)**2)

        # y_pred_custom_No = tf.clip_by_value(y_pred_custom_No, epsilon, 1 - epsilon)  # Giới hạn giá trị dự đoán
        # loss += -(1 / (y_true_custom_No.shape[0] * y_true_custom_No.shape[1])) *tf.reduce_sum(y_true_custom_No * tf.math.log(y_pred_custom_No))
        # loss += focal_loss_fixed(y_true_custom_No, y_pred_custom_No)*1.001

        # loss += categorical_cross_entropy(y_true_custom_No, y_pred_custom_No)
        # print()
        # loss+=-1/(y_true_No.shape[0]*y_true_No.shape[1])*tf.reduce_sum((y_true_No * tf.math.log(y_pred_No))+(1-y_true_No) * tf.math.log(1-y_pred_No))
        # print("loss No ", focal_loss_fixed(y_true_custom_No, y_pred_custom_No))
        s += 1
    if len(y_true_custom_N) != 0 and len(y_pred_custom_N) != 0:
        # print("pred N1 ", y_pred[y_true[:, :, 1] == 1][0, :])
        # print("pred N2 ", 1/(y_true_N.shape[0]*y_true_N.shape[1])*tf.reduce_sum(abs(y_true_N - y_pred_N)))

        # loss+=tf.reduce_mean(tf.square(y_true_N - y_pred_N))
        loss += (1 / (y_true_custom_N.shape[0] * y_true_custom_N.shape[1])) * tf.reduce_sum((y_true_custom_N - y_pred_custom_N)**2)
        # # y_pred_custom_N = tf.clip_by_value(y_pred_custom_N, epsilon, 1 - epsilon)  # Giới hạn giá trị dự đoán
        # loss += -(1 / (y_true_custom_N.shape[0] * y_true_custom_N.shape[1])) *tf.reduce_sum(y_true_custom_N * tf.math.log(y_pred_custom_N))
        # loss += focal_loss_fixed(y_true_custom_N, y_pred_custom_N)
        # print("loss N ",focal_loss_fixed(y_true_custom_N, y_pred_custom_N))
        s += 1
    if len(y_true_custom_S) != 0 and len(y_pred_custom_S) != 0:
        # print("pred S1 ", y_pred[y_true[:, :, 2] == 1][0, :])
        # print("pred S2 ", 1/(y_true_S.shape[0]*y_true_S.shape[1])*tf.reduce_sum(abs(y_true_S - y_pred_S)))

        # loss+=tf.reduce_mean(tf.square(y_true_S - y_pred_S))
        loss += (1 / (y_true_custom_S.shape[0] * y_true_custom_S.shape[1])) * tf.reduce_sum((y_true_custom_S - y_pred_custom_S)**2)
        # y_pred_custom_S = tf.clip_by_value(y_pred_custom_S, epsilon, 1 - epsilon)  # Giới hạn giá trị dự đoán
        # loss += -(1 / (y_true_custom_S.shape[0] * y_true_custom_S.shape[1])) *tf.reduce_sum(y_true_custom_S * tf.math.log(y_pred_custom_S))
        # loss += focal_loss_fixed(y_true_custom_S, y_pred_custom_S)
        # print("loss S ", focal_loss_fixed(y_true_custom_S, y_pred_custom_S))
        s += 1
    if len(y_true_custom_V) != 0 and len(y_pred_custom_V) != 0:
        # print("pred V1 ", y_pred[y_true[:, :, 3] == 1][0, :])
        # print("pred V2 ", 1/(y_true_V.shape[0]*y_true_V.shape[1])*tf.reduce_sum(abs(y_true_V - y_pred_V)))

        # loss+=tf.reduce_mean(tf.square(y_true_V - y_pred_V))
        loss += (1 / (y_true_custom_V.shape[0] * y_true_custom_V.shape[1])) * tf.reduce_sum((y_true_custom_V - y_pred_custom_V)**2)
        # y_pred_custom_V = tf.clip_by_value(y_pred_custom_V, epsilon, 1 - epsilon)  # Giới hạn giá trị dự đoán
        # loss += -(1 / (y_true_custom_V.shape[0] * y_true_custom_V.shape[1])) *tf.reduce_sum(y_true_custom_V * tf.math.log(y_pred_custom_V))
        # loss += focal_loss_fixed(y_true_custom_V, y_pred_custom_V)
        # print("loss V ", focal_loss_fixed(y_true_custom_V, y_pred_custom_V))
        s += 1
    # lossN = tf.reduce_mean(abs(y_true_N - y_pred_N))
    # lossS = tf.reduce_mean(abs(y_true_S - y_pred_S))
    # lossV = tf.reduce_mean(abs(y_true_V - y_pred_V))
    # print('lossNo',lossNo)
    # print('lossN',lossN)
    # print('lossS',lossS)
    # print('lossV',lossV)
    # print("loss1 ",loss)
    # print("s ",s)
    loss = loss / s
    # print(loss)
    # print("loss2 ", loss)
    return tf.convert_to_tensor(loss, dtype=tf.float32)




def acc(y_true, y_pred):
    global cnt, cnt_s
    cnt_s = 0
    cnt = 0
    y_true_acc = y_true.numpy()
    y_pred_acc = y_pred.numpy()


    y_pred_acc = y_pred_acc.flatten()


    index_acc=np.argmax(y_pred_acc.reshape((len(y_pred_acc) // 4, 4)), axis=1)
    index_acc+=np.arange(0,4*len(index_acc),4)
    # print(index_acc[0:10])
    y_pred_acc = np.zeros_like(y_pred_acc)
    y_pred_acc[index_acc] = 1
    y_pred_acc = y_pred_acc.reshape((len(y_pred_acc) // 4, 4))



    y_true_acc = y_true_acc.reshape((y_true_acc.shape[0]*y_true_acc.shape[1], 4))



    # print(y_pred_acc[0:2])
    t = np.sum(abs(y_pred_acc - y_true_acc), axis=1)


    cnt = len(np.nonzero(t)[0])


    cnt_s = len(t)

    return (cnt_s - cnt) / cnt_s


def accNo(y_true, y_pred):
    y_true_accNo = y_true.numpy()
    y_pred_accNo = y_pred.numpy()
    y_true_No = y_true_accNo[y_true_accNo[:, :, 0] == 1]
    y_pred_No = y_pred_accNo[y_true_accNo[:, :, 0] == 1]

    # y_pred_No = y_pred_No.flatten()
    # y_true_No = y_true_No.flatten()
    index_acc_No = np.argmax(y_pred_No, axis=1)
    index_acc_No += np.arange(0, 4 * len(index_acc_No), 4)
    # print(index_acc[0:10])
    y_pred_No = y_pred_No.flatten()
    y_pred_No = np.zeros_like(y_pred_No)
    y_pred_No[index_acc_No] = 1
    y_pred_No = y_pred_No.reshape((len(y_pred_No) // 4, 4))
    # y_pred_No[y_pred_No >= 0.5] = 1
    # y_pred_No[y_pred_No < 0.5] = 0

    # y_true_No = y_true_No.reshape((len(y_true_No) // 4, 4))
    # y_pred_No = y_pred_No.reshape((len(y_pred_No) // 4, 4))
    t_No = np.sum(abs(y_pred_No - y_true_No), axis=1)

    cnts_No = len(np.nonzero(t_No)[0])

    cnt_ssNo = len(t_No)

    if cnt_ssNo == 0:
        return 0
    else:
        return (cnt_ssNo - cnts_No) / cnt_ssNo

def accN(y_true, y_pred):
    y_true_accN = y_true.numpy()
    y_pred_accN = y_pred.numpy()
    y_true_N = y_true_accN[y_true_accN[:, :, 1] == 1]
    y_pred_N = y_pred_accN[y_true_accN[:, :, 1] == 1]

    # y_pred_No = y_pred_No.flatten()
    # y_true_No = y_true_No.flatten()
    index_acc_N = np.argmax(y_pred_N, axis=1)
    index_acc_N += np.arange(0, 4 * len(index_acc_N), 4)
    # print(index_acc[0:10])
    y_pred_N = y_pred_N.flatten()
    y_pred_N = np.zeros_like(y_pred_N)
    y_pred_N[index_acc_N] = 1
    y_pred_N = y_pred_N.reshape((len(y_pred_N) // 4, 4))
    # y_pred_N[y_pred_N >= 0.5] = 1
    # y_pred_No[y_pred_No < 0.5] = 0

    # y_true_No = y_true_No.reshape((len(y_true_No) // 4, 4))
    # y_pred_No = y_pred_No.reshape((len(y_pred_No) // 4, 4))
    t_N = np.sum(abs(y_pred_N - y_true_N), axis=1)

    cnts_N = len(np.nonzero(t_N)[0])

    cnt_ssN = len(t_N)

    if cnt_ssN == 0:
        return 0
    else:
        return (cnt_ssN - cnts_N) / cnt_ssN

def accS(y_true, y_pred):
    y_true_accS = y_true.numpy()
    y_pred_accS = y_pred.numpy()
    y_true_S = y_true_accS[y_true_accS[:, :, 2] == 1]
    y_pred_S = y_pred_accS[y_true_accS[:, :, 2] == 1]

    # y_pred_No = y_pred_No.flatten()
    # y_true_No = y_true_No.flatten()
    index_acc_S = np.argmax(y_pred_S, axis=1)
    index_acc_S += np.arange(0, 4 * len(index_acc_S), 4)
    # print(index_acc[0:10])
    y_pred_S = y_pred_S.flatten()
    y_pred_S = np.zeros_like(y_pred_S)
    y_pred_S[index_acc_S] = 1
    y_pred_S = y_pred_S.reshape((len(y_pred_S) // 4, 4))
    # y_pred_No[y_pred_No >= 0.5] = 1
    # y_pred_No[y_pred_No < 0.5] = 0

    # y_true_No = y_true_No.reshape((len(y_true_No) // 4, 4))
    # y_pred_No = y_pred_No.reshape((len(y_pred_No) // 4, 4))
    t_S = np.sum(abs(y_pred_S - y_true_S), axis=1)

    cnts_S = len(np.nonzero(t_S)[0])

    cnt_ssS = len(t_S)

    if cnt_ssS == 0:
        return 0
    else:
        return (cnt_ssS - cnts_S) / cnt_ssS

def accV(y_true, y_pred):
    y_true_accV = y_true.numpy()
    y_pred_accV = y_pred.numpy()
    y_true_V = y_true_accV[y_true_accV[:, :, 3] == 1]
    y_pred_V = y_pred_accV[y_true_accV[:, :, 3] == 1]

    # y_pred_No = y_pred_No.flatten()
    # y_true_No = y_true_No.flatten()
    index_acc_V = np.argmax(y_pred_V, axis=1)
    index_acc_V += np.arange(0, 4 * len(index_acc_V), 4)
    # print(index_acc[0:10])
    y_pred_V = y_pred_V.flatten()
    y_pred_V = np.zeros_like(y_pred_V)
    y_pred_V[index_acc_V] = 1
    y_pred_V = y_pred_V.reshape((len(y_pred_V) // 4, 4))
    # y_pred_V[y_pred_No >= 0.5] = 1
    # y_pred_No[y_pred_No < 0.5] = 0

    # y_true_No = y_true_No.reshape((len(y_true_No) // 4, 4))
    # y_pred_No = y_pred_No.reshape((len(y_pred_No) // 4, 4))
    t_V = np.sum(abs(y_pred_V - y_true_V), axis=1)

    cnts_V = len(np.nonzero(t_V)[0])

    cnt_ssV = len(t_V)

    if cnt_ssV == 0:
        return 0
    else:
        return (cnt_ssV - cnts_V) / cnt_ssV





def No(y_true, y_pred):
    y_true_cntNo = y_true.numpy()
    y_pred_cntNo = y_pred.numpy()
    y_true_No = y_true_cntNo[y_true_cntNo[:, :, 0] == 1]

    y_true_N = y_true_cntNo[y_true_cntNo[:, :, 1] == 1]

    y_true_S = y_true_cntNo[y_true_cntNo[:, :, 2] == 1]

    y_true_V = y_true_cntNo[y_true_cntNo[:, :, 3] == 1]

    return len(y_true_No) / (len(y_true_No) + len(y_true_N) + len(y_true_S) + len(y_true_V))


def N(y_true, y_pred):
    y_true_cntNo = y_true.numpy()
    y_pred_cntNo = y_pred.numpy()
    y_true_No = y_true_cntNo[y_true_cntNo[:, :, 0] == 1]

    y_true_N = y_true_cntNo[y_true_cntNo[:, :, 1] == 1]

    y_true_S = y_true_cntNo[y_true_cntNo[:, :, 2] == 1]

    y_true_V = y_true_cntNo[y_true_cntNo[:, :, 3] == 1]

    return len(y_true_N) / (len(y_true_No) + len(y_true_N) + len(y_true_S) + len(y_true_V))


def S(y_true, y_pred):
    y_true_cntNo = y_true.numpy()
    y_pred_cntNo = y_pred.numpy()
    y_true_No = y_true_cntNo[y_true_cntNo[:, :, 0] == 1]

    y_true_N = y_true_cntNo[y_true_cntNo[:, :, 1] == 1]

    y_true_S = y_true_cntNo[y_true_cntNo[:, :, 2] == 1]

    y_true_V = y_true_cntNo[y_true_cntNo[:, :, 3] == 1]

    return len(y_true_S) / (len(y_true_No) + len(y_true_N) + len(y_true_S) + len(y_true_V))


def V(y_true, y_pred):
    y_true_cntNo = y_true.numpy()
    y_pred_cntNo = y_pred.numpy()
    y_true_No = y_true_cntNo[y_true_cntNo[:, :, 0] == 1]

    y_true_N = y_true_cntNo[y_true_cntNo[:, :, 1] == 1]

    y_true_S = y_true_cntNo[y_true_cntNo[:, :, 2] == 1]

    y_true_V = y_true_cntNo[y_true_cntNo[:, :, 3] == 1]
    # print(y_true_V)
    return len(y_true_V) / (len(y_true_No) + len(y_true_N) + len(y_true_S) + len(y_true_V))



# # np.save("numpy_file/input_data_mobilenet_gray.npy", input_data)
input_data = np.load("/content/drive/MyDrive/Canup/input_data_mobilenet.npy")
# input_data= np.load("numpy_file/input_data_mobilenet_gray.npy")
label_data = np.load("/content/drive/MyDrive/Canup/label_mobilenet_4.npy")
# # class_weight = {0: 2145212,1: 323393,2: 5808, 3: 10087}
# class_weight = {0: 1, 1: 6.633,2: 369.355, 3: 212.67}
a = 2484522 / (4 * (1501648 + 643564))
b = 2484522 / (4 * (226386 + 97029))
c = 2484522 / (4 * (4046 + 1762))
d = 2484522 / (4 * (7037 + 3050))
class_weight = {0: a, 1: b, 2: c, 3: d}



ratio = 0.7
data_length = len(input_data)
while (True):
    indices = list(range(data_length))
    random.shuffle(indices)
    input_data = input_data[indices]
    label_data = label_data[indices]
    train_data = input_data[:int(data_length * ratio)]
    train_label = label_data[:int(data_length * ratio)]
    valid_data = input_data[int(data_length * ratio):]
    valid_label = label_data[int(data_length * ratio):]
    nNo_train = len(train_label[(train_label[:, :, 0] == 1)])
    nN_train = len(train_label[(train_label[:, :, 1] != 0)])
    nS_train = len(train_label[(train_label[:, :, 2] != 0)])
    nV_train = len(train_label[(train_label[:, :, 3] != 0)])
    nNo_valid = len(valid_label[(valid_label[:, :, 0] == 1)])
    nN_valid = len(valid_label[(valid_label[:, :, 1] != 0)])
    nS_valid = len(valid_label[(valid_label[:, :, 2] != 0)])
    nV_valid = len(valid_label[(valid_label[:, :, 3] != 0)])
    print("nNo_train=", nNo_train)
    print("nN_train=", nN_train)
    print("nS_train=", nS_train)
    print("nV_train=", nV_train)
    print("nNo_valid=", nNo_valid)
    print("nN_valid=", nN_valid)
    print("nS_valid=", nS_valid)
    print("nV_valid=", nV_valid)
    print("nNo_ratio=", nNo_train / nNo_valid)
    print("nN_ratio=", nN_train / nN_valid)
    print("nS_ratio=", nS_train / nS_valid)
    print("nV_ratio=", nV_train / nV_valid)
    if check(nNo_train / nNo_valid) and check(nN_train / nN_valid) and check(nS_train / nS_valid) and check(
            nV_train / nV_valid):
        break
model = tf.keras.models.load_model("/content/drive/MyDrive/Canup/mobile.h5")
model.summary()
# model.summary()
print(len(model.layers))
model_body = tf.keras.Model(inputs=model.input, outputs=model.layers[-1].output)


classifier_head1 = tf.keras.layers.Dense(8000, activation="relu", name='Denseaf1')(
    model_body.layers[-1].output)
classifier_head2 = tf.keras.layers.Reshape((100, 80))(classifier_head1)
classifier_head2b = tf.keras.layers.Dense(400, activation="relu" , name='Denseaf2')(
    classifier_head2)
classifier_head2c = tf.keras.layers.Dense(120, activation="relu" , name='Denseaf3')(
    classifier_head2b)
# classifier_head2d = tf.keras.layers.Reshape((100, 10))(classifier_head2c)
classifier_head3 = tf.keras.layers.Dense(80, activation="relu" , name='Denseaf4')(
    classifier_head2c)
classifier_head4 = tf.keras.layers.Dense(40, activation="relu" , name='Denseaf5')(
    classifier_head3)
classifier_head5 = tf.keras.layers.Dense(10, activation="relu", name='Denseaf6' )(
    classifier_head4)
classifier_head6 = tf.keras.layers.Dense(4, activation="softmax", name='Denseafn')(
    classifier_head5)






# final_model = tf.keras.Model(model_body.input, classifier_head6)
final_model = tf.keras.models.load_model("/content/drive/MyDrive/Canup/model_mobilenet_v5.h5", compile=False)



final_model.summary()
print(len(final_model.layers))
for i in range(100):
    if i >= 92:
        final_model.layers[i].trainable = True
    else:
        final_model.layers[i].trainable = False

METRICS = [
    acc, accNo, accN, accS, accV, No, N, S, V, custom_loss3
    # acc, accNo, accN, accS, accV, custom_loss3
    # custom_losstest
]
final_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=custom_loss3,
    # loss='MeanSquaredError',
    metrics=METRICS,
    run_eagerly=True
)

filepath = "/content/drive/MyDrive/Canup/model_at_epoch_{epoch}.hdf5"

checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath, monitor='acc', verbose=1, save_best_only=False, mode='auto', period=5)

def scheduler(epoch, lr):
    if epoch < 100:
        return lr
    else:
        return lr * tf.math.exp(-0.1)


callbacks = [
    # tf.keras.callbacks.EarlyStopping(verbose=1, patience=25),
    tf.keras.callbacks.LearningRateScheduler(scheduler),
    checkpoint
]
EPOCHS = 100
history = final_model.fit(
    train_data,
    train_label,
    validation_data=(valid_data, valid_label),
    shuffle=True,
    batch_size=64,
    epochs=EPOCHS,
    # class_weight=class_weight,
    callbacks=callbacks,
)
final_model.save("/content/drive/MyDrive/Canup/model_mobilenet_v6.h5")