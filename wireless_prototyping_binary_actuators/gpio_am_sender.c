#include <unistd.h>
unsigned int short_time = 375;
unsigned int long_time = 1125;

void waiter()
{
    for(int i = 0; i<666; i++)
    {
        usleep(short_time);
        usleep(long_time);
    }
}
