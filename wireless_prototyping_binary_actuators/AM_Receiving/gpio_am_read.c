#include <wiringPi.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include <stdio.h>

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


SmoothReceiver init_SmoothReceiver()
{
    SmoothReceiver sr;
    sr.data = (uint8_t*)calloc(256,sizeof(uint8_t));
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
    uint16_t bit_transfer_length;
} Bitcode;

Bitcode init_Bitcode()
{
    Bitcode bc;
    bc.data = (uint8_t*)calloc(10000,sizeof(uint8_t));
    bc.length = 0;
    bc.bit_transfer_length = 118;
    return bc;
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

//Signalcode decode(Bitcode *bc)
//{
//    Signalcode sc = init_Signalcode();
//    for(uint16_t i = 1; i<bc->length; i+=2)
//        *(sc.data+sc.length++) = *(bc->data+i);
//    return sc;
//}

void read(Bitcode *bc, int pin, int package_number)
{
    SmoothReceiver sr = init_SmoothReceiver();

    // wait until first level-change (low to high because SmoothReader is initialised with current_level = 0)
//    if(package_number == 0)
    if(1)
        while(!smoothRead(&sr, pin));
    else
    {
        int return_timer = 10*bc->bit_transfer_length;
        while(!smoothRead(&sr, pin) && return_timer--);
        if(return_timer <= 0)
            return;
    }

    FILE *fp;
    char fname[10];
    sprintf(fname, "fp_%d", package_number);
    fp = fopen(fname, "wb");

    uint8_t lvl_change;
    uint16_t onlength;
    uint8_t bitcounter = 0;
    uint16_t breakpause = 500;
    while(1)
    {
        fprintf(fp, "%d ", sr.current_level);
        lvl_change = smoothRead(&sr, pin);
        //if lvl_change read out how long level was hold
        if(lvl_change)
        {
            if(bitcounter++ == 0)
                onlength = sr.last_length;
            else
            {
                *((bc->data)+(bc->length++)) = onlength > sr.last_length;
//                bc->bit_transfer_length = onlength + sr.last_length;
                if(bc->length>=24)
                {
                    fclose(fp);
                    return;
                }
            }
            bitcounter %= 2;
        }
        delayMicroseconds(5);

//        if(sr.counter > 2*bc->bit_transfer_length)
//            break;
    }

    fclose(fp);
    free(sr.data);
}

void elro_read(int pin)
{
    uint8_t num_packages = 8;

    Bitcode **bcs = (Bitcode**)calloc(num_packages, sizeof(Bitcode*));
    for(uint8_t i = 0; i<num_packages; i++)
    {
        *(bcs+i) = (Bitcode*)calloc(1,sizeof(Bitcode));
        **(bcs+i) = init_Bitcode();
    }

//    Signalcode *scs = calloc(num_packages, sizeof(Signalcode));

    while(1)
    {
        read(*(bcs), pin, 0);
        printf("bit_transfer_length: %d\n", bcs[0]->bit_transfer_length);
        for(uint8_t i = 1; i<num_packages; i++)
        {
            (bcs[i])->bit_transfer_length = (bcs[i-1])->bit_transfer_length;
            read(*(bcs+i), pin, i);
            printf("bit_transfer_length: %d\n", bcs[i]->bit_transfer_length);
        }

        printf("read 8 packages\n");

//        for(uint8_t i = 0; i<num_packages; i++)
//            scs[i] = decode(bcs[i]);

        for(uint8_t i = 0; i<num_packages; i++)
        {
            printf("%d - ", bcs[i]->length);
            for(uint16_t j = 0; j<bcs[i]->length; j++)
                printf("%d", *((bcs[i]->data)+j));
            printf("\n");
        }
        printf("\n");
        break;
    }

    for(uint8_t i = 0; i<num_packages; i++)
        free(bcs[i]);
    printf("\n");
    free(bcs);
//    free(scs);
}


int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
    wiringPiSetup();
    pinMode(pin, INPUT);

    elro_read(pin);

    return 0;
}
