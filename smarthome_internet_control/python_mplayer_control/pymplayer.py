import subprocess
import os

class MPlayerControl:
    def __init__(self, music):
        self.music = music

    def start(self, music=None):
        if not music == None:
            self.music = music
        DEVNULL = open(os.devnull, "w")
        self.proc = subprocess.Popen(['mplayer', '-slave', self.music], stdout=DEVNULL, stderr=subprocess.STDOUT)

    def stop(self):
        self.proc.terminate()
