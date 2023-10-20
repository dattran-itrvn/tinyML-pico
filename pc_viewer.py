import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import serial

ser = serial.Serial('COM3')

fig = plt.figure(figsize=(1, 2))
viewer = fig.add_subplot(111)
plt.ion() # Turns interactive mode on (probably unnecessary)
fig.show() # Initially shows the figure

while True:
    
    data = ser.readline().decode("utf-8")
    if data[0] != '[':
        continue

    header = data[:15]
    img = data[16:]
    bitmap = list(map(int, img.split(" ")))
    print(header)
    xdim = int(header[1:4])
    ydim = int(header[5:8])
    print("{}x{}".format(xdim, ydim))
    im = Image.new("RGB",(xdim,ydim))
    i = 0
    for y in range(ydim):
        for x in range(xdim):
            px = bitmap[i]
            i = i+1
            im.putpixel((x,y),((px&0xF800) >> 8, (px&0x07E0) >> 3, (px&0x001F) << 3))

    viewer.clear() # Clears the previous image
    viewer.imshow(im) # Loads the new image
    plt.pause(.1) # Delay in seconds
    fig.canvas.draw() # Draws the image to the screen

