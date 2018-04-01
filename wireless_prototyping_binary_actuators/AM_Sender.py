import subprocess

class AM_Sender(object):
    def __init__(self, pin, device_id):
        self.pin = pin
        self.device_id = device_id
        self.id_signal = "0".join(self.device_id) + "0"


    def send(self, sig1, sig2, sig2_end):
        args = ["./gpio_am_send", str(self.pin), self.id_signal, sig1, sig2, sig2_end]
        subprocess.call(args)


class RSC_Sender(AM_Sender):
    def __init__(self, pin, device_id):
        super().__init__(pin, device_id)
        self.sig1_dict = {'A':"0111", 'B':"1011", 'C':"1101", 'D':"1110"}
        self.sig2_dict = {'ON':"101", 'OFF':"110"}
        self.id_signal = "0" + self.id_signal

    def send(self, msg1, msg2):
        sig1 = "0".join(self.sig1_dict[msg1]) + "0"
        sig2 = "0".join(self.sig2_dict[msg2]) + "0"
        sig2_end = "111110"
        super().send(sig1, sig2, sig2_end)


if __name__ == "__main__":
    import time
    s1 = RSC_Sender(1, "10110")
    s2 = RSC_Sender(1, "00000")
    s1.send("B","ON")
    s2.send("A","ON")
    time.sleep(1)
    s1.send("B","OFF")
    s2.send("A","OFF")
