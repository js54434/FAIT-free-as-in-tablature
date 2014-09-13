# the class for the window displaying the tablature

import time
import random
import sys
from PyQt4 import QtGui, QtCore

import Tracks
#import AudioTracks
import SelectionRectangle
import Cursor
import GenerateData

import Playback


class TablatureWindow(QtGui.QGraphicsView):    
    def __init__(*args, **kwargs):
        start_time = time.time()
        
        self = args[0] 
        self._parent = args[1]
                       
        self.midiPlayer = self._parent.midiPlayer
#        self.audioPlayer = self._parent.audioPlayer

        self.isPlaying = False

        QtGui.QGraphicsView.__init__(self)    
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)

        if 'loadFile' in kwargs:
            self.loadTracks(kwargs['loadFile'])
        else:
            self.tracks = [Tracks.Track(self, hasVocals='True'), 
                    Tracks.Track(self, numYGrid=7), 
#                    AudioTracks.AudioTrack(self), 
                    Tracks.Track(self, hasVocals='True')]
            self.positionTracks()

            self.scene.setSceneRect(QtCore.QRectF(0, 0, 
                    self.windowSizeX, self.windowSizeY))

        self.centerOn(0,0)

        self.initializeCursor()
        self.initializeSelectionRectangles()
        self.initializePanels()
        
        self.defineKeyGroups()
        
        end_time = time.time()
        print("Initializing time was %g seconds" % (end_time - start_time))
        
