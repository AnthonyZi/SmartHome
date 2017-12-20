#include "avr_transmitter.h"

uint8_t g_gbn_window_size = GBN_WINDOW_SIZE;
uint8_t g_gbn_base = 0;

segment_message_s message_buffer[BUFFER_SIZE];
uint8_t message_buffer_pointer = 0;

// 7 APPLICATION-LAYER -> MESSAGE
// one application can send a message to another application



void send_event(message_s message)
{
    uint16_t bytes_message = message.length;
    uint16_t bytes_count;
    uint8_t *info = message.information;

    printf("Layer 7:\n");
    printf("<- length: %u\n", bytes_message);
    printf("<- information: \n");
    for(bytes_count = 0; bytes_count < bytes_message; bytes_count++)
    {
        print_bin8(*(info+bytes_count), 0);
        printf(".");
    }
    printf("\n");


    uint8_t ret = tp_send(DEVICE_ID, message); // if 1 : buffer_overflow (max BYTES_PER_SEG * BUFFER_SIZE)
    printf("send_event: return :%u\n", ret);
}



// 4 TRANSPORT-LAYER -> SEGMENT
// transports application-layer messages between application endpoints
// flow-control: GBN-Protocol, ACK for last correctly received package
//1111.1111
// -flow-control (speed-matching)
// -sequence numbers
// -acknowledgements
//x  -stop-and-wait protocol
// -timers
// -break long messages into segments
// -congestion-control

uint8_t tp_send(uint16_t pid, message_s pmessage)
{
    // PREPARE PACKETS +++

    uint16_t bytes_message = pmessage.length;

    if((bytes_message/BYTES_PER_SEG)+1 > BUFFER_SIZE)
    {
        return 1; //buffer overflow
    }

    message_buffer_pointer = 0;

    uint8_t packet_count = bytes_message/BYTES_PER_SEG;

    // full packets
    uint8_t i;
    for(i = 0; i < packet_count; i++)
    {
        message_buffer[message_buffer_pointer].length = BYTES_PER_SEG;
        uint8_t j;
        for(j = 0; j<BYTES_PER_SEG; j++)
            message_buffer[message_buffer_pointer].information[j] = *(pmessage.information+(BYTES_PER_SEG*i)+j);
        message_buffer_pointer++;
    }

    // last not full packet
    uint8_t last_packet_size = bytes_message%BYTES_PER_SEG;
    if(last_packet_size > 0)
    {
        message_buffer[message_buffer_pointer].length = last_packet_size;
        uint8_t j;
        for(j = 0; j<last_packet_size; j++)
            message_buffer[message_buffer_pointer].information[j] = *(pmessage.information+(BYTES_PER_SEG*packet_count)+j);
        message_buffer_pointer++;
    }

    // SEND PACKETS +++

    g_gbn_base = 0;

    while(g_gbn_base < message_buffer_pointer)
    {
        uint8_t i;
        for(i = g_gbn_base; i<(g_gbn_base+g_gbn_window_size) && i<message_buffer_pointer; i++)
        {
            send_segment(pid, i, message_buffer[i]);
        }
        for(i = 0; i<g_gbn_window_size; i++)
        {
            //try to receive acknoledgements for each packet with timeout counting while nothing is received
            uint32_t in;
            scanf("%u", &in);
            if(in>=g_gbn_base)
                g_gbn_base=in+1;
        }
    }
    return 0;
}

void send_segment(uint16_t pid, uint8_t psequence_number, segment_message_s pmessage)
{

    uint8_t bytes_message = pmessage.length;
    uint8_t bytes_count;
    uint8_t *info = pmessage.information;
    uint16_t checksum = 0;

    //checksum id
    checksum += (pid & 0xFF);
    checksum += ((pid>>8) & 0xFF);

    //checksum sequence number
    checksum += psequence_number;

    //checksum information
    for(bytes_count = 0; bytes_count < bytes_message; bytes_count++)
    {
        uint8_t current_byte = *(info+bytes_count);
        checksum += current_byte;
    }

    //checksum-check:
    printf("checksum_check\n");
    print_bin8((pid & 0xFF), 1);
    printf("%u\n", (pid & 0xFF));
    print_bin8(((pid>>8) & 0xFF), 1);
    printf("%u\n", ((pid>>8) & 0xFF));
    print_bin8((psequence_number), 1);
    printf("%u\n", psequence_number);
    for(bytes_count = 0; bytes_count < bytes_message; bytes_count++)
    {
        print_bin8(*(info+bytes_count), 1);
        printf("%u\n", *(info+bytes_count));
    }

    segment_s segment;
    segment.id = pid;
    segment.checksum = checksum;
    segment.sequence_number = psequence_number;
    segment.message = pmessage;


    printf("Layer 4:\n");
    printf("<- id: ");
    print_bin16(segment.id, 1);
    printf("<- checksum: %u\n", segment.checksum);
    printf("<- sequence number: %u\n", segment.sequence_number);
}



// 3 NETWORK-LAYER -> DATAGRAMS
// service of delivering the segments from transport-layer to transport-layer
// IP-Protocol
// routing-protocols




// 2 LINK-LAYER -> FRAMES
//


// 1 PHYSICAL-LAYER -> BITS
