#include <wiringPi.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include <stdio.h>

//wait-time in microseconds
uint16_t w_time = 5;
//computing-time in main while loop where data is beeing received
uint16_t c_time = 14;
//inital bit_transfer_length : 1.5ms / (w_time + c_time)
//(raspberry pi computing_time ~10 microseconds -> 1.5ms/0.01microseconds
uint16_t btl = 80;
//initial window_size : btl/10 -> must be uneven!
uint8_t ws = 30 /2*2 +1;


typedef struct smoothReceivers
{
    uint8_t* data;
    uint8_t doff;
    uint8_t current_level;
    uint16_t counter;
    uint16_t last_length;

    uint8_t window_size;
    uint8_t thresh;
} SmoothReceiver;


SmoothReceiver init_SmoothReceiver(uint8_t pws)
{
    SmoothReceiver sr;
    sr.data = (uint8_t*)calloc(256,sizeof(uint8_t));
    sr.doff = 0;

    sr.current_level = 0;
    sr.counter = 0;
    sr.last_length = 0;

    sr.window_size = pws;
    sr.thresh = pws/2 + 1;
    return sr;
}


typedef struct bitcodes
{
    uint8_t* data;
    uint16_t length;
    uint16_t bit_transfer_length;
} Bitcode;

Bitcode init_Bitcode(uint16_t pbtl)
{
    Bitcode bc;
    bc.data = (uint8_t*)calloc(1000,sizeof(uint8_t));
    bc.length = 0;
    bc.bit_transfer_length = pbtl;
    return bc;
}

void reset_Bitcode(Bitcode *bc)
{
    bc->length = 0;
}

//typedef struct signalcodes
//{
//    uint8_t* data;
//    uint16_t length;
//} Signalcode;
//
//Signalcode init_Signalcode()
//{
//    Signalcode sc;
//    sc.data = calloc(10000,sizeof(uint8_t));
//    sc.length = 0;
//    return sc;
//}


// reads data into a buffer and realises a fir filter to smoothen readings
// fir is similar to a mean filter with a window_size from sr ..
//   .. if sr.thresh = (window_size + 1)/2
uint8_t smoothRead(SmoothReceiver *sr, int pin)
{
    *(sr->data+(sr->doff)) = (uint8_t)digitalRead(pin);
    int v = 0;
    uint8_t p = sr->doff++;
    for(uint8_t i = 0; i<sr->window_size; i++)
    {
        v += *((sr->data)+p);
        p--;
    }
    uint8_t lvl = v/sr->thresh;
    if(lvl == sr->current_level)
    {
        sr->counter++;
        return 0;
    }
    else
    {
        sr->current_level = lvl;
        sr->last_length = sr->counter;
        sr->counter = 0;
        return 1;
    }
}

void read(Bitcode *bc, int pin, int package_number)
{
    SmoothReceiver sr = init_SmoothReceiver(ws);

    uint8_t lvl_change;
    uint16_t onlength;
    uint8_t bitcounter = 0;
    uint32_t c = 3000000;
    while(c--)
    {
        lvl_change = smoothRead(&sr, pin);
        //if lvl_change read out how long level was hold
        if(lvl_change)
        {
            if(bitcounter++ == 0)
                onlength = sr.last_length;
            else
            {
                *((bc->data)+(bc->length)) = onlength > sr.last_length;
                if(*((bc->data)+(bc->length++)))
                    bc->bit_transfer_length = ( (7*btl) + (2*bc->bit_transfer_length) + (1*(onlength+sr.last_length)) ) / 10;
            }
            bitcounter %= 2;
        }
        delayMicroseconds(w_time);

    }
    free(sr.data);
}

void read_timing_test(int pin)
{
    Bitcode *bcs = (Bitcode*)calloc(1,sizeof(Bitcode));
    read(bcs, pin, 0);
    free(bcs);
}


int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
    wiringPiSetup();
    pinMode(pin, INPUT);

    read_timing_test(pin);

    return 0;
}
