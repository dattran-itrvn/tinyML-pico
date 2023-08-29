#include "stdio.h"
#include "tusb.h"
#include "pico/stdlib.h"
#include "machine_i2s.c"
#include "hardware/gpio.h"
#include "usb_microphone.h"

#define SCK 2
#define WS 3 // needs to be SCK +1
#define SD 6
#define BPS 16 
#define RATE 16000
#define BUTTON 15
#define SIZE_RECORD (RATE/1000)

uint32_t byteReads = 0;
int16_t sample_buffer[SIZE_RECORD];
machine_i2s_obj_t* i2s0;
uint8_t id_i2s = 0;

void on_i2s_samples_ready(){
    byteReads = machine_i2s_stream_read(i2s0, (void*)&sample_buffer, SIZE_RECORD*2);
}

void on_usb_microphone_tx_ready(){
  usb_microphone_write(sample_buffer, sizeof(sample_buffer));
}

void init(){
    stdio_init_all();
    gpio_init(BUTTON);
    gpio_set_dir(BUTTON, GPIO_IN);
    gpio_pull_up(BUTTON);
}

int main(){
    init();
    i2s0 = machine_i2s_make_new(id_i2s, SCK, WS, SD,
                                RX, BPS, MONO,
                                SIZEOF_DMA_BUFFER_IN_BYTES,
                                RATE);
    i2s_microphone_set_samples_ready(on_i2s_samples_ready, id_i2s);
    usb_microphone_init();
    usb_microphone_set_tx_ready_handler(on_usb_microphone_tx_ready);

    while (1){
        usb_microphone_task();
    }
    
    return 0;
}