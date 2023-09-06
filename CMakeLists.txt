cmake_minimum_required(VERSION 3.12)

# initialize pico_sdk from GIT
# (note this can come from environment, CMake cache etc)
# set(PICO_SDK_FETCH_FROM_GIT on)
set(ENV{PICO_SDK_PATH} "/home/ttb/raspberry-pi-pico/pico/pico-sdk")

# pico_sdk_import.cmake is a single file copied from this SDK
# note: this must happen before project()
include(pico_sdk_import.cmake)

project(pico_tinyML)

# initialize the Pico SDK
pico_sdk_init()

# Define ARM_CPU, CMSIS ROOT and DSP to use CMSIS-DSP
set(ARM_CPU "cortex-m0plus")
set(ROOT ${CMAKE_CURRENT_LIST_DIR}/lib/CMSIS_5)
set(DSP ${ROOT}/CMSIS/DSP)

set(CONFIGTABLE ON)
set(RFFT_Q15_256 ON)
set(ALLFAST ON)

# include CMSIS-DSP .cmake for GCC Toolchain
include(${DSP}/Toolchain/GCC.cmake)

# add CMSIS-DSP Source directory as subdirectory
add_subdirectory(${DSP}/Source EXCLUDE_FROM_ALL)

# rest of your project
add_executable(pico_tinyML
    ${CMAKE_CURRENT_LIST_DIR}/src/main.cpp
    ${CMAKE_CURRENT_LIST_DIR}/dsp/dsp_pipeline.cpp
    ${CMAKE_CURRENT_LIST_DIR}/model/ml_model.cpp
    ${CMAKE_CURRENT_LIST_DIR}/i2s_mic/i2s_microphone.cpp
)

target_link_libraries(pico_tinyML
    pico_stdlib
    pico-tflmicro
    hardware_pio
    hardware_gpio
    hardware_irq
    hardware_dma
    CMSISDSPTransform CMSISDSPSupport CMSISDSPCommon CMSISDSPComplexMath CMSISDSPFastMath CMSISDSPBasicMath
)

target_compile_options(pico_tinyML PUBLIC
    -Wno-error=shadow
    -Wno-error=cast-align
    -Wno-error=cast-qual
    -Wno-error=redundant-decls
    -Wno-error=sign-conversion
    -Wno-error=conversion
    -Wno-error=sign-compare
    -Wno-error=unused-function
)

# enable usb output, disable uart output
pico_enable_stdio_usb(pico_tinyML 1)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(pico_tinyML)

add_subdirectory("lib/pico-tflmicro" EXCLUDE_FROM_ALL)