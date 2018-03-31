import time

class AM_Sender(object):
    def __init__(self):
        pass

    def send_bit(self, bit):
        pr = "1" if bit else "0"
        print(pr, end="")

    def get_sequence_length(self, sequence):
        return len(bin(sequence))-2

    def send_sequence(self, sequence):
        seq_len = self.get_sequence_length(sequence)
        comp_bit = 1 << seq_len
        for i in range(seq_len):
            bit = 1 if (sequence<<i & comp_bit) else 0
            self.send_bit(bit)
        print("")


class RSC_Sender(AM_Sender):
    def __init__(self, address):
        super().__init__()
        self.address = address
        self.channel_dict = {'A':0b0111, 'B':0b1011, 'C':0b1101, 'D':0b1110}
        self.signal_dict = {'ON':0b101, 'OFF':0b110}

    def pad_sequence(self, sequence):
        sequence_length = self.get_sequence_length(sequence)
        comp_bit = 1 << (sequence_length-1)
        tmp_sequence_in = sequence
        tmp_sequence_out = 0
        for i in range(sequence_length):
            tmp_sequence_out = tmp_sequence_out << 1
            bit = 1 if ((tmp_sequence_in<<i) & comp_bit) else 0
            tmp_sequence_out = tmp_sequence_out | bit
            tmp_sequence_out = tmp_sequence_out << 1
        return tmp_sequence_out

    def prepare_sequence(self, channel, signal):
        tmp_address = self.pad_sequence(self.address)
        tmp_channel = self.pad_sequence(channel)
        tmp_signal = self.pad_sequence(signal)
        sequence = tmp_address << 8
        sequence = sequence | tmp_channel
        sequence = sequence << 6
        sequence1 = sequence | tmp_signal
        sequence2 = sequence | 0b111110
        return sequence1, sequence2

    def send(self, channel, signal):
        chn = self.channel_dict[channel]
        sig = self.signal_dict[signal]
        seq1,seq2 = self.prepare_sequence(chn, sig)
        self.send_sequence(seq1)
        self.send_sequence(seq1)
        self.send_sequence(seq1)
        self.send_sequence(seq2)


if __name__ == "__main__":
    sender1 = RSC_Sender(0b10110)
    sender1.send("C","OFF")
