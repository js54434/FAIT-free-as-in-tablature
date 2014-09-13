# Cursor object. 

from PyQt4 import QtGui, QtCore


class Cursor(QtGui.QGraphicsRectItem):
    def __init__(self, parent, tracks):
        self._parent = parent
        self.doesDraw = True
        
        self.tracks = tracks
        
        # the track where cursor is
        self.trackNum = 0           
        self.prev_trackNum = 0
        
        # cursor indices
        self.iCursor, self.jCursor = [0, 0] 
        self.prev_iCursor, self.prev_jCursor = [0, 0]
        self.isInLyrics = False

        QtGui.QGraphicsRectItem.__init__(self, 0, 0, 0, 0)
        self.setPen(QtCore.Qt.black)
        self.setBrush(QtCore.Qt.black)
        
        self.moveToIndex(0, 0, 0)       # initializes rectangle
                        
        # makes cursor blink
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.invertColors)
        self.setBlinkTempo(120)      # tempo in bpm
                
    def setBlinkTempo(self, tempo):
        t = 1000.0 / (tempo / 60.0)     # convert beats per min to ms per beat
        self.timer.start(t)
        
    def invertColors(self):
        self.doesDraw = not self.doesDraw
        if self.doesDraw:
            self.setPen(QtCore.Qt.black)
        else:
            self.setPen(QtCore.Qt.white)
        self.update()
        
    def moveToPosition(self, trackNum, xPos, yPos):
        iPos = self.tracks[trackNum].getCursorIndexX(xPos)
        jPos = self.tracks[trackNum].getCursorIndexY(yPos)
        self.moveToIndex(trackNum, iPos, jPos)
        
    def enterLyrics(self, *args):
        print('enter')
        self.isInLyrics = True

        # render cursor transparent
        self.setPen(QtCore.Qt.transparent)
        self.setBrush(QtCore.Qt.transparent)
        
        self.timer.stop()       # stop blinking timer
                
        self._parent.scrollIfNecessary()

        if len(args) > 0:
            xPos = args[0]
            yPos = args[1]
            
            i1 = self._parent.whichTrackHasPoint(xPos, yPos)

            # check if any lyrics are here
            lyrics = self.tracks[i1].getLyricsAtPosition(xPos, yPos)
            if len(lyrics) > 0:
                print('lyrics here')
                lyrics[0].setFocus()
            elif len(lyrics) == 0:
                lyrics2 = self.tracks[i1].createLyricsAtPosition(xPos, yPos)
                lyrics2.setFocus()

    def leaveLyrics(self):
        print('leave')
        self.isInLyrics = False

        # make cursor opaque again
        self.setPen(QtCore.Qt.black)
        self.setBrush(QtCore.Qt.black)
        self.updateHighlighting()
        
        # restart timer
        self.timer.start()
        
        self._parent.scrollIfNecessary()
                                
    def moveToIndex(self, trackNum, iPos, jPos):
        # check if cursor's already there
#        if iPos == self.iCursor and jPos == self.jCursor:
#            return
        # check if the cursor's being moved out-of-bounds
        
#        if isInLyrics == True:
            
        if iPos < 0 or iPos >= self.tracks[trackNum].numXGrid:
            return
        if jPos < 0:
            if self.tracks[trackNum].hasVocals == False:
                return
            else:
                self.enterLyrics()
                return
                #self.enterLyrics()
        if jPos >= self.tracks[trackNum].numYGrid:
            return
        # else, continue on
        
        x = self.tracks[trackNum].convertIndexToPositionX(iPos)
        y = self.tracks[trackNum].convertIndexToPositionY(jPos)
        w = self.tracks[trackNum].dx
        h = self.tracks[trackNum].dy
        self.setRect(x, y, w, h)
        
        # update indices
        self.prev_trackNum = self.trackNum
        self._parent.prev_trackFocusNum = self.trackNum
        self.trackNum = trackNum
        self._parent.trackFocusNum = trackNum
        if self.prev_trackNum != self.trackNum:     
            self.tracks[self.trackNum].setFocus()       # highlight tracks
            self.tracks[self.prev_trackNum].removeFocus()
        self.prev_iCursor = self.iCursor
        self.iCursor = iPos
        self.prev_jCursor = self.jCursor
        self.jCursor = jPos
        
        self.updateHighlighting()
                    
        # if outside of viewport, scroll window
        self._parent.scrollIfNecessary(x, y)

        
    def moveUp(self):
        self.moveToIndex(self.trackNum, self.iCursor, self.jCursor-1)

    def moveDown(self):
        self.moveToIndex(self.trackNum, self.iCursor, self.jCursor+1)

    def moveLeft(self):
        self.moveToIndex(self.trackNum, self.iCursor-1, self.jCursor)

    def moveRight(self):
        self.moveToIndex(self.trackNum, self.iCursor+1, self.jCursor)
        

    def updateHighlighting(self):
        # unhighlight previously selected number; 
        k = self.prev_trackNum
        i = self.prev_iCursor
        j = self.prev_jCursor
        self.tracks[k].unShadeAtIndex(i,j)

        # highlight current number
        k = self.trackNum
        i = self.iCursor
        j = self.jCursor
        self.tracks[k].shadeAtIndex(i, j)
        
    def addToTab(self, val):
        self.tracks[self.trackNum].addToTab(self.iCursor, self.jCursor, val)
        self.updateHighlighting()
        
    def getFromTab(self):
        return self.tracks[self.trackNum].getFromTab(self.iCursor, self.jCursor)
        
    def removeFromTab(self):
        self.tracks[self.trackNum].removeFromTab(self.iCursor, self.jCursor)
        
    def changeInstrument(self, numInst):
        self.tracks[self.trackNum].changeInstrument(numInst)
        
        
