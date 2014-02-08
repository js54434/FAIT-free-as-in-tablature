# contains classes and methods relating to individual tracks

import ast          # for string-to-data conversion
import math
import sys
import copy
from PyQt4 import QtGui, QtCore

# class for containing information about a track
class Track:
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

        self.numberFontOdd = QtGui.QFont('Helvetica', 11)
        self.numberFontEven = QtGui.QFont('Helvetica', 11)

        self.numberItems = []       # list of QGraphicsItems corresponding
                                    # to displayed text of numbers
        self.shadedItems = []
        self.copiedItems = []

        self.stringItems = []    # contains QGraphicsLineItems corresponding to each string
        self.barLineItems = []
        self.sectionLineItems = []
        self.tickMarkItems = []
        self.tuningTextItems = []
                                    
        self.numberZValue = 1
        self.tuningZValue = 0
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
        # set default lyrics
        
        if 'numXGrid' in kwargs:
            self.setNumXGrid(int(kwargs['numXGrid']))
        else:
            self.setNumXGrid(4000)
        if 'numYGrid' in kwargs:
            self.setNumYGrid(int(kwargs['numYGrid']))
        else:
            self.setNumYGrid(6)

        self.tunings = {
            'standard' : [40, 45, 50, 55, 59, 64],
            'dropped-D' : [38, 45, 50, 55, 59, 64],
            'DADGAD' : [38, 45, 50, 55, 57, 62]}
        if 'tuning' in kwargs:
            if kwargs['tuning'] in self.tunings:
                self.setTuning(kwargs['tuning'])
            else:
                self.setTuning('standard')
                print('unknown tuning specified')
        else:
            self.setTuning('standard')

        

        self.calculateBoundsAndMargins()

        if 'hasVocals' in kwargs:
            self.setLyrics("Hello world")

        
        # self.drawStuff()
        
    # return pitch in midi integer notation
    def convertNumberToPitch(self, jPos, pitchNum):
        return pitchNum + self.stringTuning[(self.numStrings-1) - jPos]   
                
    def setTuning(self, tuningStr):
        if self.numYGrid == 6:
            if tuningStr in self.tunings:
                tuningNumbers = self.tunings[tuningStr]
            else: 
                tuningNumbers = [40, 45, 50, 55, 59, 64]
        else:
            # start from lowest string and count upward
            tuningNumbers = [40, 45, 50, 55, 59, 64]
            for i in range(6, self.numYGrid):
                tuningNumbers.append(64 + 5*(i-6+1))
                
        self.stringTuning = tuningNumbers
        
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
        self.drawTuning()
        self.drawStringItems()       
        self.drawBarLineItems()
        self.drawTickMarkItems()
        self.drawSectionLineItems() 
                        
    def addToTab(self, iPos, jPos, val):
        # first check if we have an asterisk
        if val == '*':
            items = self.getGraphicsItems(iPos, jPos)
            if len(items) == 0:
                text = val
                textItem = QtGui.QGraphicsSimpleTextItem(text)
                textItem.setZValue(self.numberZValue)
                textItem.setBrush(QtCore.Qt.black)
                if iPos % 2 == 1:
                    textItem.setFont(self.numberFontOdd)
                else:
                    textItem.setFont(self.numberFontEven)
                self.scene.addItem(textItem)
                
                # little background rectangle to block strings from showing
                rectItem = QtGui.QGraphicsPolygonItem()
                rectItem.setZValue(self.numberBackgroundZValue)
                rectItem.setBrush(QtCore.Qt.white)
                rectItem.setPen(QtCore.Qt.transparent)
                
                self.scene.addItem(rectItem)
                self.setTextItemPosition([iPos, jPos, textItem, rectItem, val])
                self.numberItems.append([iPos, jPos, textItem, rectItem, val])
                
            elif len(items) > 0:
                items = self.getGraphicsItems(iPos, jPos)
                textItem = items[2]
                rectItem = items[3]
                textItem.setText(str(val))
                self.setTextItemPosition(items)     # adjust position for new number
                items[4] = val
            else:
                print('Warning: ' + str(len(items)) + ' numbers at ' + str(iPos) + ', ' + str(jPos))
        
        # check if number's already there; if not, make new graphics item
        items = self.getGraphicsItems(iPos, jPos)
        if len(items) == 0:
            text = str(val)
            textItem = QtGui.QGraphicsSimpleTextItem(text)
            textItem.setZValue(self.numberZValue)
            textItem.setBrush(QtCore.Qt.black) 
            if iPos % 2 == 1:
                textItem.setFont(self.numberFontOdd)
            else:
                textItem.setFont(self.numberFontEven)
                
            # add to scene
            self.scene.addItem(textItem)

            # little background rectangle to block strings from showing
            rectItem = QtGui.QGraphicsPolygonItem()
            rectItem.setZValue(self.numberBackgroundZValue)
            rectItem.setBrush(QtCore.Qt.white)
            rectItem.setPen(QtCore.Qt.transparent)

            self.scene.addItem(rectItem)
        
            self.setTextItemPosition([iPos, jPos, textItem, rectItem, val])
        
            # add to list
            self.numberItems.append([iPos, jPos, textItem, rectItem, val])
        elif len(items) > 0:
            # change item that was already there
            items = self.getGraphicsItems(iPos, jPos)
            textItem = items[2]
            rectItem = items[3]
            textItem.setText(str(val))
            self.setTextItemPosition(items)     # adjust position for new number
            items[4] = val
        else:
            print('Warning: ' + str(len(items)) + ' numbers at ' + str(iPos) + ', ' + str(jPos))
        
    def removeFromTab(self, iPos, jPos):
        itemList = self.getGraphicsItems(iPos, jPos)
        if len(itemList) > 0:        
            textItem = itemList[2]
            rectItem = itemList[3]
        
            # remove from list
            self.numberItems.remove(itemList)
                
            # remove from scene
            self.scene.removeItem(textItem)
            self.scene.removeItem(rectItem)

            # delete?
            
    def getFromTab(self, iPos, jPos):
        itemList = self.getGraphicsItems(iPos, jPos)
        if len(itemList) == 0:
            return -1
        elif len(itemList) > 0:
            return itemList[4]
        else:
            print('Warning: wrong number of items at ' + str(iPos) + ', ' + str(jPos))
            
    def removeNumbersFromRegion(self, iPos1, jPos1, iPos2, jPos2):
        possibleTuples = [x for x in self.numberItems \
                if x[0] in range(iPos1, iPos2+1) and \
                    x[1] in range(jPos1, jPos2+1)]
        for i in range(0, len(possibleTuples)):
            itemList = possibleTuples[i]
            # remove from list
            self.numberItems.remove(itemList)
            
            # remove from scene
            self.scene.removeItem(itemList[2])  # textItem
            self.scene.removeItem(itemList[3])  # rectItem
                            
    def getGraphicsItems(self, iPos, jPos):
        possibleTuples = [x for x in self.numberItems \
                if x[0] == iPos and x[1] == jPos]
        if len(possibleTuples) > 0:
            return possibleTuples[0]
        else:
            return []
                
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
                
    def drawStringItems(self):
        # draw strings
        for i in range(0, self.numYGrid):
            x1 = self.convertIndexToPositionX(0)
            y1 = self.convertIndexToPositionY(0.5+i)
            x2 = self.convertIndexToPositionX(self.numXGrid)
            y2 = y1
            self.stringItems.append(QtGui.QGraphicsLineItem(x1, y1, x2, y2))
            self.stringItems[i].setPen(QtCore.Qt.lightGray)
            self.stringItems[i].setZValue(self.stringZValue)
            self.scene.addItem(self.stringItems[i])
            
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
        
        for i in range(0, numTickMarks):
            x1 = self.convertIndexToPositionX((i-1)*4 + 0.5)
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
                            
    def drawTuning(self):
        for j in range(0, self.numStrings):
            text = self.convertPitchToLetter(self.stringTuning[self.numStrings-1-j])
            textItem = QtGui.QGraphicsSimpleTextItem(text)
            textItem.setBrush(QtCore.Qt.black)
            textItem.setPen(QtCore.Qt.black)
            textItem.setZValue(-10)
               
            # set position
            tw = textItem.boundingRect().width()
            th = textItem.boundingRect().height()
            x1 = self.convertIndexToPositionX(-1)
            x11 = x1 + (self.dx-tw)/2
            y11 = self.convertIndexToPositionY(j) + (self.dy-th)/2
            textItem.setPos(x11,y11)
            self.scene.addItem(textItem)
            self.tuningTextItems.append([j, textItem])
                
    def convertPitchToLetter(self, pitchNum):
        p = pitchNum % 12
        letters = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
        return letters[p]
                
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
        
        # strings
        for i in range(0, self.numYGrid):
            x1 = self.convertIndexToPositionX(0)
            y1 = self.convertIndexToPositionY(0.5+i)
            x2 = self.convertIndexToPositionX(self.numXGrid)
            y2 = y1            
            self.stringItems[i].setLine(x1, y1, x2, y2)
        
        # tuning
        for j in range(0, self.numStrings):
            textItem = self.tuningTextItems[j][1]
            tw = textItem.boundingRect().width()
            th = textItem.boundingRect().height()
            x1 = self.convertIndexToPositionX(-1)
            x11 = x1 + (self.dx-tw)/2
            y11 = self.convertIndexToPositionY(j) + (self.dy-th)/2
            textItem.setPos(x11,y11)            
        
        # numbers
        for j in range(0, len(self.numberItems)):
            items = self.numberItems[j]
            self.setTextItemPosition(items)

    def getCursorIndexX(self, xPos):
        iPos = int(math.floor( (xPos-self.x0)/self.dx ))
        return iPos
    
    def getCursorIndexY(self, yPos):
        y00 = self.y0 + 2*self.vocalsMar + self.vocalsHeight
        jPos = int(math.floor( (yPos-y00)/self.dy ))
        return jPos
                    
    def convertIndexToPositionX(self, iPos):
        return self.x0 + iPos*self.dx

    def convertIndexToPositionY(self, jPos):
        if self.hasVocals == True:
            return self.y0 + 2*self.vocalsMar + self.vocalsHeight + jPos*self.dy    
        else:
            return self.y0 + jPos*self.dy
            
    def getMovedIndexX(self, iPos, direction):
        if direction == 'left':
            if iPos - 1 < 0:
                iMov = iPos
            else:
                iMov = iPos - 1
        elif direction == 'right':
            if iPos + 1 >= self.numXGrid:
                iMov = iPos
            else:
                iMov = iPos + 1
        else:
            print('getMovedIndexX: wrong direction')

        return iMov

    def getMovedIndexY(self, jPos, direction):
        if direction == 'up':
            if jPos - 1 < 0:
                jMov = jPos
            else:
                jMov = jPos - 1
        elif direction == 'down':
            if jPos + 1 >= self.numYGrid:
                jMov = jPos
            else:
                jMov = jPos + 1
        else:
            print('getMovedIndexY: wrong direction')

        return jMov

            
    # return a grid point for a given point
    def returnAlignedCoordX(self, x, direction):
        i = self.getCursorIndexX(x)
        
        if direction == 'left':
            i1 = i
        elif direction == 'right': 
            i1 = i + 1
        else:
            print('returnAlignedCoordX: bad direction')

        if i in range (0, self.numXGrid):          # if inside track strings
            return self.convertIndexToPositionX(i1)
        elif i < 0:                                # too high
            return self.convertIndexToPositionX(i1-i)
        elif i > self.numXGrid-1:                  # too low
            return self.convertIndexToPositionX(self.numXGrid-1 + (i1-i))
        
    def returnAlignedCoordY(self, y, direction):
        i = self.getCursorIndexY(y)
        
        # pick whether we want top or bottom of grid cell
        if direction == 'top':
            i1 = i
        elif direction == 'bottom':
            i1 = i + 1
        elif direction == 'topmost':
            i1 = 0
            i = 0
        elif direction == 'bottommost':
            i = self.numYGrid-1
            i1 = i + 1
        elif direction == 'nextbottommost':
            i = self.numYGrid-1
            i1 = i
        else:
            print('returnAlignedCoordY: bad direction!')
        
        if i in range (0, self.numYGrid):          # if inside track strings
            return self.convertIndexToPositionY(i1)
        elif i < 0:                                # too high
            return self.convertIndexToPositionY(i1-i)
        elif i > self.numYGrid-1:                  # too low
            return self.convertIndexToPositionY(self.numYGrid-1 + (i1-i))
                                 
