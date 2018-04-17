import socket
import sys
import threading
import queue



class ClientThread(threading.Thread):
    def __init__(self, connection, address, smarthomethread):
        super().__init__()
        self.connection = connection
        self.address = address
        self.smarthomethread = smarthomethread
        self.send_queue = queue.Queue()

    def run(self):
        print("ClientThread started {}".format(self.address))
        sthread = SendThread(self.connection, self.send_queue)
        sthread.start()
        while(True):
            data = self.connection.recv(1024)
            if not data:
                break
            data = data.decode()
            for d in data.split("\n"):
                if not len(d.split(":")) == 3:
                    continue
                print("{} -> {}".format(self.address, d))
                self.smarthomethread.instruction_queue.put(d.strip("\n\r "))
        sthread.running = False

        sthread.join()
        print("ClientThread closing {}".format(self.address))
        self.connection.close()

class SendThread(threading.Thread):
    def __init__(self, pconnection, pqueue):
        super().__init__()
        self.connection = pconnection
        self.send_queue = pqueue
        self.running = True
        self.sockwriter = self.connection.makefile(mode="w")

    def run(self):
        while(True):
            try:
                send_msg = self.send_queue.get(block=True, timeout=2)
                self.sockwriter.write(send_msg)
                self.sockwriter.flush()

            except queue.Empty:
                if self.running == False:
                    break



class ServerThread(threading.Thread):
    def __init__(self, port, smarthomethread, clientthreads):
        super().__init__()
        self.port = port
        self.smarthomethread = smarthomethread
        self.clientthreads = clientthreads


    def send_smarthome_state(self,cthread):
        for device in self.smarthomethread.states.keys():
            status = self.smarthomethread.states[device]
            update_msg = "update:{}:{}\n".format(device, status)
            cthread.send_queue.put(update_msg)



    def run(self):
        print("ServerThread started")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.port))
        except socket.error as msg:
            print("Bind failed. Error Code: {} Message {}".format(str(msg[0],msg[1])))
            sys.exit();

        sock.listen(10)
        while(True):
            conn, addr = sock.accept()
            cthread = ClientThread(conn, addr, self.smarthomethread)
            cthread.start()

            self.send_smarthome_state(cthread)

            self.clientthreads.append(cthread)

        #close routine
        for cthread in self.clientthreads:
            cthread.join()
        sock.close()
        sys.exit()

