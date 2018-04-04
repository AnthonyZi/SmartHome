#include <wiringPi.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include <stdio.h>

typedef struct smoothReceivers
{
    uint8_t* data;
    uint8_t doff;
//    uint8_t* vals;
//    uint8_t voff;
    uint8_t current_level;
    uint16_t counter;
    uint16_t last_length;

    uint8_t window_size;
    uint8_t thresh;
} SmoothReceiver;


SmoothReceiver init_SmoothReceiver()
{
    SmoothReceiver sr;
    sr.data = calloc(256,sizeof(uint8_t));
    sr.doff = 0;

    sr.current_level = 0;
    sr.counter = 0;
    sr.last_length = 0;

    sr.window_size = 15;
    sr.thresh = 8;
    return sr;
}


typedef struct bitcodes
{
    uint8_t* data;
    uint16_t length;
} Bitcode;

Bitcode init_Bitcode()
{
    Bitcode bc;
    bc.data = calloc(10000,sizeof(uint8_t));
    bc.length = 0;
    return bc;
}

typedef struct signalcodes
{
    uint8_t* data;
    uint16_t length;
} Signalcode;

Signalcode init_Signalcode()
{
    Signalcode sc;
    sc.data = calloc(10000,sizeof(uint8_t));
    sc.length = 0;
    return sc;
}


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

Signalcode decode(Bitcode *bc)
{
    Signalcode sc = init_Signalcode();
    for(uint16_t i = 1; i<bc->length; i+=2)
        *(sc.data+sc.length++) = *(bc->data+i);
    return sc;
}

Bitcode read(int pin)
{
    SmoothReceiver sr = init_SmoothReceiver();
    Bitcode bc = init_Bitcode();
    FILE *fp1;
    fp1 = fopen("fp1", "wb");

    // wait until first level-change (low to high because SmoothReader is initialised with current_level = 0)
    while(!smoothRead(&sr, pin));

    uint8_t lvl_change;
    uint16_t onlength;
    uint8_t bitcounter = 0;
    uint16_t breakpause = 1000;
    while(1)
    {
        fprintf(fp1, "%d ", sr.current_level);
        lvl_change = smoothRead(&sr, pin);
        //if lvl_change read out how long level was hold
        if(lvl_change)
        {
            if(bitcounter++ == 0)
                onlength = sr.last_length;
            else
            {
                *((bc.data)+(bc.length)) = onlength > sr.last_length;
                breakpause = *((bc.data)+(bc.length++)) ? 4*onlength : 4*sr.last_length;
            }
            bitcounter %= 2;
        }
//        delayMicroseconds(5);

        if(sr.counter > breakpause)
            break;
    }

    fclose(fp1);

    free(sr.data);
    return bc;
}

int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
    wiringPiSetup();
    pinMode(pin, INPUT);

    Bitcode *bcs = calloc(8,sizeof(Bitcode));
    Signalcode *scs = calloc(8,sizeof(Signalcode));
    while(1)
    {
        for(uint8_t i = 0; i<8; i++)
            bcs[i] = read(pin);

        for(uint8_t i = 0; i<8; i++)
            scs[i] = decode(&(bcs[i]));

        for(uint8_t i = 0; i<8; i++)
        {
            printf("%d - ", scs[i].length);
            if(scs[i].length != 12)
            {
                printf("\n");
                break;
            }
            for(uint16_t j = 0; j<scs[i].length; j++)
                printf("%d", *((scs[i].data)+j));
            printf("\n");
        }
    }

    return 0;
}
