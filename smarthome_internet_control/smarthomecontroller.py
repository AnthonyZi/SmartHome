from smarthomeserver import *
import queue
from AM_Sending import AM_Send
from python_mplayer_control import pymplayer
import time

class SmartHomeControl(threading.Thread):
    def __init__(self,client_threads):
        super().__init__()
        self.instruction_queue = queue.Queue()
        self.client_threads = client_threads

        self.state_change_wait_time = 2

        self.state_change_time = dict()
        self.states = dict()

        self.states["light_main"] = "off"
        self.states["light_table"] = "off"
        self.states["radio"] = "off"

        self.state_change_time["light_main"] = 0
        self.state_change_time["light_table"] = 0
        self.state_change_time["radio"] = 0

        self.rsc1 = AM_Send.RSC_Sender(1, "10110", "AM_Sending")
        self.radio = pymplayer.MPlayerControl(music="http://mp3.antenneac.c.nmdn.net/ps-antenneac/livestream.mp3")


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
                self.signal_broadcast("update", idevice, self.states[idevice])


    def signal_broadcast(self, itype, idevice, istate):
        msg = "{}:{}:{}\n".format(itype, idevice, istate)
        for cthread in self.client_threads:
            cthread.send_queue.put(msg)


    def set_device_state(self, idevice, istate):
        if(idevice in self.states.keys()):
            if(time.time()-self.state_change_time[idevice] > self.state_change_wait_time):
                self.state_change_time[idevice] = time.time()
                if(idevice == "light_main"):
                    if(istate in ["on", "off"]):
                        self.states[idevice] = istate
                        self.rsc1.send("A", istate.upper())
                        self.rsc1.send("A", istate.upper())
                    else:
                        return False
                elif(idevice == "light_table"):
                    if(istate in ["on", "off"]):
                        self.states[idevice] = istate
                        self.rsc1.send("B", istate.upper())
                        self.rsc1.send("B", istate.upper())
                    else:
                        return False
                elif(idevice == "radio"):
                    if(istate in ["on", "off"]):
                        self.states[idevice] = istate
                        if istate == "on":
                            self.radio.start()
                        else:
                            self.radio.stop()
            else:
                print("last set for {} was {} seconds ago".format(idevice, time.time()-self.state_change_time[idevice]))
                return True
        else:
            return False
        return True


if __name__ == "__main__":
    client_threads = []
    shcontrol_thread = SmartHomeControl(client_threads)
    shcontrol_thread.start()
    server_thread = ServerThread(port=50000, smarthomethread=shcontrol_thread, clientthreads=client_threads)
    server_thread.start()
