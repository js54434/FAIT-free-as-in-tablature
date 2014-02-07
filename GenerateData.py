import time
import sys
import os
from PyQt4 import QtGui, QtCore

import Tracks


class GenerateData:
    def __init__(self, parent):
        self._parent = parent
        self.tracks = self._parent.tracks
        
        E = self.EChord()
        A = self.AChord()
        C = self.CChord()
        G = self.transpose(self.EChord(), 3)
        Fsm7b5 = self.transpose(self.Em7b5Chord(), 2)
        
        stepNums1 = [0, 4, 6, 10, 12]        
        stepNums2 = [0, 4, 6, 8, 12]

        self.addNotesToTrack(self.repeatedChordPattern(E, stepNums1, bar=0))
        self.addNotesToTrack(self.repeatedChordPattern(A, stepNums1, bar=1))
        self.addNotesToTrack(self.repeatedChordPattern(C, stepNums1, bar=2))
        self.addNotesToTrack(self.repeatedChordPattern(G, stepNums1, bar=3))
        self.addNotesToTrack(self.repeatedChordPattern(Fsm7b5, stepNums2, bar=4))
        

    def EChord(self):
        return [[0, 0, 0], 
                        [0, 1, 0],
                        [0, 2, 1],
                        [0, 3, 2], 
                        [0, 4, 2], 
                        [0, 5, 0]]
                        
    def EMinorChord(self):
        return [[0, 0, 0], 
                        [0, 1, 0],
                        [0, 2, 0],
                        [0, 3, 2], 
                        [0, 4, 2], 
                        [0, 5, 0]]
    
                        
    def AChord(self):
        return [[0, 0, 0],
                [0, 1, 2],
                [0, 2, 2],
                [0, 3, 2],
                [0, 4, 0]]

    def AMinorChord(self):
        return [[0, 0, 0],
                [0, 1, 1],
                [0, 2, 2],
                [0, 3, 2],
                [0, 4, 0]]

    def CChord(self):
        return [[0, 0, 0],
                [0, 1, 1],
                [0, 2, 0],
                [0, 3, 2],
                [0, 4, 3]]
                
    def Bbm7b5Chord(self):
        return [[0, 0, 0],
                [0, 1, 2],
                [0, 2, 0],
                [0, 3, 2],
                [0, 4, 1]]
                
    def Em7b5Chord(self):
        return [[0, 0, 0],
                [0, 1, 3],
                [0, 2, 0],
                [0, 3, 2],
                [0, 4, 1],
                [0, 5, 0]] 
        


    def repeatedChordPattern(self, chord, stepNums, bar=0):
        notes = []
        
        for i in stepNums:
            movedChord = self.move(chord, 16*bar + i)
            for j in range(0, len(movedChord)):
                notes.append(movedChord[j])
            
        return notes
            
    def move(self, notes, steps):
        notesOut = []
        for i in range(0, len(notes)):
            x = notes[i]
            notesOut.append([x[0] + steps, x[1], x[2]])

        return notesOut
        
    def transpose(self, notes, transposedAmount):
        notesOut = []
        for i in range(0, len(notes)):
            x = notes[i]
            notesOut.append([x[0], x[1], x[2]+transposedAmount])
            
        return notesOut

    def addNotesToTrack(self, notes):
        for i in range(0, len(notes)):
            x = notes[i]
            self.tracks[0].addToTab(x[0], x[1], x[2])
