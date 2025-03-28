# Generates test data. 
# Also has methods to generate different chords and to repeat patterns. 

from PyQt5 import QtGui, QtCore
import time
import random


class GenerateData:
    def __init__(*args):
        self = args[0]
        self._parent = args[1]
        self.tracks = self._parent.tracks
        
        if len(args) == 3:
            file = args[2]
            self.runScript(file)
        else:
#            self.doStuff()
            pass
            
    def doStuff(self):
        
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
            
    def runScript(self, file):
        print('runScript')
        # go through line by line and interpret stuff
        
        # for testing, just print everything to screen
#        st = file.readline()
#        while st != '':
#            print(st)
#            st = file.readline()
        
    def generateRandomTablatureData(self):
        t1 = time.time()
        for i in range(0, len(self.tracks)):
            # worst case scenario: fill every number
            for jx in range(0, self.tracks[i].numXGrid):
                for jy in range(0, self.tracks[i].numYGrid):
                    val = random.randint(0,9)
                    self.tracks[i].addToTab(jx, jy, val)
        t2 = time.time()
        print("Random number generating time was %g seconds" % (t2 - t1))   
