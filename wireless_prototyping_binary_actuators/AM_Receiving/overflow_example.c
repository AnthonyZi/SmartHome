#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct tests
{
    uint8_t *dat;
    uint8_t doff;
} Test;

void testing(Test *t)
{
    uint8_t p = t->doff;
    for(uint16_t i = 0; i<300; i++)
    {
        *((t->dat)+(t->doff)) = t->doff++;
        printf("%d ", *((t->dat)+(t->doff)));
    }

    printf("\n");
    for(uint16_t i = 0; i<256; i++)
    {
        printf("%d ", *((t->dat)+i));
    }

    printf("\n");
    p = 0;
    for(uint8_t i = 0; i<19; i++)
    {
        printf("%d ", *((t->dat)+p));
        p--;
    }

}

int main(int argc, char** argv)
{
    Test p1;

    p1.dat = calloc(256, sizeof(uint8_t));
    p1.doff = 0;

    testing(&p1);
}
