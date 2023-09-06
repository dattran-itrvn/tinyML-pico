# tinyML-pico
This project is simply an evaluation of using Python to develop tinyML applications on Pico. I will experiment with the environmental sound recognition application first.
Next, I will investigate it with ECG signals. I plan to develop an algorithm for detecting arrhythmias.

## Report
* Report 1: https://itrvn-my.sharepoint.com/:w:/p/thaotranxuan/EZy9URIR1ihGu8vKa7bEbgIByuL0RtL9szsglPBRjLo5nw?e=YcerPR
* Report 2: https://itrvn-my.sharepoint.com/:w:/p/thaotranxuan/EUTb9kPtj5dLshO7KfdEpSoBGB6fEp8FJV79jw-q_mLZSQ?e=K0iuhP
* Report 3: https://itrvn-my.sharepoint.com/:w:/p/thaotranxuan/EUdci5uDS1dEh7N75DrTzgMBBgWa3LB7W_kvTx7CQUU0Lg?e=Y39ykd

## Trainning
[preprocess.py](preprocess.py) to preprocess MITBIH database

There are 2 options:
+ Train with Normal spectrogram: [Norm_train](Norm_train)
    - Trainning file [Norm_train.py](Norm_train%2FNorm_train.py) 
    - Generating annotation [bxb.py](Norm_train%2Fbxb.py)
    - Report from bxb [Out1.out](Norm_train%2FOut1.out)
    - [constantQ](Norm_train%2FconstantQ) folder to norm spectrogram
  
![img.png](Norm_train%2Fimg.png)

+ Train without Normal spectrogram: [Origin_train](Origin_train)
    - Trainning file  [origin_train.py](Origin_train%2Forigin_train.py)
    - Generating annotation [bxb.py](Origin_train%2Fbxb.py)
    - Report from bxb [Out1.out](Origin_train%2FOut1.out)

![img.png](Origin_train%2Fimg.png)

In Train without Normal option, we have three versions:
![img.png](image%2Fimg.png)
+ Origin model, whose data is "labeled" 1 at the exactly area including the R peek
+ 2nd version model, whose data is "labeled" 1 at:
    - the area includes the R peek being not at the first sample in this area
    - the area before the one including the R peek being at the first sample in this area
+ 3rd version model, whose spectrogram will overlap 1 area among 2 5-second buffers

The bxb result of three version model: [Results_bxb](Results_bxb)
  