
import ast          # for string-to-data conversion
import math
import sys
import copy
from PyQt4 import QtGui, QtCore

import pyaudio
import wave

class AudioTrack:
    def __init__(*args, **kwargs):
        self = args[0]
        self._parent = args[1]
        self.scene = self._parent.scene
        
        # note: all positions in this class are absolute
        # position offset
        self.x0 = 0
        self.y0 = 0
        
        self.dx = 20    # default rectangle width
        self.dy = 20    # default rectangle height
                        # used here only for spacing elements

        # store audio variables here

        self.shadedItems = []
        self.copiedItems = []

        self.barLineItems = []
        self.sectionLineItems = []
        self.tickMarkItems = []
        self.lyricsItems = []
        self.floatingItems = []
                                    
        self.numberZValue = 1
        self.tuningZValue = 50
        self.numberBackgroundZValue = -15
        self.gridZValue = -20
        self.stringZValue = -20
#        self.cursorZValue = -10
        self.barLineZValue = -15
        self.sectionLineZValue = -14
        self.tickMarkZValue = -15
                        
        self.selectionIndices = [0, 0, 0, 0]
        self.copiedSelectionIndices = [0, 0, 0, 0]
        self.selectionCoordinates = [0, 0, 0, 0]
        self.copiedSelectionCoordinates = [0, 0, 0, 0]

        if 'hasVocals' in kwargs:
            if kwargs['hasVocals'] == 'True':
                self.hasVocals = True
            else:
                self.hasVocals = False
        else:
            self.hasVocals = False
        
        if 'numXGrid' in kwargs:
            self.setNumXGrid(int(kwargs['numXGrid']))
        else:
            self.setNumXGrid(4000)
        if 'numYGrid' in kwargs:
            self.setNumYGrid(int(kwargs['numYGrid']))
        else:
            self.setNumYGrid(6)
        
        self.calculateBoundsAndMargins()
        
                
    def calculateBoundsAndMargins(self):
        if self.hasVocals:
            self.vocalsFontSize = 16
            self.vocalsMar = 10     # margin above and below vocals
            self.vocalsHeight = 40  # default for one line of text, is expandable
        else:
            self.vocalsFontSize = 16
            self.vocalsMar = 0
            self.vocalsHeight = 0

        # calculate bounds
        self.height = self.numYGrid*self.dy + 2*self.vocalsMar + self.vocalsHeight
        self.width = self.numXGrid*self.dx
                        
    def drawStuff(self):
        self.drawWaveform()
