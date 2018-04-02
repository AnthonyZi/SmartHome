#include <wiringPi.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include <stdio.h>

typedef struct smoothReceivers
{
    uint8_t* data;
    uint8_t doff;
    uint8_t* vals;
    uint8_t voff;
} SmoothReceiver;

typedef struct dataInterpreters
{
    uint8_t* data
    uint8_t doff;

    uint8_t* vals;
    uint8_t voff;

    uint8_t mode;
    uint8_t max;
} DataInterpreter;

SmoothReceiver init_SmoothReceiver()
{
    SmoothReceiver sr;
    sr.data = (uint8_t*)malloc(sizeof(uint8_t)*256);
    sr.doff = 0;
    sr.vals = (uint8_t*)malloc(sizeof(uint8_t)*256);
    sr.voff = 0;
    return sr;
}

DataInterpreter init_DataInterpreter()
{
    di.data = (uint8_t*)malloc(sizeof(uint8_t)*256);
    di.doff = 0;
    di.vals = (uint8_t*)malloc(sizeof(uint8_t)*256);
    di.voff = 0;

    di.mode = 0;
    di.longpause = 0;
    return di;
}


void smoothRead(SmoothReceiver *sr, int pin)
{
    input = (uint8_t)digitalRead(pin);
    *(sr->data+(sr->doff++)) = (uint8_t)digitalRead(pin);
    v = *(sr->data+(sr->doff-1))+
        *(sr->data+(sr->doff-2))+
        *(sr->data+(sr->doff-3))+
        *(sr->data+(sr->doff-4))+
        *(sr->data+(sr->doff-5));
    *(sr->vals+(sr->voff++)) = v/5;
}

void read(int pin)
{
    SmoothReceiver sr = init_SmoothReceiver();
    DataInterpreter di = init_DataInterpreter();
    File *fp1
    File *fp2
    fp1 = fopen("fp1", "wb");
    fp2 = fopen("fp2", "wb");

    int c = 0;
    while(c<200000)
    {
        c++;
        smoothRead(&sr, pin);
        fprintf(fp1, "%d", *(sr.data+sr.doff-1));
        fprintf(fp2, "%d", *(sr.vals+sr.voff-1));
        delayMicroseconds(10);
    }
    fclose(fp1);
    fclose(fp2);

    free(sr.data);
    free(sr.vals);
    free(di.data);
    free(di.vals);
}

int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
//    char* outfile = argv[2];
    wiringPiSetup();
    pinMode(pin, INPUT);

    read(pin);

    return 0;
}
