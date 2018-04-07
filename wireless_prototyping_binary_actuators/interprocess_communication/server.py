import socket
import sys

import threading

HOST = "localhost"
PORT = 8888

class ClientThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while(True):
            data = conn.recv(1024)
            if(data == "bye".encode() or not data):
                break;
            print(data)
        conn.close()


if __name__ == "__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket created")

    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print("Bind failed. Error Code : {} Message {}".format(str(msg[0]),msg[1]))
        sys.exit()

    print("Socket bind complete")

    s.listen(10)
    print("Socket now listening")

    conn, addr = s.accept()
    print("Connected with {} : {}".format(addr[0], addr[1]))

    cthread = ClientThread()
    cthread.start()
    cthread.join()


    s.close()
