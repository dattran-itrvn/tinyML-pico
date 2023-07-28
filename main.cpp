#include "stdio.h"
#include "pico/stdlib.h"
#include "machine_i2s.c"

#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define UART_ID uart0
#define BAUD_RATE 115200


#define SCK 16
#define WS 17 // needs to be SCK +1
#define SD 20
#define BPS 32 // 24 is not valid in this implementation, but INMP441 outputs 24 bits samples
#define RATE 16000

void init()
{
    stdio_init_all();
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
}

int main()
{
    char strLog[5];
    int FLAG = 0;
    init();
    uart_puts(UART_ID, "Audio Test\n");
	machine_i2s_obj_t* i2s0 = machine_i2s_make_new(0, SCK, WS, SD, RX, BPS, STEREO, SIZEOF_DMA_BUFFER_IN_BYTES, RATE);
    if(i2s0 == NULL){
        while (true)
        {
            uart_puts(UART_ID, "ERROR\n");
            sleep_ms(1000);
        }
    }
    else{
        uart_puts(UART_ID, "OK\n");
    }
	int32_t buffer[I2S_RX_FRAME_SIZE_IN_BYTES / 4];
   
	while (true) {
		FLAG = machine_i2s_stream_read(i2s0, (void*)&buffer[0], I2S_RX_FRAME_SIZE_IN_BYTES);
		sprintf(strLog, "%.8X ", buffer[0]); // right channel is empty, play using $ cat /dev/ttyACM0 | xxd -r -p | aplay -r16000 -c1 -fS32_BE
        uart_puts(UART_ID, strLog);
        memset(strLog, 0, 10);
	}

    return 0;
}