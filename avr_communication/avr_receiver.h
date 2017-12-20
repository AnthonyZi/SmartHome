#ifndef AVR_RECEIVER_H
#define AVR_RECEIVER_H

#include <stdio.h>
#include <stdint.h>
#include "mydefs.h"

#include "printhelp.h"

// 7 APPLICATION-LAYER -> MESSAGE
// one application can send a message to another application

void receive_message(uint32_t msg_encoded);


// 4 TRANSPORT-LAYER -> SEGMENT
// transports application-layer messages between application endpoints
// -flow-control (speed-matching)
// -sequence numbers
// -acknowledgements
// -timers
// -break long messages into segments
// -congestion-control

void receive_segment();


// 3 NETWORK-LAYER -> DATAGRAMS
// service of delivering the segments from transport-layer to transport-layer
// IP-Protocol
// routing-protocols




// 2 LINK-LAYER -> FRAMES
//


// 1 PHYSICAL-LAYER -> BITS

#endif
