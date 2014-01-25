# -*- coding: utf-8 -*-

import time
import random
import sys
from PyQt4 import QtGui, QtCore

import Tracks
import MidiPlayer
import SelectionRectangle
import Cursor

import fluidsynth


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        self.prev_saveFilename = ''
    
        super(MainWindow, self).__init__()
        
        self.midiPlayer = MidiPlayer.MidiPlayer()        
                
        self.initUI()
        
    def initUI(self):
        
        # menus and statusbar
        self.statusBar()
        
        # add TablatureWindow
        self.tabWidget = QtGui.QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle('FAIT Tablature Editor')    

        self.startNewTablature()
        self.tabWidget.addTab(self.tablatureWindow, 'Untitled')
        self.tablatureWindow.setFocus()
        
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        editMenu = menubar.addMenu('&Edit')
        
        newFile = QtGui.QAction(QtGui.QIcon('new.png'), 'New Tab', self)
        newFile.setShortcut(QtGui.QKeySequence.New)
        newFile.setStatusTip('New tab')
        newFile.triggered.connect(self.startNewTablature)
        
        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open...', self)
        openFile.setShortcut(QtGui.QKeySequence.Open)
        openFile.setStatusTip('Open file')
        openFile.triggered.connect(self.showOpenDialog)
        
        saveAsFile = QtGui.QAction(QtGui.QIcon('save.png'), 'Save As...', self)
        saveAsFile.setShortcut(QtGui.QKeySequence.SaveAs)
        saveAsFile.setStatusTip('Save file')
        saveAsFile.triggered.connect(self.showSaveAsDialog)
        
        saveFile = QtGui.QAction(QtGui.QIcon('save.png'), 'Save', self)
        saveFile.setShortcut(QtGui.QKeySequence.Save)
        saveFile.setStatusTip('Save file')
        saveFile.triggered.connect(self.saveAsPreviousFilename)
        
        fileMenu.addAction(newFile)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)

        cutSelection = QtGui.QAction('Cut', self)
        cutSelection.setShortcut(QtGui.QKeySequence.Cut)
        cutSelection.setStatusTip('Cut')
        cutSelection.triggered.connect(self.cutSelection)

        copySelection = QtGui.QAction('Copy', self)
        copySelection.setShortcut(QtGui.QKeySequence.Copy)
        copySelection.setStatusTip('Copy')
        copySelection.triggered.connect(self.copySelection)

        pasteSelection = QtGui.QAction('Paste', self)
        pasteSelection.setShortcut(QtGui.QKeySequence.Paste)
        pasteSelection.setStatusTip('Paste')
        pasteSelection.triggered.connect(self.pasteSelection)

        editMenu.addAction(cutSelection)
        editMenu.addAction(copySelection)
        editMenu.addAction(pasteSelection)
        
#        selectNextWord = QtGui.QAction('Paste', self)
#        selectNextWord.setShortcut(QtGui.QKeySequence.Paste)
#        selectNextWord.triggered.connect(self.tablatureWindow.selectNextWord)


        self.positionWindow()       # center and almost maximize window

        self.show()
        
    def positionWindow(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        width = QtGui.QDesktopWidget().availableGeometry().width() - 100
        height = QtGui.QDesktopWidget().availableGeometry().height() - 100
        self.resize(width, height)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
        
    def showSaveAsDialog(self):
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', 
                '~/Documents/coding/Tab Program/')
        if fname != '':     # if "cancel" was not pressed
            f = open(fname, 'w')
        
            with f:
                f.write(self.tablatureWindow.getSaveFileData())                
                self.prev_saveFilename = fname 
                self.tabWidget.setTabText(0, fname)
                
    def saveAsPreviousFilename(self):
        if self.prev_saveFilename == '':            # if this is a new file and hasn't been saved yet
            self.showSaveAsDialog()
        else:
            fname = self.prev_saveFilename
            f = open(fname, 'w')
            
            with f:
                f.write(self.tablatureWindow.getSaveFileData())
                
    def showOpenDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                '~/Documents/coding/Tab Program/')
        
        # in the future, check if current file has been saved
        
        if fname != '':
            f = open(fname, 'r')
            
            with f:
                self.tablatureWindow = TablatureWindow(self.midiPlayer, loadFile=f)
                self.tabWidget.removeTab(0)
                self.tabWidget.addTab(self.tablatureWindow, fname)
                self.tablatureWindow.setFocus()

    def startNewTablature(*args, **kwargs):
        self = args[0]
        self.tablatureWindow = TablatureWindow(self.midiPlayer)
        self.tabWidget.removeTab(0)
        self.tabWidget.addTab(self.tablatureWindow, 'Untitled')
        self.tablatureWindow.setFocus()
        
    def cutSelection(self):
        self.tablatureWindow.cutSelection()

    def copySelection(self):
        self.tablatureWindow.copySelection()
        
    def pasteSelection(self):
        self.tablatureWindow.pasteSelection()


