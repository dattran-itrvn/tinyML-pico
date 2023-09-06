/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#include <stdio.h>

#include "pico/stdlib.h"
#include "../model/tflite_model.h"
#include "../dsp/dsp_pipeline.h"
#include "../model/ml_model.h"
#include "../i2s_mic/i2s_microphone.h"
#include <time.h>

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
#define LEN_RECORD        512 
#define SIZE_APP_BUFFER   (SIZEOF_DMA_BUFFER_IN_BYTES / 8)

q15_t capture_buffer_q15[LEN_RECORD];
int16_t buffer_record_full[LEN_RECORD];

volatile int new_samples_captured = 0;

q15_t input_q15[INPUT_BUFFER_SIZE + (FFT_SIZE / 2)];

DSPPipeline dsp_pipeline(FFT_SIZE);
MLModel ml_model(tflite_model, 128 * 1024);

int8_t* scaled_spectrum = nullptr;
int32_t spectogram_divider;
float spectrogram_zero_point;

uint16_t countSample = 0;
uint16_t byteReads = 0;
int16_t sample_buffer[SIZE_APP_BUFFER/2];
uint8_t id_i2s = 0;
machine_i2s_obj_t* i2s0;
double executionTimeData = 0;

clock_t clock()
{
    return (clock_t) time_us_64();
}

//// Callback function I2S /////
void on_i2s_samples_ready(){
    byteReads = machine_i2s_stream_read(i2s0, (void*)&buffer_record_full[countSample], SIZE_APP_BUFFER); // app buffer len <= dma buffer len / 8
    countSample += byteReads/2;
}

int main( void )
{
    // initialize stdio
    stdio_init_all();
    
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

    i2s0 = machine_i2s_make_new(id_i2s, SCK, WS, SD,
                                RX, BPS, MONO,
                                SIZEOF_DMA_BUFFER_IN_BYTES * 10,
                                SAMPLE_RATE);

    i2s_microphone_set_samples_ready(on_i2s_samples_ready, id_i2s);

    if(i2s0 == NULL){
        printf("Failed to initialize MIC I2S!\n");
        while (1) { tight_loop_contents(); }
    }
    else{
        printf("|        MIC I2S initialize OK       |\n");
    }
    printf("--------------------------------------\n");

    while (1) {   
        while (countSample < LEN_RECORD) {
            tight_loop_contents();
            printf("Enough data\r\n");
        } 
        countSample = 0;

        clock_t startTime = clock();
        for(int i = 0; i < LEN_RECORD; i++){
            capture_buffer_q15[i] = buffer_record_full[i];
        }
        dsp_pipeline.shift_spectrogram(scaled_spectrum, SPECTRUM_SHIFT, 124);
        // move input buffer values over by INPUT_BUFFER_SIZE samples
        memmove(input_q15, &input_q15[INPUT_BUFFER_SIZE], (FFT_SIZE / 2));
        // copy new samples to end of the input buffer with a bit shift of INPUT_SHIFT
        arm_shift_q15(capture_buffer_q15, INPUT_SHIFT, input_q15 + (FFT_SIZE / 2), INPUT_BUFFER_SIZE);
    
        for (int i = 0; i < SPECTRUM_SHIFT; i++) {
            dsp_pipeline.calculate_spectrum(
                input_q15 + i * ((FFT_SIZE / 2)),
                scaled_spectrum + (129 * (124 - SPECTRUM_SHIFT + i)),
                spectogram_divider, spectrogram_zero_point
            );
        }
        float prediction = ml_model.predict();
        if (prediction >= 0.5) {
            printf("\tFire Alarm\tdetected!\t(prediction = %f)\n\n", prediction);
        } else {
            printf("\tFire Alarm\tNOT detected\t(prediction = %f)\n\n", prediction);
        }
        clock_t endTime = clock();
        double executionTime = (double)(endTime - startTime) / 1000;
        printf("%.4f micro sec\n", executionTime);
    }

    return 0;
}

