#ifndef _TRANSMITTER_H
#define _TRANSMITTER_H

#ifdef _PROTOCOL_SMARTHOME_1
#define _PROTOCOL_SMARTHOME
#define SURROUNDING     100
#define ACTIVE_0        200
#define ACTIVE_1        800
#endif //_PROTOCOL_SMARTHOME_1

#ifdef _PROTOCOL_SMARTHOME_2
#define _PROTOCOL_SMARTHOME
#define SURROUNDING     200
#define ACTIVE_0        400
#define ACTIVE_1        1200
#endif //_PROTOCOL_SMARTHOME_2

#ifdef _PROTOCOL_SMARTHOME

#include <stdint.h>

void sendbit(bool valp);
void send8(uint8_t datap, uint8_t lengthp);
void send16(uint16_t datap, uint8_t lengthp);
void send32(uint32_t datap, uint8_t lengthp);
void send64(uint64_t datap, uint8_t lengthp);

#endif // _PROTOCOL_SMARTHOME
#endif // _TRANSMITTER_H
