
import csv
import numpy as np
import wfdb
from matplotlib import pyplot as plt
from preprocess import preprocess_data
from define import *
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.styles import Font
import wfdb
import scipy.signal as signal
from scipy.signal import butter, filtfilt, lfilter, iirnotch


def butter_lowpass(cutoff, fs, order=3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=3):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def butter_highpass(cutoff, fs, order=3):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def butter_highpass_filter(data, cutoff, fs, order=3):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y


def find_max_locate(ecg_array):
    arr = ecg_array
    y_i = np.amax(arr)
    i_1, = np.where(arr == y_i)
    x_i = i_1[0]
    return y_i, i_1, x_i


def derivative_filter(fs):
    if fs != 200:
        int_c = (4 - 0) / (fs * (1 / 40))
        x = np.arange(0, 4)
        xp = np.array([1, 2, 0, -2, -1]) * (1 / 8) * fs
        fp = np.linspace(0, int_c, 5)  # mang 5 gia tri buoc nhay int_c
        b = np.interp(x, xp, fp)  # 1-D data interpolation (trả về mảng 1 chiều nội suy)b = np.interp(x, xp, fp)
    else:
        b = np.array([1, 2, 0, -2, -1]) * (1 / 8) * fs
    return b



def pan_tompkin(ecg, fs):
    qrs_c = []  # np.zeros(shape=(1,1)) # amplitude of R
    qrs_i = []  # index
    # SIG_LEV = 0
    nois_c = []
    nois_i = []
    # delay = 0
    # skip = 0
    # not_nois = 0
    # selected_RR = []
    m_selected_RR = 0
    mean_RR = 0
    qrs_i_raw = []
    qrs_amp_raw = []
    ser_back = []
    ecg = np.nan_to_num(ecg)
    if (fs == 200):
        ecg = ecg - np.mean(ecg)  # remove mean of Signal
        # Low pass filter
        ecg_l = butter_lowpass_filter(data=ecg, cutoff_low=12, fs=fs, order=3)
        ecg_l = ecg_l / (np.max(abs(ecg_l)))
        # Highpass filter
        ecg_h = butter_highpass_filter(data=ecg_l, cutoff_high=5, fs=fs, order=3)
        ecg_h = ecg_h / np.max(abs(ecg_h))
    else:
        # Bandpass filter for Noise cancelation of other sampling frequencies(Filtering)
        ecg_h = butter_bandpass_filter(data=ecg, lowcut=5, highcut=15, fs=fs, order=3)
        ecg_h = ecg_h / np.max(abs(ecg_h))

    # Derivative filter H(z) = (1/8T)(-z^(-2) - 2z^(-1) + 2z + z^(2))#######################
    b = derivative_filter(fs)
    ecg_d = signal.filtfilt(b, 1, ecg_h)
    ecg_d = ecg_d / np.max(ecg_d)

    # Squaring nonlinearly enhance the dominant peaks
    ecg_s = ecg_d ** 2
    # plt.plot(ecg_s)
    # Moving average Y(nt) = (1/N)[x(nT-(N - 1)T)+ x(nT - (N - 2)T)+...+x(nT)]
    window_len = round(0.150 * fs)
    if window_len % 2 == 0:
        window_len += 1
    s = np.r_[
        ecg_s[window_len - 1:0:-1], ecg_s, ecg_s[-2:-window_len - 1:-1]]  # add element into a array. ex.between ecg_s
    ecg_m = np.convolve(s, np.ones(window_len), mode='valid') / round(0.150 * fs)
    ecg_m = ecg_m[int(window_len / 2):-int(window_len / 2)]

    # Find all peaks in ecg signal
    # ecg_m[ecg_m < 0.0001] = 0
    # locs = peakutils.indexes(ecg_m, thres=0.5, min_dist=fs*0.2)
    locs = signal.find_peaks(ecg_m, threshold=0.00000000001, distance=fs * 0.22)[0]
    pks = ecg_m[locs]
    # plt.plot(ecg_m)
    # plt.show()
    # Initialize the training phase (2 seconds of the signal) to determine the THR_SIG and THR_NOISE
    THR_SIG = (np.max(ecg_m[0:2 * fs])) * 1 / 3  # 0.25 of the max amplitude
    THR_NOISE = (np.mean(ecg_m[0:2 * fs])) * 1 / 2  # 0.5 of the mean signal is considered to be noise
    SIG_LEV = THR_SIG
    NOISE_LEV = THR_NOISE
    # Initialize bandpass filter threshold(2 seconds of the bandpass signal)
    THR_SIG1 = (np.max(ecg_h[0:2 * fs])) * 1 / 3
    THR_NOISE1 = (np.mean(ecg_h[0:2 * fs])) * 1 / 2
    SIG_LEV1 = THR_SIG1
    NOISE_LEV1 = THR_NOISE1

    for i in range(0, len(pks)):
        # locate the corresponding peak in the filtered signal
        if (locs[i] - int(round(0.150 * fs))) >= 1 and locs[i] <= len(ecg_h) - 1:
            y_i, i_l, x_i = find_max_locate(ecg_h[(locs[i] - int(round(0.150 * fs))):(locs[i])])
        else:
            if i == 0:
                y_i, i_1, x_i = find_max_locate(ecg_h[0:locs[i]])
                ser_back = 1
            elif locs[i] >= len(ecg_h):
                y_i, i_2, x_i = find_max_locate(ecg_h[(locs[i] - round(0.150 * fs)):-1])

        # update the number of beats (Two heart rate means one the most recent and the other selector)
        x = len(qrs_c)
        # calculate the mean of the last 8 R waves to make sure that QRS is not
        # missing(If no R detected, trigger a search back) 1.66*mean
        if x >= 9:
            x1 = np.asarray(qrs_i[x - 9: x])
            diffRR = np.diff(x1)  # calculate RR interval
            mean_RR = np.mean(diffRR)  # calculater the mean of 8 previous R waves interval
            comp = qrs_i[-1] - qrs_i[-2]  # lastest RR
            if comp <= 0.92 * mean_RR or comp >= 1.16 * mean_RR:  # most recent RR interval that fell between the accpetable low and high RR-interval limits
                # lower down thresholds to detect better in MVI
                THR_SIG = 0.5 * (THR_SIG)
                # lower down thresholds to detect better in Bandpass filtered
                THR_SIG1 = 0.5 * (THR_SIG1)
            else:
                m_selected_RR = mean_RR  # the lastest regular beats mean

        if m_selected_RR:
            test_m = m_selected_RR  # if the regular RR available use it
        elif mean_RR and m_selected_RR == 0:
            test_m = mean_RR
        else:
            test_m = 0

        if test_m:
            if ((locs[i] - qrs_i[-1]) >= round(1.66 * test_m)):  # it shows a QRS is missed
                try:
                    pks_temp, i_3, locs_temp = find_max_locate(
                        ecg_m[(qrs_i[-1] + round(0.2 * fs)):(locs[i] - round(0.2 * fs))])
                except Exception as e:
                    print("{} get error: {}".format(i, e))
                locs_temp = qrs_i[-1] + round(0.2 * fs) + locs_temp - 1  # location
                if pks_temp > THR_NOISE:
                    qrs_c.append(pks_temp)
                    qrs_i.append(locs_temp)
                # find the location in filtered sig
                if locs_temp <= len(ecg_h):
                    y_i_t, i_4, x_i_t = find_max_locate(ecg_h[(locs_temp - round(0.150 * fs)):locs_temp])
                else:
                    y_i_t, i_5, x_i_t = find_max_locate(ecg_h[(locs_temp - round(0.150 * fs)):locs_temp])
                # take care of bandpass signal threshold
                if y_i_t > THR_NOISE1:
                    qrs_i_raw.append(locs_temp - round(0.150 * fs) + (x_i_t - 1))  # save index of bandpass
                    qrs_amp_raw.append(y_i_t)  # save amplitude of bandpass
                    SIG_LEV1 = 0.25 * y_i_t + 0.75 * SIG_LEV1  # when found with the second thres

                not_nois = 1
                SIG_LEV = 0.25 * pks_temp + 0.75 * SIG_LEV
            else:
                not_nois = 0

        # find noise and QRS peaks
        if pks[i] >= THR_SIG:
            # if a QRS candidate occurs within 360ms of the previous QRS
            # the algorithm determines if its T wave or QRS
            skip = 0
            if len(qrs_c) >= 3:
                if (locs[i] - qrs_i[-1]) <= round(0.3600 * fs):
                    Slope1 = np.mean(np.diff(
                        ecg_m[locs[i] - round(0.075 * fs):locs[i]]))  # mean slope of the waveform at that position
                    Slope2 = np.mean(
                        np.diff(ecg_m[(qrs_i[-1] - round(0.075 * fs)): qrs_i[-1]]))  # mean slope of previous R wave
                    if abs(Slope1) <= abs(0.5 * Slope2):  # slope less then 0.5 of previous R
                        nois_c.append(pks[i])
                        nois_i.append(locs[i])
                        skip = 1  # T wave identification
                        # adjust noise level in both filtered and MVI
                        NOISE_LEV1 = 0.125 * y_i + 0.875 * NOISE_LEV1
                        NOISE_LEV = 0.125 * pks[i] + 0.875 * NOISE_LEV
                    # else:
                    #     skip = 0
            if skip == 0:  # skip is 1 when a T wave is detected
                qrs_c.append(pks[i])
                qrs_i.append(locs[i])
                # bandpass filter check threshold
                if y_i >= THR_SIG1:
                    if ser_back:
                        qrs_i_raw.append(x_i)
                    else:
                        qrs_i_raw.append(locs[i] - round(0.150 * fs) + (x_i - 1))
                qrs_amp_raw.append(y_i)  # save amplitude of bandpass
                SIG_LEV1 = 0.125 * y_i + 0.875 * SIG_LEV1  # adjust threshold for bandpass filtered sig

            # adjust Signal level
            SIG_LEV = 0.125 * pks[i] + 0.875 * SIG_LEV

        elif (THR_NOISE <= pks[i]) and (pks[i] < THR_SIG):
            # adjust Noise level in filtered sig
            NOISE_LEV1 = 0.125 * y_i + 0.875 * NOISE_LEV1
            # adjust Noise level in MVI
            NOISE_LEV = 0.125 * pks[i] + 0.875 * NOISE_LEV

        elif pks[i] < THR_NOISE:
            nois_c.append(pks[i])
            nois_i.append(locs[i])
            NOISE_LEV1 = 0.125 * y_i + 0.875 * NOISE_LEV1
            NOISE_LEV = 0.125 * pks[i] + 0.875 * NOISE_LEV

        # adjust the threshold with SNR
        if NOISE_LEV != 0 or SIG_LEV != 0:
            THR_SIG = NOISE_LEV + 0.25 * (abs(SIG_LEV - NOISE_LEV))
            THR_NOISE = 0.5 * (THR_SIG)

        # adjust the threshold with SNR for bandpassed signal
        if NOISE_LEV1 != 0 or SIG_LEV1 != 0:
            THR_SIG1 = NOISE_LEV1 + 0.25 * (abs(SIG_LEV1 - THR_NOISE1))
            THR_NOISE1 = 0.5 * (THR_SIG1)

    skip = 0  # reset parameters
    not_nois = 0  # reset parameters
    ser_back = 0  # reset bandpass param

    symbol = []
    for i in range(0, len(qrs_i)):
        symbol.append('N')
    # locs1 = []
    # for e in locs:
    #     locs1.append(e)

    qrs_i1 = []
    for e in qrs_i:
        qrs_i1.append(e - 0)
    # print('length beats_detection: ', len(qrs_i1))
    # print('beats_detection:', qrs_i1)
    return qrs_i1, symbol


