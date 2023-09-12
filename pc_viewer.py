import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import serial

def get_img(width=255, height=255):
    data = np.arange(width * height, dtype=np.int64).reshape((height, width))
    img_data = np.empty((height, width, 3), dtype=np.uint8)
    img_data[:, :, 0] = data // height
    img_data[:, :, 1] = data % width
    img_data[:, :, 2] = 100
    return Image.fromarray(img_data)

# # display(get_img())
# imgplot = plt.imshow(get_img())
# plt.show()


ser = serial.Serial('COM3')
xdim = 160
ydim = 120
# xdim = 80
# ydim = 60

while True:
    im = Image.new("RGB",(xdim,ydim))
    data = ser.readline().decode("utf-8")
    if data[0] != '[':
        continue

    header = data[:15]
    img = data[16:]
    bitmap = list(map(int, img.split(" ")))
    print(header)
    # 160x120

    i = 0
    for y in range(ydim):
        for x in range(xdim):
            px = bitmap[i]
            i = i+1
            im.putpixel((x,y),((px&0xF800) >> 8, (px&0x07E0) >> 3, (px&0x001F) << 3))

    plt.imshow(im)
    plt.show()
    plt.clf() #will make the plot window empty
    im.close()