#        self.makeBoundariesVisibleForTesting()
        
        # initialize tracks to guitar
        for i in range(0, len(self.tracks)):
            if self.tracks[i].__class__.__name__ is not 'AudioTrack':
                self.tracks[i].changeInstrument(27)
        
        self.setTempo(140)
        
        self.generateData()

        

        
    def defineKeyGroups(self):
        self.numberKeys = (QtCore.Qt.Key_0,
                      QtCore.Qt.Key_1,  
                      QtCore.Qt.Key_2, 
                      QtCore.Qt.Key_3, 
                      QtCore.Qt.Key_4, 
                      QtCore.Qt.Key_5, 
                      QtCore.Qt.Key_6, 
                      QtCore.Qt.Key_7, 
                      QtCore.Qt.Key_8, 
                      QtCore.Qt.Key_9)
                      
        self.arrowKeys = (QtCore.Qt.Key_Up, 
                        QtCore.Qt.Key_Down,
                        QtCore.Qt.Key_Left,
                        QtCore.Qt.Key_Right)
                        
        self.letterKeys = (QtCore.Qt.Key_A, QtCore.Qt.Key_B, QtCore.Qt.Key_C,
            QtCore.Qt.Key_D, QtCore.Qt.Key_E, QtCore.Qt.Key_F, QtCore.Qt.Key_G,
            QtCore.Qt.Key_H, QtCore.Qt.Key_I, QtCore.Qt.Key_J, QtCore.Qt.Key_K,
            QtCore.Qt.Key_L, QtCore.Qt.Key_M, QtCore.Qt.Key_N, QtCore.Qt.Key_O,
            QtCore.Qt.Key_P, QtCore.Qt.Key_Q, QtCore.Qt.Key_R, QtCore.Qt.Key_S,
            QtCore.Qt.Key_T, QtCore.Qt.Key_U, QtCore.Qt.Key_V, QtCore.Qt.Key_W,
            QtCore.Qt.Key_X, QtCore.Qt.Key_Y, QtCore.Qt.Key_Z)
        
        
    def keyPressEvent(self, e):
        i = self.trackFocusNum
        key = e.key()
        modifiers = QtGui.QApplication.keyboardModifiers()

        if self.cursorItem.isInLyrics == True:
            if key == QtCore.Qt.Key_Down:
                self.cursorItem.leaveLyrics()
            else:
                QtGui.QGraphicsView.keyPressEvent(self, e)
            return
        # else, cursor is in track, and we do the following
        
        
        if key in self.arrowKeys:
            if modifiers == QtCore.Qt.ShiftModifier:    # if shift is held
                if self.selectionRectangle.rect().width() == 0 or \
                        self.selectionRectangle.rect().height() == 0:        # if nothing is selected
                    self.selectionRectangle.setRect(self.cursorItem.rect()) # then choose cursor rectangle as selection area
           
                sides = self.whichSidesOfSelectionRectangleIsCursorAt()
                
                if key == QtCore.Qt.Key_Up:
                    if 'top' in sides:
                        self.selectionRectangle.expandUp()
                    elif 'bottom' in sides and 'top' not in sides:
                        self.selectionRectangle.contractUp()
                    self.cursorItem.moveUp()
                if key == QtCore.Qt.Key_Down:
                    if 'bottom' in sides:
                        self.selectionRectangle.expandDown()
                    elif 'top' in sides and 'bottom' not in sides:
                        self.selectionRectangle.contractDown()
                    self.cursorItem.moveDown()
                if key == QtCore.Qt.Key_Left:
                    if 'left' in sides:
                        self.selectionRectangle.expandLeft()
                    elif 'right' in sides and 'left' not in sides:
                        self.selectionRectangle.contractLeft()
                    self.cursorItem.moveLeft()
                if key == QtCore.Qt.Key_Right:
                    if 'right' in sides:
                        self.selectionRectangle.expandRight()
                    elif 'left' in sides and 'right' not in sides:
                        self.selectionRectangle.contractRight()
                    self.cursorItem.moveRight()
                    
                c = self.selectionRectangle.rect()
                for i in range(0, len(self.tracks)):
                    # -1's are to make sure selection area doesn't select more than intended
                    self.tracks[i].shadeSelectedRegion(c.left(), c.top(), c.right()-1, c.bottom()-1)    

            else:    # if shift is not held
                self.unSelect()
                if key == QtCore.Qt.Key_Up:
                    self.cursorItem.moveUp()
                if key == QtCore.Qt.Key_Down:
                    self.cursorItem.moveDown()
                if key == QtCore.Qt.Key_Left:
                    self.cursorItem.moveLeft()
                if key == QtCore.Qt.Key_Right:
                    self.cursorItem.moveRight()

        # enter moves cursor down
        if key == QtCore.Qt.Key_Return:
            self.cursorItem.moveDown()
            
        # check for number input
        if key in self.numberKeys:
            self.unSelect()
            num = int(key)-48               # number typed in

            val = self.cursorItem.getFromTab()     # current number at space
            if val == -1:
                # if no number is already there, go ahead and add the number
                self.cursorItem.addToTab(num)
                            
                pitch = self.tracks[i].convertNumberToPitch(self.cursorItem.jCursor, num)
                self.midiPlayer.changeInstrument(i, self.tracks[i].getLatestInstrument())
                self.midiPlayer.playNote(self, i, pitch, duration=0.3)
            else:
                # if there is a number, check if could be the first digit of a two-digit number
                maxVal = 24         # highest number allowed
                maxDigit = (maxVal - (maxVal % 10)) / 10        # maximum of second digit
                if val in range(1, maxDigit+1):
                    # add second digit to number
                    num2 = val*10 + num
                    self.cursorItem.addToTab(num2)
                    
                    pitch = self.tracks[i].convertNumberToPitch(self.cursorItem.jCursor, num2)
                    self.midiPlayer.changeInstrument(i, self.tracks[i].getLatestInstrument())
                    self.midiPlayer.playNote(self, i, pitch, duration=0.3)
                else:
                    # otherwise, just add new number
                    self.cursorItem.addToTab(num)
                    
                    pitch = self.tracks[i].convertNumberToPitch(self.cursorItem.jCursor, num)
                    self.midiPlayer.changeInstrument(i, self.tracks[i].getLatestInstrument())
                    self.midiPlayer.playNote(self, i, pitch, duration=0.3)      
                    
        # asterisk (*) stops note
        if key == QtCore.Qt.Key_Asterisk:
            self.unSelect()
            self.cursorItem.addToTab('*')
            
        # space and backspace removes data
        if key == QtCore.Qt.Key_Backspace or key == QtCore.Qt.Key_Space:
            if self.selectionRectangle.rect().width() == 0 or \
                    self.selectionRectangle.rect().height() == 0:
                self.cursorItem.removeFromTab()
            else:
                # remove selected items
                for j in range(len(self.tracks)):
                    self.tracks[j].removeSelectedRegion()
            self.unSelect()
            
        # insert and delete
        #, QtCore.Qt.Key_Delete
        
        # "p" starts or stops playback
        if key == QtCore.Qt.Key_P:
            self.togglePlayback()
                
    
    def mousePressEvent(self, e):
        self.unSelect()
        
        scenePoint = self.mapToScene(e.x(), e.y())
        xPos = scenePoint.x()
        yPos = scenePoint.y()
        print('scenePoint: ' + str([xPos, yPos]))
        self.mousePressedX = xPos
        self.mousePressedY = yPos
                
        # reset selection to zero area
        self.selectionRectangle.setRect(
            self.mousePressedX, 
            self.mousePressedY, 
            0, 
            0)

        # move cursor to where mouse clicked
        i1 = self.whichTrackHasPoint(xPos, yPos)
        if self.tracks[i1].isPositionOnStrings(xPos, yPos) == True:
            if self.cursorItem.isInLyrics == True:
                self.cursorItem.leaveLyrics()
            self.cursorItem.moveToPosition(i1, xPos, yPos)
        elif self.tracks[i1].isPositionOnLyrics(xPos, yPos) == True:
            if self.cursorItem.isInLyrics == False:
                self.cursorItem.enterLyrics(xPos, yPos)
            # if mouse clicked on lyrics, then default to standard behavior, 
            # which is to edit the lyrics
            QtGui.QGraphicsView.mousePressEvent(self, e)

    def mouseMoveEvent(self, e):        
        if e.buttons() == QtCore.Qt.LeftButton:
            scenePoint = self.mapToScene(e.x(), e.y())
            xPos = scenePoint.x()
            yPos = scenePoint.y()
            
            i1 = self.whichTrackHasPoint(xPos, yPos)
            if self.tracks[i1].isPositionOnLyrics(xPos, yPos) == True:
                QtGui.QGraphicsView.mouseMoveEvent(self, e)
            else:
                # shade all rectangles within this area
                self.selectionRectangle.updateSelectionRectangle(
                    [self.mousePressedX, self.mousePressedY, xPos, yPos])

                # when selecting, we want the cursor to follow the rectangle
                x1 = self.tracks[i1].returnAlignedCoordX(xPos, 'left')
                y1 = self.tracks[i1].returnAlignedCoordY(yPos, 'top')
                self.cursorItem.moveToPosition(i1, x1, y1)
            
