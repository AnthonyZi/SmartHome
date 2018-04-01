#include <wiringPi.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include <stdio.h>

typedef struct arrays
{
    uint8_t* data;
    uint32_t len;
} Array;

Array read(int pin, int time)
{
    Array arr;
    arr.len = (uint32_t)time;
    arr.data = (uint8_t*)malloc(sizeof(uint8_t)*time);

    uint8_t input;
    for(int i = 0; i<time; i++)
    {
        input = (uint8_t)digitalRead(pin);
        *(arr.data+i) = input;
        delayMicroseconds(10);
    }
    return arr;
}

int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
    int time = atoi(argv[2]);
    wiringPiSetup();
    pinMode(pin, INPUT);
    Array arr = read(pin,time);

    FILE *fp;

    fp = fopen("gpio_input.txt", "wb");
    for(int i = 0; i<arr.len; i++)
        fprintf(fp, "%d", *(arr.data+i));
    fclose(fp);

    return 0;
}
