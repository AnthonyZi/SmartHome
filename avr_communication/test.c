#include "avr_transmitter.h"
#include "avr_receiver.h"
#include "mydefs.h"

#include "printhelp.h"

#define TESTSIZE 2000

int main(int argc, char** argv, char** env)
{
    uint8_t message[TESTSIZE];
    int i;
    for(i = 0; i < TESTSIZE; i++)
    {
        message[i] = i%256;
    }
    message_s out;
    out.length = TESTSIZE;
    out.information = message;
    send_event(out);

//    receive_segment();
    return 0;
}
