#include "stdio.h"
#include "pico/stdlib.h"
#include "machine_i2s.c"
#include "Wav.h"

#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define UART_ID uart0
#define BAUD_RATE 500000

#define SCK 2
#define WS 3 // needs to be SCK +1
#define SD 6
#define BPS 16 // 24 is not valid in this implementation, but INMP441 outputs 24 bits samples
#define RATE 16000
#define LEN_WAVE_HEADER 44
#define TIME_RECORD 5

void init()
{
    stdio_init_all();
    // uart_init(UART_ID, BAUD_RATE);
    // gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    // gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
}

int main()
{
    char strLog[5];
    uint8_t headerWave[LEN_WAVE_HEADER];
    uint32_t byteReads = 0;
    uint16_t count = 0;
    uint32_t byte_record = (BPS/8) * RATE * TIME_RECORD;

    init();
    // printf("Audio Test ");
	machine_i2s_obj_t* i2s0 = machine_i2s_make_new(0, SCK, WS, SD, RX, BPS, MONO, SIZEOF_DMA_BUFFER_IN_BYTES, RATE);
    // if(i2s0 == NULL){
    //     while (true)
    //     {
    //         printf("ERROR ");
    //         sleep_ms(1000);
    //     }
    // }
    // else{
    //     printf("OK ");
    // }
	int16_t buffer[byte_record/2];
    
    count += 1;
    printf("START RECORD 5 SECONDS \r\n");
    sleep_ms(500);
    byteReads = machine_i2s_stream_read(i2s0, (void*)&buffer, byte_record);
    printf("END RECORD 5 SECONDS \r\n");
    if(byteReads == byte_record){
        printf("\r\n");
        printf("----- WAV DUMP START -----\r\n");
        CreateWavHeader(headerWave, byte_record);
        for (int i = 0; i < LEN_WAVE_HEADER; ++i){
            if (!((i + 1) % 32))
                printf("\r\n");
            printf("%02X", ((unsigned char*)&headerWave)[i]);
        }
        printf("\r\n");
        for (int b = 0; b < byte_record/2; ++b){
            if (!((b + 1) % 16)){
                printf("\r\n");
            }
            int16_t value = buffer[b];
            printf("%02X%02X", (value & 0xFF), ((value >> 8) & 0xFF));
        }
        printf("\r\n");
        printf("------ WAV DUMP END ------\r\n");
        byteReads = 0;
    }
    
    return 0;
}