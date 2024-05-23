### Install CMake (at least version 3.13), and GCC cross compiler
```
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
```
### Set up your project to point to use the Raspberry Pi Pico SDK by cloning the SDK locally:

```
git clone https://github.com/raspberrypi/pico-sdk.git

cd pico-sdk
git submodule update --init

```
### Board configuration
I use the Pico Camera PCB from ITRVN.COM\
And using board configuration from **./pico-sdk/src/boards/include/boards/pico.h**\
W25Q16JVSNIQ - 16 Mbit - 2 MByte
```
#define PICO_BOOT_STAGE2_CHOOSE_GENERIC_03H 1

#ifndef PICO_FLASH_SPI_CLKDIV
#define PICO_FLASH_SPI_CLKDIV 4
#endif

#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (2 * 1024 * 1024)
#endif
```

