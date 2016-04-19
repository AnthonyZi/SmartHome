#include "transmitter.h"

void sendbit(bool valp)
{
        // set transmitpin inactive
        // delay SURROUNDING
        // set transmitpin active
        valp ? //delay(ACTIVE_1) : delay(ACTIVE_0);
        // set transmitpin inactive
        // delay SURROUNDING
}

void send8(uint8_t datap, uint8_t lengthp)
{
        uint8_t comperator = 1<<(lengthp-1);
        for(uint8_t i=0, i<lengthp, i++)
        {
                sendbit((datap&comperator)>0);
                datap <<= 1;
        }
}

void send16(uint16_t datap, uint8_t lengthp)
{
        uint16_t comperator = 1<<(lengthp-1);
        for(uint8_t i=0, i<lengthp, i++)
        {
                sendbit((datap&comperator)>0);
                datap <<= 1;
        }
}

void send32(uint32_t datap, uint8_t lengthp)
{
        uint32_t comperator = 1<<(lengthp-1);
        for(uint8_t i=0, i<lengthp, i++)
        {
                sendbit((datap&comperator)>0);
                datap <<= 1;
        }
}

void send64(uint64_t datap, uint8_t lengthp)
{
        uint64_t comperator = 1<<(lengthp-1);
        for(uint8_t i=0, i<lengthp, i++)
        {
                sendbit((datap&comperator)>0);
                datap <<= 1;
        }
}
