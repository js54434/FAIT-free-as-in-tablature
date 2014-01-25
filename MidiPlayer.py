# contains classes and methods that do the actual midi performance
import threading
import fluidsynth
import time
import os

class MidiPlayer:
    def __init__(self):
        # make this platform-dependent
        self.fs = fluidsynth.Synth()
        self.fs.start()
        # connect fluidsynth to audio output
        os.system("jack_connect fluidsynth:l_00 system:playback_1")
        os.system("jack_connect fluidsynth:r_00 system:playback_2")

        sfid = self.fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
        self.fs.program_select(0, sfid, 0, 0)
                
    def playNote(self, parent, trackNum, pitch, volume=96, duration=0.5):
        worker = PlayNote(self, self.fs, trackNum, pitch, volume, duration)
        worker.start()


class PlayNote(threading.Thread):
    def __init__(self, parent, fs, trackNum, pitch, volume, duration):
        threading.Thread.__init__(self)
        self._parent = parent
        self.trackNum = trackNum
        self.pitch = pitch
        self.volume = volume
        self.duration = duration
        self.fs = fs        # fluidsynth object
        
    def run(self):
        self.fs.noteon(0, self.pitch, self.volume)
        time.sleep(self.duration)

        self.fs.noteoff(0, self.pitch)
        #time.sleep(0.1)