def checkPTK(DIR, namefile):
        record = wfdb.rdrecord(DIR + str(namefile))
        ecg_o = record.p_signal[:, 0]
        d_ptk_bts, symbol_ptk = pan_tompkin(ecg_o, fs=record.fs)

        ecg, beats, sym = preprocess_data(DIR + str(namefile) + '.hea')
        bts = np.zeros_like(beats)
        print(namefile)
        for i in range(len(beats)):
            if ecg[beats[i]] < 0:
                # print(i, ' ', 1)
                bts[i] = np.argmax(
                    -(ecg[beats[i] - int(FREQUENCY_SAMPLING * BXB_WIN):beats[i] + int(FREQUENCY_SAMPLING * BXB_WIN)])) + \
                         beats[i] - int(FREQUENCY_SAMPLING * BXB_WIN)
            else:
                bts[i] = np.argmax(
                    (ecg[beats[i] - int(FREQUENCY_SAMPLING * BXB_WIN):beats[i] + int(FREQUENCY_SAMPLING * BXB_WIN)])) + \
                         beats[i] - int(FREQUENCY_SAMPLING * BXB_WIN)
                # print(i, ' ', 2)
        l_btss = len(d_ptk_bts)
        top = 0
        bot = 0
        if d_ptk_bts[0] - 30 < 0:
            l_btss -= 1
            symbol_ptk = symbol_ptk[1:]
            top = 1
        if d_ptk_bts[-1] + 30 > len(ecg):
            l_btss -= 1
            symbol_ptk = symbol_ptk[:-1]
            bot = 1
        btss = np.zeros(l_btss, dtype='int64')

        for j in range(len(d_ptk_bts) - bot - top):
            btss[j] = np.argmax(abs(ecg[d_ptk_bts[j + top] - 30:d_ptk_bts[j + top] + 30])) + d_ptk_bts[j + top] - 30

        sym[(sym == 'N') | (sym == 'L') | (sym == 'R') | (sym == 'e') | (sym == 'j')] = 'N'
        sym[(sym == 'A') | (sym == 'a') | (sym == 'J') | (sym == 'S')] = 'N'
        sym[(sym == 'V') | (sym == 'e')] = 'N'
        sym[(sym == 'f') | (sym == 'Q') | (sym == 'F')] = 'N'

        symidx = np.zeros(len(sym))
        nondata = sym.copy()
        nondata[:] = ' '
        symidx[sym != 'N'] = 1

        detectsym2 = np.array(symbol_ptk.copy())
        detectsym2[:2] = 'N'
        detectsym2[-2:] = 'N'

        df = np.diff(np.array(btss))
        if df[0] < 200:
            df[0] = 200
        rr = [0]
        rr.extend(df)
        rr = np.array(rr)
        divba = np.zeros(len(btss))
        divba[1:-1] = df[:-1] / df[1:]


        # turn 2 detect SV

        minlocal1 = []
        minlocal2 = []
        QS2 = []
        QS5 = []
        QS8 = []
        diff_f2 = [0]
        diff_a2 = []
        diff_f5 = [0]
        diff_a5 = []
        diff_f8 = [0]
        diff_a8 = []
        diff_fm = [0]
        diff_am = []
        diff_tb = []
        # print(namefile)
        for i in range(len(btss)):
            # print(i)
            if ecg[btss[i]] >= 0:
                d = 1
            else:
                d = -1

            if btss[i] < 30:
                s1 = 0 + np.argmin(d * ecg[0:btss[i]])
            else:
                s1 = btss[i] - 30 + np.argmin(d * ecg[btss[i] - 30:btss[i]])

            if btss[i] > len(ecg) - 30:
                s2 = btss[i] + np.argmin(d * ecg[btss[i]:])
            else:
                s2 = btss[i] + np.argmin(d * ecg[btss[i]:btss[i] + 30])
            if ecg[s1] * ecg[s2] >= 0:
                if abs(ecg[s1]) > abs(ecg[s2]):
                    s12 = s1
                else:
                    s12 = s2
            else:
                if ecg[s1] * ecg[btss[i]] < 0:
                    s12 = s1
                else:
                    s12 = s2

            diff_tb.append(round(abs(ecg[btss][i] - ecg[s12]), 6))

            cnt = 0
            f = True
            while (ecg[btss[i] - cnt] * ecg[btss[i]] > 0):
                cnt += 1
                if btss[i] - cnt < 0 or cnt > 30:
                    minlocal1.append(btss[i] - cnt + 1)
                    f = False
                    break
            if f:
                minlocal1.append(btss[i] - cnt)
            cnt = 0
            f = True
            while (ecg[btss[i] + cnt] * ecg[btss[i]] > 0):
                cnt += 1
                if btss[i] + cnt > len(ecg) - 1 or cnt > 30:
                    minlocal2.append(btss[i] + cnt - 1)
                    f = False
                    break
            if f:
                minlocal2.append(btss[i] + cnt)
            # print(i)
            sRS = 0.8 * (ecg[btss[i]] - ecg[minlocal2[i]]) + ecg[minlocal2[i]]
            sQR = 0.8 * (ecg[btss[i]] - ecg[minlocal1[i]]) + ecg[minlocal1[i]]
            QS2.append(np.argmin(abs(ecg[btss[i]:minlocal2[i] + 1] - sRS)) + btss[i] - (
                    np.argmin(abs(ecg[minlocal1[i]:btss[i] + 1] - sQR)) + minlocal1[i]))

            sRS = 0.5 * (ecg[btss[i]] - ecg[minlocal2[i]]) + ecg[minlocal2[i]]
            sQR = 0.5 * (ecg[btss[i]] - ecg[minlocal1[i]]) + ecg[minlocal1[i]]
            QS5.append(np.argmin(abs(ecg[btss[i]:minlocal2[i] + 1] - sRS)) + btss[i] - (
                    np.argmin(abs(ecg[minlocal1[i]:btss[i] + 1] - sQR)) + minlocal1[i]))

            sRS = 0.2 * (ecg[btss[i]] - ecg[minlocal2[i]]) + ecg[minlocal2[i]]
            sQR = 0.2 * (ecg[btss[i]] - ecg[minlocal1[i]]) + ecg[minlocal1[i]]
            QS8.append(np.argmin(abs(ecg[btss[i]:minlocal2[i] + 1] - sRS)) + btss[i] - (
                    np.argmin(abs(ecg[minlocal1[i]:btss[i] + 1] - sQR)) + minlocal1[i]))
            if i > 0 and i < len(btss) - 1:
                diff_f2.append(round(abs((QS2[i] - QS2[i - 1]) / QS2[i - 1]), 6))
                diff_a2.append(round(abs((QS2[i - 1] - QS2[i]) / QS2[i]), 6))
                diff_f5.append(round(abs((QS5[i] - QS5[i - 1]) / QS5[i - 1]), 6))
                diff_a5.append(round(abs((QS5[i - 1] - QS5[i]) / QS5[i]), 6))
                diff_f8.append(round(abs((QS8[i] - QS8[i - 1]) / QS8[i - 1]), 6))
                diff_a8.append(round(abs((QS8[i - 1] - QS8[i]) / QS8[i]), 6))
                diff_fm.append(round((diff_f2[i] + diff_f5[i] + diff_f8[i]) / 3, 6))
                diff_am.append(round((diff_a2[i - 1] + diff_a5[i - 1] + diff_a8[i - 1]) / 3, 6))
            if i == len(btss) - 1:
                diff_a2.append(0)
                diff_a5.append(0)
                diff_a8.append(0)
                diff_am.append(0)


        # classify S and V
        QS2 = np.array(QS2)
        QS5 = np.array(QS5)
        QS8 = np.array(QS8)
        symbol_ptk_np = np.array(symbol_ptk)
        idx=0
        while (idx<len(btss)-1):
            if rr[idx+1] <= int(FREQUENCY_SAMPLING*0.2) and abs(ecg[btss[idx]] / ecg[btss[idx - 1]]) < 0.8 and abs(ecg[btss[idx]] / ecg[btss[idx + 1]]) < 0.8:
                btss = np.delete(btss,idx)
                df = np.diff(np.array(btss))
                rr = [0]
                rr.extend(df)
                rr = np.array(rr)
                symbol_ptk_np = np.delete(symbol_ptk_np,idx)
                continue
            if idx!=0 and rr[idx] <= int(FREQUENCY_SAMPLING*0.2) and abs(ecg[btss[idx]] / ecg[btss[idx - 1]]) < 0.8 and abs(ecg[btss[idx]] / ecg[btss[idx + 1]]) < 0.8:
                btss = np.delete(btss,idx)
                df = np.diff(np.array(btss))
                rr = [0]
                rr.extend(df)
                rr = np.array(rr)
                symbol_ptk_np = np.delete(symbol_ptk_np,idx)
                continue
            # if rr[idx] <= 100 and abs(ecg[btss[idx]] / ecg[btss[idx - 1]]) < 0.8 and abs(ecg[btss[idx]] / ecg[btss[idx + 1]]) < 0.8:
            #     btss = np.delete(btss,idx)
            #     rr = np.delete(rr,idx)
            #     symbol_ptk_np = np.delete(symbol_ptk_np,idx)
            #     continue
            idx+=1
        # for i in range(1,len(btss)-1):
        idx=1
        while (idx<len(btss)-1):
            if rr[idx] <= int(FREQUENCY_SAMPLING*0.2):
                btss = np.delete(btss,idx-1)
                df = np.diff(np.array(btss))
                rr = [0]
                rr.extend(df)
                rr = np.array(rr)
                symbol_ptk_np = np.delete(symbol_ptk_np,idx-1)
                continue

            idx+=1
       

        wfdb.wrann(record_name=str(namefile),
                   extension='atr',
                   sample=np.asarray(bts),
                   symbol=np.asarray(sym),
                   fs=360,
                   write_dir='PTK')

        wfdb.wrann(record_name=str(namefile),
                   extension='txt',
                   sample=np.asarray(btss),
                   symbol=np.asarray(symbol_ptk_np),
                   fs=360,
                   write_dir='PTK')

DATA_DIR_FOLDER = "C:/Users/AI-DEV/Downloads/mit-bih-arrhythmia-database-1.0.0/"
NOISE_DIR_FOLDER = "C:/Users/AI-DEV/Downloads/nstdb/nstdb/"
TRAIN_DATA_DIR_STR = [101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215,
                      220, 223, 230]
VALID_DATA_DIR_STR = [100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231,
                      232, 233, 234]

# if __name__ == "__main__":
#     a, b, c, d, e, f, g, h, err, expt = main(DATA_DIR_FOLDER, 101)
if __name__ == "__main__":
    for i in TRAIN_DATA_DIR_STR:
        checkPTK(DATA_DIR_FOLDER, i)
    for i in VALID_DATA_DIR_STR:
        checkPTK(DATA_DIR_FOLDER, i)