#    def mouseReleaseEvent(self, e):
#        pass

    def scrollContentsBy(self, dx, dy):
        QtGui.QGraphicsView.scrollContentsBy(self, dx, dy)
        
        # move button to compensate
#        rect = self._parent.playButton.geometry()
#        self._parent.playButton.setGeometry(rect.x()+dx, rect.y(), rect.width(), rect.height())
    
        # scroll floating panels
        rect = self.leftPanel.rect()
        self.leftPanel.setRect(rect.x()-dx, rect.y(), rect.width(), rect.height())
        
        rect = self.topPanel.rect()
        self.topPanel.setRect(rect.x()-dx, rect.y()-dy, rect.width(), rect.height())
    
        # scroll floating items like tuning and play button
        for i in range(0, len(self.tracks)):
            self.tracks[i].scrollFloatingItems(dx, dy)


    def scrollIfNecessary(*args):
        self = args[0]
        if len(args) == 3:
            x = args[1]
            y = args[2]
        else:
            x = self.cursorItem.rect().x()
            y = self.cursorItem.rect().y()
            
        scrollX = 16 * self.tracks[0].dx
        scrollY = self.tracks[0].numYGrid * self.tracks[0].dy
                        
        cursorPoint = self.mapFromScene(x, y)
        x_cur, y_cur = [cursorPoint.x(), cursorPoint.y()]

        viewportCenterPoint = self.mapToScene(self.viewport().rect().center())
        x = viewportCenterPoint.x()
        y = viewportCenterPoint.y()

        if x_cur > self.width()-80:
            # we translate by moving center
            self.centerOn(x+scrollX, y+1)           # "+1" is to correct for a bug in "centerOn"
        elif x_cur < 10:
            self.centerOn(x-scrollX, y+1)
            
        viewportCenterPoint = self.mapToScene(self.viewport().rect().center())
        x = viewportCenterPoint.x()
        y = viewportCenterPoint.y()
        
        if y_cur > self.height()-80:
            self.centerOn(x+1, y+scrollY)
        elif y_cur < 80:
            self.centerOn(x+1, y-scrollY)

        self.update()

                        
    def whichSidesOfSelectionRectangleIsCursorAt(self):
        sides = []
        
        b1 = self.cursorItem.boundingRect()
        b2 = self.selectionRectangle.rect()
        if b1.top() == b2.top():
            sides.append('top')
        if b1.left() == b2.left():
            sides.append('left')
        if b1.bottom() == b2.bottom():
            sides.append('bottom')
        if b1.right() == b2.right():
            sides.append('right')
        
        return sides

                        
    def whichTrackHasPoint(self, x, y):
        # if too high or too low, settle on nearest track
        if y < self.tracks[0].top():
            return 0
        for i in range(0, len(self.tracks)-1):
            if y in range(self.tracks[i].top(), self.tracks[i].bottom()):       # if inside track
                return i
            elif y in range(self.tracks[i].bottom(), self.tracks[i+1].top()):   # if just beneath track
                return i
        lastNum = len(self.tracks) - 1
        if y in range(self.tracks[lastNum].top(), self.tracks[lastNum].bottom()):
            return lastNum
        elif y > self.tracks[lastNum].bottom():
            return lastNum

        # else
        return -1
                    
    def cutSelection(self):
        num = len(self.getSelectedTrackNums())
        if num > 0:
            self.copiedSelectionRectangle.setRect(self.selectionRectangle.rect())            
            for i in range(0, len(self.tracks)):
                self.tracks[i].cutSelectedRegion()
        
    def copySelection(self):
        num = len(self.getSelectedTrackNums())
        if num > 0:
            self.copiedSelectionRectangle.setRect(self.selectionRectangle.rect())            
            for i in range(0, len(self.tracks)):
                self.tracks[i].copySelectedRegion()

    def pasteSelection(self):
        selectedTrackNums = self.getCopiedTrackNums()
        if len(selectedTrackNums) == 0:
            pass

        # if one track selected, copy only the selected track and paste to whatever other track
        elif len(selectedTrackNums) == 1:
            i = selectedTrackNums[0]
            iPos = self.cursorItem.iCursor
            
            copiedStuff = self.tracks[i].getCopiedItems()
            self.tracks[self.trackFocusNum].pasteFromOtherTrack(iPos, copiedStuff)
            
            # show pastedSelectionRectangle at coordinates
            xx = self.copiedSelectionRectangle.rect()
            x = [xx.x(), xx.y(), xx.x() + xx.width(), xx.y() + xx.height()]
            # shift to cursor position
            newX0 = self.tracks[self.trackFocusNum].convertIndexToPositionX(iPos)
            delta_y = self.tracks[self.trackFocusNum].trackTop() - self.tracks[i].trackTop()
            newY0 = x[1] + delta_y
            self.pastedSelectionRectangle.setRect(newX0, newY0, x[2]-x[0], x[3]-x[1])
            self.update()
            
        # if more than one track selected, paste only those tracks to the same tracks
        elif len(selectedTrackNums) > 1:
            iPos = self.cursorItem.iCursor
            for i in selectedTrackNums:
                self.tracks[i].pasteSelectedRegion(iPos)
                
            xx = self.copiedSelectionRectangle.rect()
            x = [xx.x(), xx.y(), xx.x() + xx.width(), xx.y() + xx.height()]
            # shift to cursor position
            newX0 = self.tracks[selectedTrackNums[0]].convertIndexToPositionX(iPos)
            self.pastedSelectionRectangle.setRect(newX0, x[1], x[2]-x[0], x[3]-x[1])
            self.update()

        self.cursorItem.updateHighlighting()
        
    def getSelectedTrackNums(self):
        s = []
        for i in range(0, len(self.tracks)):
            if self.tracks[i].isSomeRegionSelected():
                s.append(i)
        return s

    def getCopiedTrackNums(self):
        s = []
        for i in range(0, len(self.tracks)):
            if self.tracks[i].wasSomeRegionCopied():
                s.append(i)
        return s
                
    def unSelect(self):
        self.selectionRectangle.setRect(0,0,0,0)

        # undo selection in each track
        for i in range(0, len(self.tracks)):
            self.tracks[i].unSelect()
            
        self.cursorItem.updateHighlighting()
            
    
        
    def makeBoundariesVisibleForTesting(self):
        
        self.trackRects = []
        self.lyricsRects = []
        self.stringRects = []
        self.leftBarRect = []
        self.topBarRect = []
        j = 0
        for i in range(0, len(self.tracks)):
            # track boundaries
            x1 = self.tracks[i].left()
            y1 = self.tracks[i].top()
            x2 = self.tracks[i].right()
            y2 = self.tracks[i].bottom()
            self.trackRects.append(QtGui.QGraphicsRectItem(x1, y1, (x2-x1), (y2-y1)))
            self.trackRects[i].setPen(QtCore.Qt.blue)
            self.trackRects[i].setBrush(QtCore.Qt.transparent)
            self.scene.addItem(self.trackRects[i])
            
            # lyrics boundaries
            if self.tracks[i].hasVocals == True:
                y1 = self.tracks[i].lyricsTop()
                y2 = self.tracks[i].lyricsBottom()
                self.lyricsRects.append(QtGui.QGraphicsRectItem(x1, y1, (x2-x1), (y2-y1)))
                self.lyricsRects[j].setPen(QtCore.Qt.red)
                self.lyricsRects[j].setBrush(QtCore.Qt.transparent)
                self.scene.addItem(self.lyricsRects[j])
                j = j + 1
                            
            # string boundaries
            y1 = self.tracks[i].trackTop()
            y2 = self.tracks[i].trackBottom()
            self.stringRects.append(QtGui.QGraphicsRectItem(x1, y1, x2-x1, y2-y1))
            self.stringRects[i].setPen(QtCore.Qt.green)
            self.stringRects[i].setBrush(QtCore.Qt.transparent)
            self.scene.addItem(self.stringRects[i])
            
            y1 = 0
            y2 = self.tracks[0].top()
            x1 = 0
            x2 = self.tracks[0].right()
            self.topBarRect = QtGui.QGraphicsRectItem(x1, y1, x2-x1, y2-y1)
            self.topBarRect.setPen(QtCore.Qt.gray)
            self.topBarRect.setBrush(QtCore.Qt.transparent)
            self.scene.addItem(self.topBarRect)
            
            y1 = 0
            y2 = self.tracks[len(self.tracks)-1].bottom()
            x1 = 0
            x2 = self.tracks[0].left()
            self.leftBarRect = QtGui.QGraphicsRectItem(x1, y1, x2-x1, y2-y1)
            self.leftBarRect.setPen(QtCore.Qt.gray)
            self.leftBarRect.setBrush(QtCore.Qt.transparent)
            self.scene.addItem(self.leftBarRect)
                        
    def initializeCursor(self):
        
        # create cursor
        self.cursorItem = Cursor.Cursor(self, self.tracks)
        self.cursorItem.setZValue(-10)           # have cursor appear below numbers so 
                                                # cursor doesn't block them
        self.scene.addItem(self.cursorItem)

    def initializeSelectionRectangles(self):
        # create various selection rectangles to visualize selection        
        self.selectionRectangle = SelectionRectangle.SelectionRectangle(self.tracks, 0, 0, 0, 0)
        self.selectionRectangle.setZValue(30)
        self.selectionRectangle.setPen(QtCore.Qt.transparent)
        self.selectionRectangle.setBrush(QtCore.Qt.cyan)
        self.selectionRectangle.setOpacity(0.5)
        self.scene.addItem(self.selectionRectangle)
        
        self.copiedSelectionRectangle = SelectionRectangle.SelectionRectangle(self.tracks, 0, 0, 0, 0)
        self.copiedSelectionRectangle.setZValue(30)
        self.copiedSelectionRectangle.setPen(QtCore.Qt.transparent)
        self.copiedSelectionRectangle.setBrush(QtCore.Qt.green)
        self.copiedSelectionRectangle.setOpacity(0.25)
        self.scene.addItem(self.copiedSelectionRectangle)        
        
        self.pastedSelectionRectangle = SelectionRectangle.SelectionRectangle(self.tracks, 0, 0, 0, 0)
        self.pastedSelectionRectangle.setZValue(40)
        self.pastedSelectionRectangle.setPen(QtCore.Qt.transparent)
        self.pastedSelectionRectangle.setBrush(QtCore.Qt.red)
        self.pastedSelectionRectangle.setOpacity(0.25)
        self.scene.addItem(self.pastedSelectionRectangle)
        
    def initializePanels(self):