#    def getCursorQRect(self):
#        x1 = self.convertIndexToPositionX(self.iCursor)
#        y1 = self.convertIndexToPositionY(self.jCursor)
#        x2 = self.convertIndexToPositionX(self.iCursor+1)
#        y2 = self.convertIndexToPositionY(self.jCursor+1)
#        return QtCore.QRectF(x1, y1, x2-x1, y2-y1)

                    
    def isPositionInsideBoundary(self, xPos, yPos):
        if (xPos >= self.left() and xPos < self.right() and
            yPos >= self.top() and yPos < self.bottom()):
            return True
        else:
            return False      

    def isPositionOnStrings(self, xPos, yPos):
        if (xPos >= self.left() and xPos < self.right() and
            yPos >= self.trackTop() and yPos < self.trackBottom()):
            return True
        else:
            return False        
        
    def isPartOfRegionOnStrings(self, x1, y1, x2, y2):
        # no if both coordinates of at least one dimension are on the same
        # side
        # yes otherwise
        isTooHigh = (y1 < self.trackTop() and y2 < self.trackTop())
        isTooLow = (y1 >= self.trackBottom() and y2 >= self.trackBottom())
        isTooLeft = (x1 < self.left() and x2 < self.left())
        isTooRight = (x1 >= self.right() and x2 >= self.right())
        return not (isTooHigh or isTooLow or isTooLeft or isTooRight)
        
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
        