class TablatureWindow(QtGui.QGraphicsView):    
    def __init__(*args, **kwargs):
        start_time = time.time()

        self = args[0]                
        self.midiPlayer = args[1]

        QtGui.QGraphicsView.__init__(self)    
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)

        if 'loadFile' in kwargs:
            self.loadTracks(kwargs['loadFile'])
        else:
            self.tracks = [Tracks.Track(self.scene), Tracks.Track(self.scene, hasVocals='True'), 
                Tracks.Track(self.scene), Tracks.Track(self.scene)]
            self.initializeTracks()

            self.scene.setSceneRect(QtCore.QRectF(0, 0, 
                    self.windowSizeX, self.windowSizeY))

        self.centerOn(0,0)

        self.initializeGraphics()
        
        self.defineKeyGroups()
        
        end_time = time.time()
        print("Initializing time was %g seconds" % (end_time - start_time))
        
    def initializeTracks(self):
        self.prev_iCursor = 0
        self.prev_jCursor = 0
        self.prev_trackFocusNum = 0
        self.trackFocusNum = 0       # to begin with, focus is on track 0
        
        self.xMar = 50          # margins from top and left side of window to topmost track
        self.yMar = 50
        self.trackMar = 50      # margin between tracks
        
        self.tracks[0].setX0(self.xMar)
        self.tracks[0].setY0(self.yMar)
        for i in range(0, len(self.tracks)):
            if i > 0:
                self.tracks[i].setX0(self.xMar)
                self.tracks[i].setY0(self.tracks[i-1].graphics.y0 + \
                            self.tracks[i-1].graphics.height + self.trackMar)
            self.tracks[i].drawStuff()

        # calculate window size
        self.windowSizeX = self.tracks[0].graphics.x0 + \
                        self.tracks[0].graphics.dx*3 + self.tracks[0].width()
        self.windowSizeY = self.tracks[0].graphics.y0
        for i in range(0, len(self.tracks)):
            self.windowSizeY = self.windowSizeY + self.tracks[i].height() + self.trackMar
        
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

        # check for standard key combinations
        #standard

        modifiers = QtGui.QApplication.keyboardModifiers()
        
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
                    self.tracks[i].moveCursorUp()
                if key == QtCore.Qt.Key_Down:
                    if 'bottom' in sides:
                        self.selectionRectangle.expandDown()
                    elif 'top' in sides and 'bottom' not in sides:
                        self.selectionRectangle.contractDown()
                    self.tracks[i].moveCursorDown()
                if key == QtCore.Qt.Key_Left:
                    if 'left' in sides:
                        self.selectionRectangle.expandLeft()
                    elif 'right' in sides and 'left' not in sides:
                        self.selectionRectangle.contractLeft()
                    self.tracks[i].moveCursorLeft()
                if key == QtCore.Qt.Key_Right:
                    if 'right' in sides:
                        self.selectionRectangle.expandRight()
                    elif 'left' in sides and 'right' not in sides:
                        self.selectionRectangle.contractRight()
                    self.tracks[i].moveCursorRight()
                    
                #self.selectionRectangle.updateSelectionRectangle()
