# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""
Capture an image from the camera and display it on a supported LCD.
"""
import sys
import time

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

cam.size = OV7670_SIZE_DIV8
cam.colorspace = OV7670_COLOR_YUV
cam.flip_y = True

buf = bytearray(2 * cam.width * cam.height)
chars = b" .:-=+*#%@"
6
width = cam.width
row = bytearray(2 * width)

sys.stdout.write("\033[2J")

while True:
    cam.capture(buf)
    for j in range(cam.height):
        sys.stdout.write(f"\033[{j}H")
        for i in range(cam.width):
            row[i * 2] = row[i * 2 + 1] = chars[
                buf[2 * (width * j + i)] * (len(chars) - 1) // 255
            ]
        sys.stdout.write(row)
        sys.stdout.write("\033[K")
        sys.stdout.write('\n')
    sys.stdout.write("\033[J")
    time.sleep(0.02)