#        self.tablatureWindow.viewport().height()
        self.leftPanel = QtGui.QGraphicsRectItem(0, 0, 100, self.windowSizeY)
        self.leftPanel.setBrush(QtCore.Qt.lightGray)
        self.leftPanel.setPen(QtCore.Qt.transparent)
        self.leftPanel.setZValue(40)
        self.scene.addItem(self.leftPanel)
        
        self.topPanel = QtGui.QGraphicsRectItem(0, 0, 2000, 100)
        self.topPanel.setBrush(QtCore.Qt.lightGray)
        self.topPanel.setPen(QtCore.Qt.transparent)
        self.topPanel.setZValue(40)
        self.scene.addItem(self.topPanel)


    def positionTracks(self):
        self.prev_trackFocusNum = 0
        self.trackFocusNum = 0       # to begin with, focus is on track 0
        
        self.xMar = 100          # margins from top and left side of window to topmost track
        self.yMar = 100
        self.trackMar = 50      # margin between tracks
        
        self.tracks[0].setX0(self.xMar)
        self.tracks[0].setY0(self.yMar)
        for i in range(0, len(self.tracks)):
            if i > 0:
                self.tracks[i].setX0(self.xMar)
                self.tracks[i].setY0(self.tracks[i-1].y0 + \
                            self.tracks[i-1].height + self.trackMar)
            self.tracks[i].drawStuff()
    
        # calculate window size
        self.windowSizeX = self.tracks[0].x0 + \
                        self.tracks[0].dx*3 + self.tracks[0].width
        self.windowSizeY = self.tracks[0].y0
        for i in range(0, len(self.tracks)):
            self.windowSizeY = self.windowSizeY + self.tracks[i].height + self.trackMar
            
        
    def setTempo(self, tempo):
        self.midiPlayer.setTempo(tempo)
        self.cursorItem.setBlinkTempo(tempo)
        self.updateStatusBar()
        
        
    def updateStatusBar(self):
        self._parent.statusBar().showMessage('tempo: ' + str(self.midiPlayer.tempo))


    def togglePlayback(self):
        if self.isPlaying == False:
            self.beginPlayback()
        else:
            self.stopPlayback()
            
        self.setFocus()     # make sure QGraphicsView doesn't lose focus when overlaying playButton is pressed
        
    def beginPlayback(self):
        self.isPlaying = True
        print('playback')
        # start playback:
        # test an overlay button
        self._parent.playButton.setIcon(QtGui.QIcon("pauseButton.png"))
        self.playback = Playback.Playback(self)
        
    def stopPlayback(self):
        self.isPlaying = False
        print('stopPlayback')
        self._parent.playButton.setIcon(QtGui.QIcon("startButton-sharp.png"))
        self.playback.stopPlayback()
        
    def getSaveFileData(self):
        # return a string of what we want to save
        
        st = ''
        # first add number of tracks and their sizes
        st = st + 'number of tracks:\n'             # line 1
        st = st + str(len(self.tracks)) + '\n'     # line 2
        for i in range (0, len(self.tracks)):
            st = st + 'track ' + str(i) + '\n'                        
            st = st + 'hasVocals?' + '\n'
            st = st + str(self.tracks[i].hasVocals) + '\n'
            st = st + 'numXGrid:\n'                                   
            st = st + str(self.tracks[i].numXGrid) + '\n'                  
            st = st + 'numYGrid:\n'
            st = st + str(self.tracks[i].numYGrid) + '\n'
            st = st + 'Raw track data:\n'
            # now dump data, separated by '\n' delimiter
            st = st + self.tracks[i].toString() + '\n'
            st = st + self.tracks[i].instrumentsToString() + '\n'
            st = st + '\n'
            st = st + '\n'
        return st
        
    def loadTracks(self, file):
        dataStrings = []
        instStrings = []
        
        # go through file line by line and do appropriate actions
        file.readline()                     # line 1: "number of tracks"
        st = file.readline()                # line 2: get number of tracks
        numTracks = int(st)
        self.tracks = []
  
        for i in range(0, numTracks):
            st = file.readline()                    # 'track' + no.
            if st != '':        # if not end of file
                file.readline()                     # "hasVocals?"
                hasVocals1 = file.readline().strip('\n') # 'True' if has vocals
                file.readline()                     # "numXGrid"                                
                numXGrid1 = int(file.readline())     
                file.readline()                     # "numYGrid"
                numYGrid1 = int(file.readline())     
                file.readline()                     
                st = file.readline()                
                dataStrings.append(st)              # get raw data
                st = file.readline()
                instStrings.append(st)              # get instrument data
                
                file.readline()                     # blank
                file.readline()                     # blank
                
                self.tracks.append(Tracks.Track(self, numXGrid=str(numXGrid1), 
                    numYGrid=str(numYGrid1), hasVocals=hasVocals1))
                                
        
        # draw tracks' grids, tunings, and cursor, and arrange tracks
        self.PositionTracks()
#        self.initializeCursor()
#        self.initializeSelectionRectangles()
        
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 
                self.windowSizeX, self.windowSizeY))

        # now that tracks are arranged, load track data
        for i in range(0, len(self.tracks)):
            self.tracks[i].loadFromString(dataStrings[i])
            self.tracks[i].loadInstrumentsFromString(instStrings[i])
            
    def runScript(self, file):
        GenerateData.GenerateData(self, file)
            
    def generateData(self):
        GenerateData.GenerateData(self)
        self.cursorItem.updateHighlighting()
        
    def changeInstrument(self, numInst):
        print('change instrument, ' + str(numInst))
        # show dialog
        
        self.cursorItem.changeInstrument(numInst)
