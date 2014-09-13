# class for starting or stopping a single midi note, coordinated 
# by the MidiPlayer class
# 
# does the nitty-gritty details of stopping and starting a note and
# handling the Threads

import threading
import time
import math

from PyQt4 import QtGui, QtCore


class PlayNote(threading.Thread):
    def __init__(self, parent, fs, trackNum, pitch, volume, duration, sameNote):
        threading.Thread.__init__(self)
        self._parent = parent
        self.trackNum = trackNum
        self.pitch = pitch
        self.volume = volume
        self.duration = duration
        self.fs = fs        # fluidsynth object
        
        self.sameNote = sameNote        # determines whether new note has same pitch as before
        self.event = threading.Event()
        
    def run(self):
        self.startTime = time.time()
        if self.sameNote == 'True':
            self.fs.noteoff(self.trackNum, self.pitch)
        self.fs.noteon(self.trackNum, self.pitch, self.volume)

        checkTime = 0.050   # ms

        # if self.duration was set to -1, play indefinitely
        if self.duration == -1:
            while not self.event.is_set():
                self.event.wait(checkTime)        
            if self.sameNote == 'False':
                self.fs.noteoff(self.trackNum, self.pitch)
        
        elif self.duration > 0:
            # wait and check roughly every 100 ms to see if something stops it by calling self.event.set()
            num = int(math.ceil(self.duration / checkTime));
            dt = self.duration / num
            for i in range(num):
                if self.event.is_set() or (self.duration < time.time() - self.startTime):
                    break
                self.event.wait(dt)

            if self.sameNote == 'False':
                self.fs.noteoff(self.trackNum, self.pitch)
        
        else:
            print('Warning: note duration of ' + str(self.duration) + ' is not a valid number')
    
    def stopNote(self, sameNote='False'):
        self.sameNote = sameNote
        self.event.set()
        
