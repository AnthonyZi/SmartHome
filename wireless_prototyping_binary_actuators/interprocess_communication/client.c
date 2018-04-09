#include <stdio.h>
#include <string.h>
#include <stdlib.h> //for exit(0);
#include <sys/socket.h>
#include <errno.h> //For errno - the error number
#include <netdb.h>   //hostent
#include <arpa/inet.h>
#include <unistd.h>

int hostname_to_ip(char* hostname, char* ip)
{
    struct hostent *he;
    struct in_addr **addr_list;
    int i;

    if ( (he = gethostbyname( hostname ) ) == NULL)
    {
        herror("gethostbyname");
        return 1;
    }

    addr_list = (struct in_addr**) he->h_addr_list;

    for(i = 0; addr_list[i] != NULL; i++)
    {
        strcpy(ip, inet_ntoa(*addr_list[i]) );
        return 0;
    }
}

int main(int argc, char *argv[])
{
    int sock;
    struct sockaddr_in server;
    char message[1024];
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock == -1)
        printf("Could not create socket");
    puts("Socket created");

    char host_ip[100];
    hostname_to_ip("00anthony.chickenkiller.com", host_ip);
    server.sin_addr.s_addr = inet_addr(host_ip);
    server.sin_family = AF_INET;
    server.sin_port = htons(3347);

    if(connect(sock, (struct sockaddr*)&server, sizeof(server)) < 0)
    {
        perror("connect failed. Error");
        return 1;
    }

    puts("Connected\n");

    char* terminate_str = "bye";
    while(1)
    {
        printf("Enter message:\n");
        scanf("%s", message);

        if(send(sock, message, strlen(message), 0) < 0)
        {
            puts("Send failed");
            return 1;
        }

        if(strcmp(message, terminate_str) == 0)
            break;
    }

    close(sock);
    return 0;
}
