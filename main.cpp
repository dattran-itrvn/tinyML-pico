#include "stdio.h"
#include "pico/stdlib.h"
#include "machine_i2s.c"
#include "hardware/gpio.h"
#include "Wav.h"

#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define UART_ID uart0

#define SCK 2
#define WS 3 // needs to be SCK +1
#define SD 6
#define BPS 16 
#define RATE 16000
#define LEN_WAVE_HEADER 44
#define TIME_RECORD 0.001

#define BUTTON 15

void init()
{
    stdio_init_all();
    gpio_init(BUTTON);
    gpio_set_dir(BUTTON, GPIO_IN);
    gpio_pull_up(BUTTON);
}

int main()
{
    uint8_t headerWave[LEN_WAVE_HEADER];
    uint32_t byteReads = 0;
    uint32_t countByte = 0;
    int16_t buffer, *data;
    uint32_t FIFO_BYTE = uint32_t(RATE * TIME_RECORD * BPS / 8);
    int16_t I2SBuf[FIFO_BYTE/2];
    uint8_t flag = 1;

    init();
    printf("Audio Test: ");
	machine_i2s_obj_t* i2s0 = machine_i2s_make_new(0, SCK, WS, SD, RX, BPS, MONO, SIZEOF_DMA_BUFFER_IN_BYTES, RATE);
    if(i2s0 == NULL){
        while (true){
            printf("ERROR\r\n");
            sleep_ms(1000);
        }
    }
    else{
        printf("OK\r\n");
    }

    printf("START RECORD\r\n");
    printf("\r\n");
    printf("----- START DATA -----\r\n");
    sleep_ms(500);

    // Read Data with Time
    // while (true)
    // {
    //     byteReads = machine_i2s_stream_read(i2s0, (void*)&I2SBuf, FIFO_BYTE);
    //     if(byteReads == FIFO_BYTE){
    //         for(int b = 0; b < FIFO_BYTE/2; b++){
    //             if (!(b % 32)){
    //                 printf("\r\n");
    //             }
    //             int16_t val = I2SBuf[b];
    //             printf("%02hX%02hX", (val & 0xFF), ((val >> 8) & 0xFF));
    //         }
    //         countByte += byteReads;
    //         if(!gpio_get(BUTTON)){
    //             printf("\r\n");
    //             printf("----- END DATA -----\r\n");
    //             break;
    //         }
    //     }
    // }

    // Read Data with FIFO
    while (true)
    {
        byteReads = machine_i2s_stream_read(i2s0, (void*)&buffer, 2);
        if (!(countByte % 32)){
            printf("\r\n");
        }
        int16_t val = buffer;
        printf("%02hX%02hX", (val & 0xFF), ((val >> 8) & 0xFF));
        countByte += 2;
        if(!gpio_get(BUTTON)){
            printf("\r\n");
            printf("----- END DATA -----\r\n");
            break;
        }
    }

    // Create Header File  
    printf("\r\n");
    printf("----- START HEADER -----\r\n");
    CreateWavHeader(headerWave, countByte);
    for (int i = 0; i < LEN_WAVE_HEADER; ++i){
        if (!((i + 1) % 32))
            printf("\r\n");
        printf("%02X", ((unsigned char*)&headerWave)[i]);
    }
    printf("\r\n");
    printf("----- END HEADER -----\r\n");
    printf("%d\r\n", countByte);

    // Stereo 32bits
    // printf("Left:,Right:");
    // while (true){
    //     int16_t buffer[I2S_RX_FRAME_SIZE_IN_BYTES/2];
    //     byteReads = machine_i2s_stream_read(i2s0, (void*)&buffer, I2S_RX_FRAME_SIZE_IN_BYTES);
    //     if (byteReads == 0){
    //         continue;
    //     }
    //     else{  
    //         printf("%d,%d\n", buffer[0], buffer[1]);
    //     }
    // }

    return 0;
}