#    def width(self):
#        return self.width
        
#    def height(self):
#        return self.height
        
#    def loadNumberGraphicsFromData(self, data):
#        # data has already been loaded, so we read from that
#        for i in range(0, len(data)):
#            iPos, jPos, val = data[i]
#            self.drawNewNumber(iPos, jPos, val)    
            
    def setFocus(self):
        for i in range(0, self.numYGrid):
            self.stringItems[i].setPen(QtCore.Qt.black)
        
    def removeFocus(self):
        for i in range(0, self.numYGrid):
            self.stringItems[i].setPen(QtCore.Qt.gray)        
            
    def shadeSelectedNumbers(self, x11, y11, x22, y22):
        iPos1 = self.getCursorIndexX(x11)
        jPos1 = self.getCursorIndexY(y11)
        iPos2 = self.getCursorIndexX(x22)
        jPos2 = self.getCursorIndexY(y22)
        self.selectionIndices = [iPos1, jPos1, iPos2, jPos2]
        self.selectionCoordinates = [min(x11,x22), min(y11,y22), max(x11,x22), max(y11,y22)]
        
        # get list of items in this range
        newShadedItems = [x for x in self.numberItems \
                if x[0] in range(iPos1, iPos2+1) and x[1] in range(jPos1, jPos2+1)]
        # now shade them
        for i in range(0, len(newShadedItems)):
            newShadedItems[i][2].setBrush(QtCore.Qt.white)       # make numbers white
            newShadedItems[i][3].setBrush(QtCore.Qt.black)       # make background black

            
        # unshade all self.shadedItems that are no longer selected
        unShadeTheseItems = [x for x in self.shadedItems if x not in newShadedItems]
        for i in range(0, len(unShadeTheseItems)):
            iPos = unShadeTheseItems[i][0]
