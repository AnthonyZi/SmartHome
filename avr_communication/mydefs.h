#ifndef MYDEFS_H
#define MYDEFS_H

#define BYTES_PER_SEGMENT 10

typedef struct message
{
    uint16_t length;
    uint8_t *information;
} message_s;


typedef struct segment_message
{
    uint8_t length;
    uint8_t information[BYTES_PER_SEGMENT];
} segment_message_s;

typedef struct segment
{
    uint16_t id;
    uint8_t sequence_number;
    uint16_t checksum;
    segment_message_s message;
} segment_s;

//identificatoin 12 bits
#define MAIN_STATION_PI     0x0A8
#define SENS_PYR_1          0xAF1 //0000.1010.1111.0001

//headline 4 bits
#define SEND                0xd

//information 16 bits
#define ON                  0x0001
#define OF                  0x0002



#endif
