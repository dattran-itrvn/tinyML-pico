cmake_minimum_required(VERSION 3.13)

set(FAMILY rp2040)

set(ENV{PICO_SDK_PATH} "/home/ttb/raspberry-pi-pico/pico/pico-sdk")

include(pico_sdk_import.cmake)
include(pico_extras_import.cmake)

project(pico_test)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# rest of your project
add_executable(main
               main.cpp
               Wav.cpp
               )

# Add pico_stdlib library which aggregates commonly used features
target_link_libraries(main
                      pico_stdlib
                      hardware_pio
                      hardware_gpio
                      hardware_irq
                      hardware_dma
                      pico_multicore
                      pico_unique_id
                      )

target_compile_options(main PUBLIC
                    -Wno-error=shadow
                    -Wno-error=cast-align
                    -Wno-error=cast-qual
                    -Wno-error=redundant-decls
                    -Wno-error=sign-conversion
                    -Wno-error=conversion
                    -Wno-error=sign-compare
                    -Wno-error=unused-function
                    )
                                

pico_enable_stdio_usb(main 1)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(main)