#                        for i in range(0, len(self.tracks)):
#            self.tracks[i].shadeSelectedNumbers(x1, y1, x20, y20)
                c = self.selectionRectangle.rect()
                for i in range(0, len(self.tracks)):
                    # -1's are to make sure selection area doesn't select more than intended
                    self.tracks[i].shadeSelectedNumbers(c.left(), c.top(), c.right()-1, c.bottom()-1)    

            else:    # if shift is not held
                self.unSelect()
                if key == QtCore.Qt.Key_Up:
                    self.tracks[i].moveCursorUp()
                if key == QtCore.Qt.Key_Down:
                    self.tracks[i].moveCursorDown()
                if key == QtCore.Qt.Key_Left:
                    self.tracks[i].moveCursorLeft()
                if key == QtCore.Qt.Key_Right:
                    self.tracks[i].moveCursorRight()
            self.updateCursorGraphics()

            
        # check for number input
        if key in self.numberKeys:
            self.unSelect()
            num = int(key)-48               # number typed in

            val = self.tracks[i].getFromTab()     # current number at space
            if val == -1:
                # if no number is already there, go ahead and add the number
                # this will also update the graphics
                self.tracks[i].addToTab(num)
                
                self.updateCursorGraphics()     # make new number white
            
                # convert entered number to pitch and play note
                pitch = self.tracks[i].convertNumberToPitch(self.tracks[i].jCursor, num)
                self.midiPlayer.playNote(self, i, pitch)
            else:
                # if there is a number, check if could be the first digit of a two-digit number
                maxVal = 24         # highest number allowed
                maxDigit = (maxVal - (maxVal % 10)) / 10        # maximum second digit
                if val in range(1, maxDigit+1):
                    # add second digit to number
                    num2 = val*10 + num
                    self.tracks[i].addToTab(num2)
                    self.updateCursorGraphics()
                    pitch = self.tracks[i].convertNumberToPitch(self.tracks[i].jCursor, num2)
                    self.midiPlayer.playNote(self, i, pitch)
                else:
                    # otherwise, just add new number
                    self.tracks[i].addToTab(num)
                    self.updateCursorGraphics()
                    pitch = self.tracks[i].convertNumberToPitch(self.tracks[i].jCursor, num)
                    self.midiPlayer.playNote(self, i, pitch)                
            
        # spacebar, backspace, or delete remove data
        if key in (QtCore.Qt.Key_Space, QtCore.Qt.Key_Backspace):
            if self.selectionRectangle.rect().width() == 0 or \
                    self.selectionRectangle.rect().height() == 0:
                self.tracks[i].removeFromTab()
            else:
                # remove selected items
                for j in range(len(self.tracks)):
                    self.tracks[j].removeSelectedRegion()
            self.unSelect()
            
        # insert and delete
        #, QtCore.Qt.Key_Delete
                        
                    
    def mousePressEvent(self, e):
        self.unSelect()
        
        scenePoint = self.mapToScene(e.x(), e.y())
        xPos = scenePoint.x()
        yPos = scenePoint.y()
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
        self.changeTrackFocus(i1)
        if self.tracks[i1].isPositionOnStrings(xPos, yPos):
            self.tracks[i1].moveCursorToPosition(xPos, yPos)
        self.updateCursorGraphics()
                
    def mouseMoveEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton:
            scenePoint = self.mapToScene(e.x(), e.y())
            xPos = scenePoint.x()
            yPos = scenePoint.y()
            
            # shade all rectangles within this area
            self.selectionRectangle.updateSelectionRectangle(
                [self.mousePressedX, self.mousePressedY, xPos, yPos])
            self.updateCursorGraphics()

            # when selecting, we want the cursor to follow the rectangle
            i1 = self.whichTrackHasPoint(xPos, yPos)
            self.changeTrackFocus(i1)
            x1 = self.tracks[i1].returnAlignedCoordX(xPos, 'left')
            y1 = self.tracks[i1].returnAlignedCoordY(yPos, 'top')
            self.tracks[i1].moveCursorToPosition(x1, y1)      
            self.updateCursorGraphics()              
            
    def mouseReleaseEvent(self, e):
        pass
                        
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
            iPos = self.tracks[self.trackFocusNum].iCursor
            
            copiedStuff = self.tracks[i].getCopiedItems()
            self.tracks[self.trackFocusNum].pasteFromOtherTrack(iPos, copiedStuff)
            
            # show pastedSelectionRectangle at coordinates
            xx = self.copiedSelectionRectangle.rect()
            x = [xx.x(), xx.y(), xx.x() + xx.width(), xx.y() + xx.height()]
            # shift to cursor position
            newX0 = self.tracks[self.trackFocusNum].graphics.convertIndexToPositionX(iPos)
            delta_y = self.tracks[self.trackFocusNum].trackTop() - self.tracks[i].trackTop()
            newY0 = x[1] + delta_y
            self.pastedSelectionRectangle.setRect(newX0, newY0, x[2]-x[0], x[3]-x[1])
            self.update()
            
        # if more than one track selected, paste only those tracks to the same tracks
        elif len(selectedTrackNums) > 1:
            iPos = self.tracks[self.trackFocusNum].iCursor
            for i in selectedTrackNums:
                self.tracks[i].pasteSelectedRegion(iPos)
                
            xx = self.copiedSelectionRectangle.rect()
            x = [xx.x(), xx.y(), xx.x() + xx.width(), xx.y() + xx.height()]
            # shift to cursor position
            newX0 = self.tracks[selectedTrackNums[0]].graphics.convertIndexToPositionX(iPos)
            self.pastedSelectionRectangle.setRect(newX0, x[1], x[2]-x[0], x[3]-x[1])
            self.update()

        self.updateCursorGraphics()
        
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
                        
    def initializeGraphics(self):
        
        # create cursor
        i = self.trackFocusNum