#            if iPos % 2 == 0:
#                unShadeTheseItems[i][2].setBrush(QtCore.Qt.black)
#            else:                
#                unShadeTheseItems[i][2].setBrush(QtCore.Qt.lightGray)
            unShadeTheseItems[i][2].setBrush(QtCore.Qt.black)
            unShadeTheseItems[i][3].setBrush(QtCore.Qt.white)
            
        self.shadedItems = newShadedItems[:]
            
    def isSomethingSelected(self):
        if len(self.shadedItems) > 0:
            return True
        else:
            return False

    def isSomeRegionSelected(self):
        x = self.selectionCoordinates
        return self.isPartOfRegionOnStrings(x[0], x[1], x[2], x[3])
            
    def wasSomeRegionCopied(self):
        x = self.copiedSelectionCoordinates
        return self.isPartOfRegionOnStrings(x[0], x[1], x[2], x[3])
            
    def cutSelectedRegion(self):
        self.copySelectionCoordinates()
        if self.isSomethingSelected():
            # make a copy
            self.copiedItems = self.cloneItems(self.shadedItems)
            # remove shaded items from scene
            iPos1, jPos1, iPos2, jPos2 = self.selectionIndices
            self.removeNumbersFromRegion(iPos1, jPos1, iPos2, jPos2)
        else:
            self.copiedItems = []

    def copySelectedRegion(self):
        self.copySelectionCoordinates()
        if self.isSomethingSelected():
            self.copiedItems = self.cloneItems(self.shadedItems)
        else:
            self.copiedItems = []
                
    def copySelectionCoordinates(self):
        self.copiedSelectionCoordinates = self.selectionCoordinates[:]
        self.copiedSelectionIndices = self.selectionIndices[:]
        
    def removeSelectedRegion(self):
        iPos1, jPos1, iPos2, jPos2 = self.selectionIndices
        self.removeNumbersFromRegion(iPos1, jPos1, iPos2, jPos2)

    def pasteSelectedRegion(self, iPos):
        if len(self.copiedItems) > 0:
            copiedItems = self.cloneItems(self.copiedItems)
            
            min_iPos = min(self.copiedSelectionIndices[0], self.copiedSelectionIndices[2])
            d_iPos = iPos - min_iPos
            # note: iPos is the cursor of the track in focus, not necessarily of this track

            # remove item at the region we want to copy to
            iPos1, jPos1, iPos2, jPos2 = self.copiedSelectionIndices
            iPos1 = iPos1 + d_iPos
            iPos2 = iPos2 + d_iPos
            self.removeNumbersFromRegion(iPos1, jPos1, iPos2, jPos2)
        
            for i in range(0, len(copiedItems)):
                x = copiedItems[i]
                x[0] = x[0] + d_iPos
                self.setTextItemPosition(x)
                self.numberItems.append(x)
                self.scene.addItem(x[2])     # add number
                self.scene.addItem(x[3])     # add background rectangle
                
        elif len(self.copiedItems) == 0 and self.wasSomeRegionCopied() == True:
            # erase numbers from area
            iPos1, jPos1, iPos2, jPos2 = self.copiedSelectionIndices            
            min_iPos = min(self.copiedSelectionIndices[0], self.copiedSelectionIndices[2])
            d_iPos = iPos - min_iPos
            iPos1 = iPos1 + d_iPos
            iPos2 = iPos2 + d_iPos
            self.removeNumbersFromRegion(iPos1, jPos1, iPos2, jPos2)
            
