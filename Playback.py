# class used for playing midi
import math

from PyQt4 import QtGui, QtCore


class Playback:
    def __init__(self, parent):
        self._parent = parent
        self.midiPlayer = self._parent.midiPlayer
#        self.audioPlayer = self._parent.audioPlayer
        self.cursorItem = self._parent.cursorItem
        self.tracks = self._parent.tracks
        self.tempo = self.midiPlayer.tempo

        self.notesPlaying = []        
        
        # set initial instruments
        for i in range(0, len(self.tracks)):
            if self.tracks[i].isTab():
                inst = self.tracks[i].getLatestInstrument()
                self.midiPlayer.changeInstrument(i, inst)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(
            self.timer, 
            QtCore.SIGNAL("timeout()"),
            self.playOneStep)


        # start audio playback
#        self.audioPlayback = AudioPlayer.Playback(self._parent)
            
        dt = int(1000.0 * 60.0 / (4.0 * self.tempo))
        self.timer.start(dt)
        
        
    def playOneStep(self):
        # first make any necessary instrument changes
        for i in range(0, len(self.tracks)):
            if self.tracks[i].isTab():
                inst = self.tracks[i].getInstrumentAtCurrentIndex()
                if inst >= 0:
                    self.midiPlayer.changeInstrument(i, inst)
    
        # find all notes on all tracks at current cursor position
        iPos = self.cursorItem.iCursor
        for i in range(0, len(self.tracks)):
            if self.tracks[i].isTab():
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
