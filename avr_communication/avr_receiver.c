#include "avr_receiver.h"


// 7 APPLICATION-LAYER -> MESSAGE
// one application can send a message to another application

void sensor_receive_message(uint32_t msg_encoded)
{
//    message_s recv;
//    recv.headline = (msg_encoded >> 16) & 0x0000000F;
//    recv.information = (msg_encoded) & 0x0000FFFF;
//
//    printf("Layer 7:\n");
//    printf("head: ");
//    print_bin4(recv.headline, 1);
//    printf("information: ");
//    print_bin16(recv.information, 1);
}



// 4 TRANSPORT-LAYER -> SEGMENT
// transports application-layer messages between application endpoints
// -flow-control (speed-matching)
// -sequence numbers
// -acknowledgements
// -timers
// -break long messages into segments
// -congestion-control


void receive_segment()
{
//    printf("waiting for receive:\n");
//    segment_s recv;
//    uint32_t in;
//    scanf("%u", &in);
//
//    recv.identification = (in >> 20);
//    recv.message_encoded = (in & 0x000FFFFF);
//
//    printf("Layer 4:\n");
//    printf("id: ");
//    print_bin12(recv.identification, 1);
//    printf("message: ");
//    print_bin20(recv.message_encoded, 1);
//    switch(recv.identification)
//    {
//        case MAIN_STATION_PI:
//            sensor_receive_message(recv.message_encoded);
//    }
}



// 3 NETWORK-LAYER -> DATAGRAMS
// service of delivering the segments from transport-layer to transport-layer
// IP-Protocol
// routing-protocols




// 2 LINK-LAYER -> FRAMES
//


// 1 PHYSICAL-LAYER -> BITS
