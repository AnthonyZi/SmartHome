#include <wiringPi.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#include <stdio.h>

int short_time = 375; 
int long_time = 1125;

void send_bit(int pin, int bit)
{
    if(bit)
    {
        digitalWrite(pin, HIGH);
        delayMicroseconds(long_time);
        digitalWrite(pin, LOW);
        delayMicroseconds(short_time);
    }
    else
    {
        digitalWrite(pin, HIGH);
        delayMicroseconds(short_time);
        digitalWrite(pin, LOW);
        delayMicroseconds(long_time);
    }
}

void send_signal(int pin, char* sig1, char* sig2, char* sig3)
{
    int sig1_len = strlen(sig1);
    int sig2_len = strlen(sig2);
    int sig3_len = strlen(sig3);
    digitalWrite(pin, LOW);
    delay(10);
    for(int i = 0; i<sig1_len; i++)
    {
        int bit = sig1[i] != '0';
        send_bit(pin, bit);
    }
    for(int i = 0; i<sig2_len; i++)
    {
        int bit = sig2[i] != '0';
        send_bit(pin, bit);
    }
    for(int i = 0; i<sig3_len; i++)
    {
        int bit = sig3[i] != '0';
        send_bit(pin, bit);
    }
}

void send(int pin, char* sig1, char* sig2, char* sig3, char* sig3_end)
{
    digitalWrite(pin, HIGH);
    send_signal(pin, sig1, sig2, sig3);
    send_signal(pin, sig1, sig2, sig3);
    send_signal(pin, sig1, sig2, sig3);
    send_signal(pin, sig1, sig2, sig3_end);
}

int main(int argc, char** argv)
{
    int pin = atoi(argv[1]);
    char* sig1 = argv[2];
    char* sig2 = argv[3];
    char* sig3 = argv[4];
    char* sig3_end = argv[5];
    wiringPiSetup();
    pinMode(pin, OUTPUT);
    send(pin, sig1, sig2, sig3, sig3_end);
    return 0;
}
