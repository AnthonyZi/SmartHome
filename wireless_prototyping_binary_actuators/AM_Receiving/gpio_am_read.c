#include <wiringPi.h>
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
    uint8_t* data;
    uint8_t doff;

    uint8_t* vals;
    uint8_t voff;

    uint8_t mode;
    uint8_t longpause;
} DataInterpreter;

SmoothReceiver init_SmoothReceiver()
{
    SmoothReceiver sr;
//    sr.data = (uint8_t*)malloc(sizeof(uint8_t)*256);
    sr.data = calloc(256,sizeof(uint8_t));
    sr.doff = 0;
//    sr.vals = (uint8_t*)malloc(sizeof(uint8_t)*256);
    sr.vals = calloc(256,sizeof(uint8_t));
    sr.voff = 0;
    return sr;
}

DataInterpreter init_DataInterpreter()
{
    DataInterpreter di;
//    di.data = (uint8_t*)malloc(sizeof(uint8_t)*256);
    di.data= calloc(256,sizeof(uint8_t));
    di.doff = 0;
//    di.vals = (uint8_t*)malloc(sizeof(uint8_t)*256);
    di.vals = calloc(256,sizeof(uint8_t));
    di.voff = 0;

    di.mode = 0;
    di.longpause = 0;
    return di;
}


void smoothRead(SmoothReceiver *sr, int pin)
{
    *(sr->data+(sr->doff++)) = (uint8_t)digitalRead(pin);
    int v = 0;
    uint8_t p = sr->doff;
    for(uint8_t i = 0; i<19; i++)
    {
        p = (uint8_t)(p-1);
        v += *((sr->data)+p);
    }
    *((sr->vals)+(sr->voff++)) = v;
}

void read(int pin)
{
    SmoothReceiver sr = init_SmoothReceiver();
    DataInterpreter di = init_DataInterpreter();
    FILE *fp1;
    FILE *fp2;
    fp1 = fopen("fp1", "wb");
    fp2 = fopen("fp2", "wb");

    int c = 0;
    while(c<100000)
    {
        c++;
        smoothRead(&sr, pin);
        uint8_t doff = sr.doff-1;
        uint8_t voff = sr.voff-1;
        fprintf(fp1, "%d ", *(sr.data+doff));
        fprintf(fp2, "%d ", *(sr.vals+voff));
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
