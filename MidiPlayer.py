# contains classes and methods that do the actual midi performance
import threading
import fluidsynth
import time
import os
import sys
import math

from PyQt4 import QtGui, QtCore

class MidiPlayer:
    def __init__(self):        
        self.fs = fluidsynth.Synth()
        self.fs.start()
        
        # connect fluidsynth to JACK audio output if this is linux
        if 'linux' in sys.platform: 
            print('Since this is linux, we assume JACK is installed and use it to connect audio.')
            os.system("jack_connect fluidsynth:l_00 system:playback_1")
            os.system("jack_connect fluidsynth:r_00 system:playback_2")

        sfid = self.fs.sfload("FluidR3_GM.sf2")
#        sfid = self.fs.sfload("/usr/share/sounds/sf2/Scc1t2.sf2")
        
        self.fs.program_select(0, sfid, 0, 0)
        
        self.setTempo(120)
        
    def setTempo(self, tempo):
        self.tempo = tempo
                
    def playNote(self, parent, trackNum, pitch, volume=96, duration=-1, sameNote='False'):
        worker = PlayNote(self, self.fs, trackNum, pitch, volume, duration, sameNote)
        worker.start()
        
        return worker
        
#    def stopEverything(self):
#        self.fs.system_reset()      # stops everything  
        

class Playback:
    def __init__(self, parent):
        self._parent = parent
        self.midiPlayer = self._parent.midiPlayer
        self.cursorItem = self._parent.cursorItem
        self.tracks = self._parent.tracks
        self.tempo = self.midiPlayer.tempo

        self.notesPlaying = []        

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(
            self.timer, 
            QtCore.SIGNAL("timeout()"),
            self.playOneStep)
            
        dt = int(1000.0 * 60.0 / (4.0 * self.tempo))
        self.timer.start(dt)
        
    def playOneStep(self):
        # find all notes on all tracks at current cursor position
        iPos = self.cursorItem.iCursor
        for i in range(0, len(self.tracks)):
            for j in range(0, self.tracks[i].numYGrid):
                val = self.tracks[i].getFromTab(iPos, j)
                
                if val == '*':
                    # get whatever notes are still playing on the appropriate string
                    noteInfo = [x for x in self.notesPlaying if x[1] == i and x[2] == j]
                    # silence notes if they were still playing
                    if len(noteInfo) > 0:
                        noteInfo = noteInfo[0]
                        noteInfo[0].stopNote()
                        self.notesPlaying.remove(noteInfo)
                        
                elif val > -1:
                    # stop any notes that are still playing on the string
                    noteInfo = [x for x in self.notesPlaying if x[1] == i and x[2] == j]
                    newPitch = self.tracks[i].convertNumberToPitch(j, val)

                    if len(noteInfo) > 0:
                        # if new pitch is different, stop note within 50 ms
                        if noteInfo[0][0].pitch != newPitch:
                            noteInfo = noteInfo[0]
                            noteInfo[0].stopNote()
                            self.notesPlaying.remove(noteInfo)
                            
                            noteThread = self.midiPlayer.playNote(self, i, newPitch)
                            # store trackNum, stringNum, and thread object of currently playing notes
                            self.notesPlaying.append([noteThread, i, j])

                        # if pitch is the same, stop note immediately so order of 
                        # noteon and noteoff don't get mixed up
                        else:
                            noteInfo = noteInfo[0]
                            noteInfo[0].stopNote(sameNote='True')
                            self.notesPlaying.remove(noteInfo)

                            noteThread = self.midiPlayer.playNote(self, i, newPitch, sameNote='True')
                            self.notesPlaying.append([noteThread, i, j])
                            
                    else:
                        noteThread = self.midiPlayer.playNote(self, i, newPitch)
                        self.notesPlaying.append([noteThread, i, j])
                    
        # update graphics by moving cursor
        self.cursorItem.moveRight()
        
    def stopPlayback(self):
        self.timer.stop()
        for i in range(0, len(self.notesPlaying)):
            noteInfo = self.notesPlaying[i]
            noteInfo[0].stopNote()
        # remove from list
        self.notesPlaying = []        


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
        print('sameNote = ' + str(self.sameNote))
        if self.sameNote == 'True':
            self.fs.noteoff(0, self.pitch)
        self.fs.noteon(0, self.pitch, self.volume)

        checkTime = 0.050

        # if self.duration was set to -1, play indefinitely
        if self.duration == -1:
            while not self.event.is_set():
                self.event.wait(checkTime)        # wait 100 ms
            if self.sameNote == 'False':
                self.fs.noteoff(0, self.pitch)
        
        elif self.duration > 0:
            # wait and check roughly every 100 ms to see if something stops it by calling self.event.set()
            num = int(math.ceil(self.duration / checkTime));
            dt = self.duration / num
            for i in range(num):
                if self.event.is_set() or (self.duration < time.time() - self.startTime):
                    break
                self.event.wait(dt)

            if self.sameNote == 'False':
                self.fs.noteoff(0, self.pitch)
        
        else:
            print('Warning: note duration of ' + str(self.duration) + ' is not a valid number')
    
    def stopNote(self, sameNote='False'):
        self.sameNote = sameNote
        self.event.set()
        
