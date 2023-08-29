cmake_minimum_required(VERSION 3.12)

# initialize pico_sdk from GIT
# (note this can come from environment, CMake cache etc)
# set(PICO_SDK_FETCH_FROM_GIT on)
set(ENV{PICO_SDK_PATH} "/home/ttb/raspberry-pi-pico/pico/pico-sdk")

# pico_sdk_import.cmake is a single file copied from this SDK
# note: this must happen before project()
include(pico_sdk_import.cmake)

project(machine_i2s)

# initialize the Pico SDK
pico_sdk_init()

add_executable(machine_i2s
               src/main.c
               src/machine_i2s.c
               src/usb_descriptors.c
               src/usb_microphone.c
               )

target_link_libraries(machine_i2s
                      pico_stdlib
                      hardware_pio
                      hardware_gpio
                      hardware_irq
                      hardware_dma
                      pico_unique_id
                      tinyusb_device
                      tinyusb_board 
                      )

target_include_directories(machine_i2s PRIVATE src)

pico_enable_stdio_usb(machine_i2s 1)

pico_add_extra_outputs(machine_i2s)