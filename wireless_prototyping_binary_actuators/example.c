//#include <unistd.h>
//
//void waiter()
//{
//    unsigned int short_time = 375;
//    unsigned int long_time = 1125;
//    for(int i = 0; i<666; i++)
//    {
//        usleep(short_time);
//        usleep(long_time);
//    }
//}

#include <time.h>
double My_variable = 3.0;

int fact(int n) {
    if (n <= 1) return 1;
    else return n*fact(n-1);
}

int my_mod(int x, int y) {
    return (x%y);
}

char *get_time()
{
    time_t ltime;
    time(&ltime);
    return ctime(&ltime);
}
