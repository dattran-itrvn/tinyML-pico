/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#include <stdio.h>

#include "pico/stdlib.h"
#include "tflite_model.h"
#include "dsp_pipeline.h"
#include "ml_model.h"
#include "Wav.h"
#include <time.h>
#include "../lib/i2s_mic_for_pico/machine_i2s.c"

// constants
#define SCK 2
#define WS 3 // needs to be SCK +1
#define SD 6
#define BPS 16 
#define SAMPLE_RATE       16000
#define FFT_SIZE          256
#define SPECTRUM_SHIFT    4
#define INPUT_BUFFER_SIZE ((FFT_SIZE / 2) * SPECTRUM_SHIFT)
#define INPUT_SHIFT       0
#define BUTTON 15
#define LEN_WAVE_HEADER 44

uint32_t countByte = 0;

q15_t capture_buffer_q15[SIZEOF_HALF_DMA_BUFFER_IN_BYTES];
volatile int new_samples_captured = 0;

q15_t input_q15[INPUT_BUFFER_SIZE + (FFT_SIZE / 2)];

DSPPipeline dsp_pipeline(FFT_SIZE);
MLModel ml_model(tflite_model, 128 * 1024);

int8_t* scaled_spectrum = nullptr;
int32_t spectogram_divider;
float spectrogram_zero_point;

uint8_t headerWave[LEN_WAVE_HEADER];

machine_i2s_obj_t* i2s0;
typedef void (*I2SHandler) (machine_i2s_obj_t* i2s0);


clock_t clock(){
    return (clock_t) time_us_64() / 10000;
}

void on_i2s_mic_samples_ready(machine_i2s_obj_t* i2s0){
    new_samples_captured = machine_i2s_stream_read(i2s0, (void*)&capture_buffer_q15, INPUT_BUFFER_SIZE * 2);
    if(new_samples_captured != 0){
        printf("Data OK\r\n");
    }
}

int main( void )
{
    // initialize stdio
    stdio_init_all();
    gpio_init(BUTTON);
    gpio_set_dir(BUTTON, GPIO_IN);
    gpio_pull_up(BUTTON);
    
    printf("---- Pico Tiny-ML-ITRVN detection ----\n");

    if (!ml_model.init()) {
        printf("Failed to initialize ML model!\n");
        while (1) { tight_loop_contents(); }
    }
    else {
        printf("|       ML model initialize OK       |\n");
    }
    if (!dsp_pipeline.init()) {
        printf("Failed to initialize DSP Pipeline!\n");
        while (1) { tight_loop_contents(); }
    }
    else {
        printf("|     DSP Pipeline initialize OK     |\n");
    }

    scaled_spectrum = (int8_t*)ml_model.input_data();
    spectogram_divider = 64 * ml_model.input_scale(); 
    spectrogram_zero_point = ml_model.input_zero_point();

    i2s0 = machine_i2s_make_new(0, SCK, WS, SD, RX, BPS, MONO, SIZEOF_DMA_BUFFER_IN_BYTES, SAMPLE_RATE);
    if(i2s0 == NULL){
        printf("Failed to initialize MIC I2S!\n");
        while (1) { tight_loop_contents(); }
    }
    else{
        printf("|        MIC I2S initialize OK       |\n");
    }
    printf("--------------------------------------\n");
    
    printf("START RECORD\r\n");
    printf("\r\n");
    printf("----- START DATA -----\r\n");

    while (1) {    
        new_samples_captured = machine_i2s_stream_read(i2s0, (void*)&capture_buffer_q15, SIZEOF_HALF_DMA_BUFFER_IN_BYTES * 2);
        if(!gpio_get(BUTTON)){
            printf("\r\n");
            printf("----- END DATA -----\r\n");
            break;
        }

        // while (new_samples_captured == 0) {
        //     tight_loop_contents();
        // }
        // new_samples_captured = 0;

        dsp_pipeline.shift_spectrogram(scaled_spectrum, SPECTRUM_SHIFT, 124);
        // move input buffer values over by INPUT_BUFFER_SIZE samples
        memmove(input_q15, &input_q15[INPUT_BUFFER_SIZE], (FFT_SIZE / 2) * sizeof(q15_t));
        // copy new samples to end of the input buffer with a bit shift of INPUT_SHIFT
        arm_shift_q15(capture_buffer_q15, INPUT_SHIFT, input_q15 + (FFT_SIZE / 2), INPUT_BUFFER_SIZE);
    
        for (int i = 0; i < SPECTRUM_SHIFT; i++) {
            dsp_pipeline.calculate_spectrum(
                input_q15 + i * ((FFT_SIZE / 2)),
                scaled_spectrum + (129 * (124 - SPECTRUM_SHIFT + i)),
                spectogram_divider, spectrogram_zero_point
            );
        }

        // calculator time predict model
        clock_t startTime = clock();
        float prediction = ml_model.predict();
        // sleep_ms(100);
        clock_t endTime = clock();
        double executionTime = (double)(endTime - startTime) / CLOCKS_PER_SEC;
        printf("%.8f sec\n", executionTime);

        // time_taken = time_us_64() - time_taken;
        // printf("Time Process %d us\r\n", time_taken);
        // if (prediction >= 0.5) {
        //   printf("\tFire Alarm\tdetected!\t(prediction = %f)\n\n", prediction);
        // } else {
        //   printf("\tFire Alarm\tNOT detected\t(prediction = %f)\n\n", prediction);
        // }
    }

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

    return 0;
}

