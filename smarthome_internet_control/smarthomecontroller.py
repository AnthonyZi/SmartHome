from smarthomeserver import *
import queue
from AM_Sending import AM_Send

class SmartHomeControl(threading.Thread):
    def __init__(self,client_threads):
        super().__init__()
        self.instruction_queue = queue.Queue()
        self.client_threads = client_threads
        self.states = dict()
        self.states["light_main"] = "off"
        self.states["light_table"] = "off"
        self.rsc1 = AM_Send.RSC_Sender(1, "10110")


    def run(self):
        print("SmartHomeControl startet")
        while(True):
            instruction = self.instruction_queue.get(block=True)
            self.signal_decode(instruction)

    def signal_decode(self, instruction):
        i_list = [i.strip("\n\r ") for i in instruction.split(":")] + ["",""]
        itype, idevice, istate = i_list[:3]
        if(itype == "set"):
            if(self.set_device_state(idevice, istate)):
                self.signal_broadcast("update", idevice, istate)


    def signal_broadcast(self, itype, idevice, istate):
        msg = "{}:{}:{}\n".format(itype, idevice, istate)
        for cthread in self.client_threads:
            cthread.send_queue.put(msg)


    def set_device_state(self, idevice, istate):
        if(idevice in self.states.keys()):
            if(idevice == "light_main"):
                if(istate in ["on", "off"]):
                    self.states[idevice] = istate
                    rsc.send("A", istate.upper())
                else:
                    return False
            elif(idevice == "light_table"):
                if(istate in ["on", "off"]):
                    self.states[idevice] = istate
                    rsc.send("B", istate.upper())
                else:
                    return False
        else:
            return False
        return True


if __name__ == "__main__":
    client_threads = []
    shcontrol_thread = SmartHomeControl(client_threads)
    shcontrol_thread.start()
    server_thread = ServerThread(port=50000, smarthomethread=shcontrol_thread, clientthreads=client_threads)
    server_thread.start()