#        self.drawBarLineItems()
#        self.drawTickMarkItems()
#        self.drawSectionLineItems()
        self.drawLyricsBoundary()
        self.addButtons()

    def drawWaveform(self):
        print('drawWaveform()')
                        
    def setTextItemPosition(self, items):
        iPos, jPos, textItem, rectItem, val = items
        
        tw = textItem.boundingRect().width()
        th = textItem.boundingRect().height()
        x1 = self.convertIndexToPositionX(iPos) + self.dx/2 - tw/2
        y1 = self.convertIndexToPositionY(jPos) + self.dy/2 - th/2
        textItem.setPos(x1, y1)        
        x2 = x1 + tw
        y2 = y1 + th
        rectItem.setPolygon(QtGui.QPolygonF([
            QtCore.QPoint(x1,y1), 
            QtCore.QPoint(x1,y2), 
            QtCore.QPoint(x2,y2), 
            QtCore.QPoint(x2,y1)]))        
                
            
    def drawBarLineItems(self):
        # initialize bar lines
        
        # to begin with, bars will be located every 16 spaces
        numBarLines = int(math.floor(self.numXGrid / 16)) + 1
        
        # upper and lower bounds
        y1 = self.convertIndexToPositionY(0)
        y2 = self.convertIndexToPositionY(self.numYGrid)
        
        for i in range(0, numBarLines):
            x1 = self.convertIndexToPositionX((i-1)*16)
            x2 = x1
            self.barLineItems.append(QtGui.QGraphicsLineItem(x1, y1, x2, y2))
            self.barLineItems[i].setPen(QtCore.Qt.black)
            self.barLineItems[i].setZValue(self.barLineZValue)
            self.scene.addItem(self.barLineItems[i])
            
    def drawTickMarkItems(self):
        numTickMarks = int(math.floor(self.numXGrid / 4)) + 1
        
        y1 = self.convertIndexToPositionY(self.numYGrid)
        y2 = y1 + 10
        
        for i in range(0, numTickMarks-1):
            x1 = self.convertIndexToPositionX(i*4 + 0.5)
            x2 = x1
            tickMarkItem = QtGui.QGraphicsLineItem(x1, y1, x2, y2)
            tickMarkItem.setPen(QtCore.Qt.gray)
            tickMarkItem.setZValue(self.tickMarkZValue)
            self.tickMarkItems.append(tickMarkItem)
            self.scene.addItem(tickMarkItem)
            
            
    def drawSectionLineItems(self):
        # initialize the thicker lines that separate sections
        # to begin with, the whole track's just one section

        # upper and lower bounds
        y1 = self.convertIndexToPositionY(0) - 5
        y2 = self.convertIndexToPositionY(self.numYGrid) + 5
        
        x1 = self.convertIndexToPositionX(0)
        x2 = x1
        self.sectionLineItems.append(QtGui.QGraphicsLineItem(x1, y1, x2, y2))
        self.sectionLineItems[0].setPen(QtGui.QPen(QtCore.Qt.black, 3))
        self.sectionLineItems[0].setZValue(self.sectionLineZValue)
        self.scene.addItem(self.sectionLineItems[0])

        x1 = self.convertIndexToPositionX(self.numXGrid)
        x2 = x1
        self.sectionLineItems.append(QtGui.QGraphicsLineItem(x1, y1, x2, y2))
        self.sectionLineItems[1].setPen(QtGui.QPen(QtCore.Qt.black, 3))
        self.sectionLineItems[1].setZValue(self.sectionLineZValue)
        self.scene.addItem(self.sectionLineItems[1])
                                        
    def toggleTrackPlayback(self):
        print('toggleTrackPlayback')
            
    def addButtons(self):
        # play button
        self.playButton = QtGui.QPushButton("play")
        self.playButton.setParent(self._parent._parent)
        self.playButton.setGeometry(self.left() - 50, self.trackTop(), 30, 30)
        QtCore.QObject.connect(self.playButton, QtCore.SIGNAL("released()"), 
            self.toggleTrackPlayback)
        
        # add everything to self.floatingItems list
        self.floatingItems = [self.playButton]
                                
    def drawVocals(self):
        pass
        
    def addLyricsRegion(self):
        self.hasVocals = True
        self.adjustPositions()
                
    def removeLyricsRegion(self):
        self.hasVocals = False
        self.adjustPositions()
        
    def adjustPositions(self):
        self.calculateBoundsAndMargins()

                    
    def isPositionInsideBoundary(self, xPos, yPos):
        if (xPos >= self.left() and xPos < self.right() and
            yPos >= self.top() and yPos < self.bottom()):
            return True
        else:
            return False      
        
    def isPositionOnLyrics(self, xPos, yPos):
        if self.hasVocals == True:
            isTooHigh = (yPos < self.lyricsTop())
            isTooLow = (yPos >= self.trackTop())
            isTooLeft = (xPos < self.left())
            isTooRight = (xPos >= self.right())
            return not (isTooHigh or isTooLow or isTooLeft or isTooRight)
        else:
            return False
            
    def top(self):
        return self.y0
    
    def bottom(self):
        return self.y0 + self.height
        
    def trackTop(self):
        return self.top() + 2*self.vocalsMar + self.vocalsHeight
        
    def trackBottom(self):
        return self.bottom()
        
    def lyricsTop(self):
        return self.top() + self.vocalsMar
        
    def lyricsBottom(self):
        return self.top() + self.vocalsMar + self.vocalsHeight
        
    def left(self):
        return self.x0
        
    def right(self):
        return self.x0 + self.width

    def setNumXGrid(self, numXGrid):
        self.numXGrid = numXGrid
    
    def setNumYGrid(self, numYGrid):
        self.numYGrid = numYGrid
        self.numStrings = self.numYGrid
                
    def setX0(self, x0):
        self.x0 = x0
        
    def setY0(self, y0):
        self.y0 = y0
        
    def setFocus(self):
        pass
        
    def removeFocus(self):
        pass
            
    def shadeSelectedRegion(self, x11, y11, x22, y22):
        pass
            
    def isSomethingSelected(self):
        return False

    def isSomeRegionSelected(self):
        return False
