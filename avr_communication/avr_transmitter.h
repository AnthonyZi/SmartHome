#ifndef AVR_TRANSMITTER_H
#define AVR_TRANSMITTER_H

#include <stdio.h>
#include <stdint.h>
#include "mydefs.h"

#include "printhelp.h"


#define DEVICE_ID SENS_PYR_1

#define BUFFER_SIZE 205 //for messages in byte (max = 254 =(255-GBN_WINDOW_SIZE) - ack starts at 0 and 1st sequence number starts at 1)
#define BYTES_PER_SEG BYTES_PER_SEGMENT //information-bytes per send-segment - change in mydefs.h

#define GBN_WINDOW_SIZE 5
#define ACK_TIMEOUT 50 //in ms

// 7 APPLICATION-LAYER -> MESSAGE
// one application can send a message to another application


void send_event(message_s message);


// 4 TRANSPORT-LAYER -> SEGMENT
// transports application-layer messages between application endpoints
// -flow-control (speed-matching)
// -sequence numbers
// -acknowledgements
// -timers
// -break long messages into segments
// -congestion-control

uint8_t tp_send(uint16_t pid, message_s pmessage);
void send_segment(uint16_t pid, uint8_t psequence_number, segment_message_s pmessage);


// 3 NETWORK-LAYER -> DATAGRAMS
// service of delivering the segments from transport-layer to transport-layer
// IP-Protocol
// routing-protocols




// 2 LINK-LAYER -> FRAMES
//


// 1 PHYSICAL-LAYER -> BITS


#endif