#        elif len(self.copiedItems) == 0 and self.wasSomeRegionCopied() == False:
#            print('nothing selected')
            
    def getCopiedItems(self):
        return self.cloneItems(self.copiedItems)
        
    def getCopiedSelectionCoordinates(self):
        x = self.copiedSelectionCoordinates
        # check mins and maxes
        return [min(x[0], x[2]), min(x[1], x[3]), max(x[0], x[2]), max(x[1], x[3])]
        
    def pasteFromOtherTrack(self, iPos, copiedItems):
        self.copiedItems = self.cloneItems(copiedItems)
        self.pasteSelectedRegion(iPos)
                
    def cloneItems(self, itemList):
        # clone the list and return selected items
        copiedItemsClone = []
        for i in range(0, len(itemList)):            
            x = itemList[i]
            text = x[2].text()
            textItem = QtGui.QGraphicsSimpleTextItem(text)
            textItem.setZValue(self.numberZValue)
            textItem.setBrush(QtCore.Qt.black)
            
            # little background rectangle to block strings from showing
            rectItem = QtGui.QGraphicsPolygonItem()
            rectItem.setZValue(self.numberBackgroundZValue)
            rectItem.setBrush(QtCore.Qt.white)
            rectItem.setPen(QtCore.Qt.transparent)
    
            iPos = self.getCursorIndexX(x[3].boundingRect().left())
            jPos = self.getCursorIndexY(x[3].boundingRect().top())
            val = x[4]
            self.setTextItemPosition([iPos, jPos, textItem, rectItem, val])
        
            # add to list
            y = [x[0], x[1], textItem, rectItem, val]
            copiedItemsClone.append(y)
            
        return copiedItemsClone        

    def unSelect(self):
        # set numbers to normal
        for i in range(0, len(self.shadedItems)):
            self.shadedItems[i][2].setBrush(QtCore.Qt.black)
            self.shadedItems[i][3].setBrush(QtCore.Qt.white)
                        
    def shadeAtIndex(self, iPos, jPos):
        items = [x for x in self.numberItems \
            if x[0] == iPos and x[1] == jPos]
        if len(items) == 1:
            items[0][2].setBrush(QtCore.Qt.white)
            items[0][3].setBrush(QtCore.Qt.black)
    
    def unShadeAtIndex(self, iPos, jPos):
        items = [x for x in self.numberItems \
            if x[0] == iPos and x[1] == jPos]
        if len(items) == 1:
            items[0][2].setBrush(QtCore.Qt.black)
            items[0][3].setBrush(QtCore.Qt.white)
            
    def setLyrics(self, text):
        self.lyricsItem = QtGui.QGraphicsTextItem(text)
        x = self.left() + self.lyricsItem.boundingRect().width() / 2
        y = self.lyricsBottom() + self.lyricsItem.boundingRect().height() / 2
        self.lyricsItem.setPos(x, y)
#        self.lyricsItem.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.lyricsItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.lyricsItem.setZValue(50)
        self.scene.addItem(self.lyricsItem)
        
    def toString(self):
        data = [[x[0],x[1],x[4]] for x in self.numberItems]
        return str(data)
        
    def loadFromString(self, st):
        data = ast.literal_eval(st)
        for i in range(0, len(data)):
            x = data[i]
            self.addToTab(x[0], x[1], x[2])        

        
        
        
        