#        c = self.tracks[i].getCursorQRect()
#        self.cursorItem = Cursor.Cursor(c.left(), c.top(), c.width(), c.height())
        self.cursorItem = QtGui.QGraphicsRectItem(self.tracks[i].getCursorQRect())
        self.scene.addItem(self.cursorItem)
        self.cursorItem.setPen(QtCore.Qt.black)
        self.cursorItem.setBrush(QtCore.Qt.black)
        self.cursorItem.setZValue(-10)           # have cursor appear below numbers so 
                                                # cursor doesn't block them
        self.updateCursorGraphics()             # in this case, makes cursor text inverted
        
        # set focus
        self.tracks[self.trackFocusNum].setFocus()
        
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
            
    def changeTrackFocus(self, newTrackFocusNum):
        if newTrackFocusNum != self.trackFocusNum:
            self.tracks[newTrackFocusNum].setFocus()
            self.tracks[self.trackFocusNum].removeFocus()
        self.trackFocusNum = newTrackFocusNum
        # prev_trackFocusNum will be updated once updateCursorGraphics() is run        
                                                           
                              
    def updateCursorGraphics(self): 
        # we assume cursor positions have already been updated in tracks[i].data
    
        # move cursor item
        i = self.trackFocusNum
        x11 = self.tracks[i].graphics.convertIndexToPositionX(self.tracks[i].iCursor)
        y11 = self.tracks[i].graphics.convertIndexToPositionY(self.tracks[i].jCursor)
#        self.cursorItem.setPos(x11, y11)
        w = self.cursorItem.rect().width()
        h = self.cursorItem.rect().height()
        self.cursorItem.setRect(x11, y11, w, h)
        
        
        # if outside of viewport, scroll window
        cursorPoint = self.mapFromScene(x11, y11)
        x_cur, y_cur = [cursorPoint.x(), cursorPoint.y()]

        viewportCenterPoint = self.mapToScene(self.viewport().rect().center())
        x = viewportCenterPoint.x()
        y = viewportCenterPoint.y()

        if x_cur > self.width()-80:
            # we translate by moving center
            self.centerOn(x+120, y+1)           # "+1" is to correct for a bug in "centerOn"
        elif x_cur < 10:
            self.centerOn(x-120, y+1)
            
        viewportCenterPoint = self.mapToScene(self.viewport().rect().center())
        x = viewportCenterPoint.x()
        y = viewportCenterPoint.y()
        
        if y_cur > self.height()-80:
            self.centerOn(x+1, y+80)
        elif y_cur < 80:
            self.centerOn(x+1, y-80)

        self.update()
        
        # make number at previous cursor position black
        i = self.prev_iCursor
        j = self.prev_jCursor
        k = self.prev_trackFocusNum
        self.tracks[k].unShadeAtIndex(i,j)

        # make number at current position white
        k = self.trackFocusNum
        i = self.tracks[k].iCursor
        j = self.tracks[k].jCursor
        self.tracks[k].shadeAtIndex(i, j)
        
        self.updateCursorInfo()
        self.update()  

    def updateCursorInfo(self):
        self.prev_trackFocusNum = self.trackFocusNum
        self.prev_iCursor = self.tracks[self.trackFocusNum].iCursor
        self.prev_jCursor = self.tracks[self.trackFocusNum].jCursor
            
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
            st = st + '\n'
            st = st + '\n'
        return st
        
    def loadTracks(self, file):
        dataStrings = []
        
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
                
                file.readline()                     # blank
                file.readline()                     # blank
                
                self.tracks.append(Tracks.Track(self.scene, numXGrid=str(numXGrid1), 
                    numYGrid=str(numYGrid1), hasVocals=hasVocals1))
        
        # draw tracks' grids, tunings, and cursor, and arrange tracks
        self.initializeTracks()
        
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 
                self.windowSizeX, self.windowSizeY))

        # now that tracks are arranged, load track data
        for i in range(0, len(self.tracks)):
            self.tracks[i].loadFromString(dataStrings[i])

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 