#        x = self.selectionCoordinates
#        return self.isPartOfRegionOnStrings(x[0], x[1], x[2], x[3])
            
    def wasSomeRegionCopied(self):
        return False
#        x = self.copiedSelectionCoordinates
#        return self.isPartOfRegionOnStrings(x[0], x[1], x[2], x[3])
            
    def cutSelectedRegion(self):
        pass

    def copySelectedRegion(self):
        pass
                
    def copySelectionCoordinates(self):
        self.copiedSelectionCoordinates = self.selectionCoordinates[:]
        self.copiedSelectionIndices = self.selectionIndices[:]
        
    def removeSelectedRegion(self):
        pass
#        iPos1, jPos1, iPos2, jPos2 = self.selectionIndices
#        self.removeNumbersFromRegion(iPos1, jPos1, iPos2, jPos2)

    def pasteSelectedRegion(self, iPos):
        pass
                    
    def getCopiedSelectionCoordinates(self):
        x = self.copiedSelectionCoordinates
        # check mins and maxes
        return [min(x[0], x[2]), min(x[1], x[3]), max(x[0], x[2]), max(x[1], x[3])]
                        

    def unSelect(self):
        pass
                                    
    def setLyrics(self, text):
        self.lyricsItem = QtGui.QGraphicsTextItem(text)
        x = self.left()
        y = self.lyricsTop() + self.lyricsItem.boundingRect().height() / 2
        
        self.lyricsItem.setPos(x, y)
    
        x1 = self.left()
        x2 = self.right()
        y1 = self.lyricsTop()
        y2 = self.lyricsBottom()
#        self.lyricsItem.setRect(QtCore.QRect(x1, y1, x2, y2))

#        self.lyricsItem.setGeometry(x, y, 
#        self.lyricsItem.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.lyricsItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.lyricsItem.setZValue(50)
        self.scene.addItem(self.lyricsItem)
        
    def drawLyricsBoundary(self):
        if self.hasVocals == True:
            x1 = self.left()
            x2 = self.right()
            y1 = self.lyricsTop()
            y2 = self.lyricsBottom()
            w = x2 - x1
            h = y2 - y1
            self.lyricsBoundary = QtGui.QGraphicsRectItem(x1, y1, w, h)
            self.lyricsBoundary.setPen(QtCore.Qt.black)
            self.lyricsBoundary.setBrush(QtCore.Qt.transparent)
            self.scene.addItem(self.lyricsBoundary)
            
#    def getLyricsAtPosition(self, xPos, yPos):

            
    def scrollFloatingItems(self, dx, dy):
        # buttons and stuff
        for i in range(0, len(self.floatingItems)):
            rect = self.floatingItems[i].geometry()
            self.floatingItems[i].setGeometry(rect.x(), rect.y()+dy, rect.width(), rect.height())
            
        # tuning
        for i in range(0, len(self.tuningTextItems)):
            item = self.tuningTextItems[i][1]
            pos = item.scenePos()
            old_pos = pos
            item.setPos(pos.x()-dx, pos.y())        
        
        
    def isTab(self):
        return False
        
    def isAudio(self):
        return True
        
    def startPlayback(self):
        print('start audio playback')
    
