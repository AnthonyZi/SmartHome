#include "printhelp.h"

void print_bin4(uint8_t number, uint8_t newline)
{
    int i;
    for(i=0; i<4; i++)
    {
        if(number & (1 << 3))
            printf("1");
        else
            printf("0");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}

void print_bin8(uint8_t number, uint8_t newline)
{
    int i;
    for(i=0; i<8; i++)
    {
        if(number & (1 << 7))
            printf("1");
        else
            printf("0");
        if(i == 7)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}

void print_bin12(uint16_t number, uint8_t newline)
{
    int i;
    for(i=0; i<12; i++)
    {
        if(number & (1 << 11))
            printf("1");
        else
            printf("0");
        if(i == 11)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}

void print_bin16(uint16_t number, uint8_t newline)
{
    int i;
    for(i=0; i<16; i++)
    {
        if(number & (1 << 15))
            printf("1");
        else
            printf("0");
        if(i == 15)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}

void print_bin20(uint32_t number, uint8_t newline)
{
    int i;
    for(i=0; i<20; i++)
    {
        if(number & (1 << 19))
            printf("1");
        else
            printf("0");
        if(i == 19)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}

void print_bin24(uint32_t number, uint8_t newline)
{
    int i;
    for(i=0; i<24; i++)
    {
        if(number & (1 << 23))
            printf("1");
        else
            printf("0");
        if(i == 23)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}


void print_bin32(uint32_t number, uint8_t newline)
{
    int i;
    for(i=0; i<32; i++)
    {
        if(number & (1 << 31))
            printf("1");
        else
            printf("0");
        if(i == 31)
            break;
        if(((i+1) % 4) == 0)
            printf(".");
        number = number << 1;
    }
    if(newline)
        printf("\n");
}
