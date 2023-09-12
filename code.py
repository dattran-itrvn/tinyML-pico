import sys
import time
from ulab import numpy as np
import board
import busio
import digitalio

from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV4,
    OV7670_SIZE_DIV8,
    OV7670_SIZE_DIV16,
    OV7670_COLOR_YUV,
    OV7670_TEST_PATTERN_COLOR_BAR_FADE,
)

# Ensure the camera is shut down, so that it releases the SDA/SCL lines,
# then create the configuration I2C bus

with digitalio.DigitalInOut(board.GP10) as reset:
    reset.switch_to_output(False)
    time.sleep(0.001)
    bus = busio.I2C(board.GP9, board.GP8)

# Set up the camera (you must customize this for your board!)
cam = OV7670(
    bus,
    data_pins=[
        board.GP12,
        board.GP13,
        board.GP14,
        board.GP15,
        board.GP16,
        board.GP17,
        board.GP18,
        board.GP19,
    ],  # [16]     [org] etc
    clock=board.GP11,  # [15]     [blk]
    vsync=board.GP7,  # [10]     [brn]
    href=board.GP21,  # [27/o14] [red]
    mclk=board.GP20,  # [16/o15]
    shutdown=None,
    reset=board.GP10,
)  # [14]

cam.size = OV7670_SIZE_DIV4

arr = np.zeros((cam.height, cam.width), dtype=np.uint16)
width = cam.width
height = cam.height
frame_id = 0
while True:
    cam.capture(arr)
    arr.byteswap(inplace=True)
    sys.stdout.write('[' + f'{width:03}' + 'x' + f'{height:03}' + '] ' + f'{frame_id:04}' + '$')
    for j in range(height):
        for i in range(width):
            pixel = arr[j, i]
            sys.stdout.write(' ' + str(pixel))
            
    sys.stdout.write('\n')
    time.sleep(0.02)
    frame_id += 1
    if frame_id >= 9999:
        frame_id = 0


