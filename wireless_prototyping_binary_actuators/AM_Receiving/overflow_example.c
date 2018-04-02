#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    uint8_t *p1;
    uint8_t *p2;

    uint8_t p1off;
    uint8_t p2off;

    p1 = calloc(256, sizeof(uint8_t));
    p2 = calloc(256, sizeof(uint8_t));

    p1off = 0;
    p2off = 0;

    int v = 0;
    uint8_t p = p1off;
    for(uint16_t i = 0; i<300; i++)
    {
        *(p1+p1off) = p1off++;
        printf("%d ", *(p1+p1off));
    }

    printf("\n");
    for(uint16_t i = 0; i<256; i++)
    {
        printf("%d ", *(p1+i));
    }

    printf("\n");
    p = 0;
    for(uint8_t i = 0; i<19; i++)
    {
        printf("%d ", *(p1+p));
        p--;
    }
}
