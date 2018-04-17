import subprocess

class MPlayerControl:
    def __init__(self, music):
        self.music = music

    def start(self, music=None):
        if not music == None:
            self.music = music
        self.proc = subprocess.Popen(['mplayer', '-slave', self.music])

    def stop(self):
        self.proc.terminate()
