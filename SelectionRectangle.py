import time
import sys
import os
from PyQt4 import QtGui, QtCore

import Tracks


class SelectionRectangle(QtGui.QGraphicsRectItem):
    def __init__(self, tracks, x1, y1, x2, y2):
        QtGui.QGraphicsRectItem.__init__(self, x1, y1, x2, y2)
        self.tracks = tracks

    def updateSelectionRectangle(*args):
        self = args[0]
        if len(args) == 2:        
            x1, y1, x2, y2 = args[1]
        elif len(args) == 1:
            r = self.rect()
            x1 = r.left()
            y1 = r.top()
            x2 = r.right()
            y2 = r.bottom()
            
        x11 = min(x1, x2)
        y11 = min(y1, y2)
        x22 = max(x1, x2)
        y22 = max(y1, y2)

        # figure out which track points are in
        i1 = self.whichTrackHasPoint(x11, y11)
        i2 = self.whichTrackHasPoint(x22, y22)
        
        if i1 == i2:
            x1 = self.tracks[i1].returnAlignedCoordX(x11, 'left')
            y1 = self.tracks[i1].returnAlignedCoordY(y11, 'top')
            x2 = self.tracks[i2].returnAlignedCoordX(x22, 'right')
            x20 = self.tracks[i2].returnAlignedCoordX(x22, 'left')
            y2 = self.tracks[i2].returnAlignedCoordY(y22, 'bottom')
            y20 = self.tracks[i2].returnAlignedCoordY(y22, 'top')            
        else:
            x1 = self.tracks[i1].returnAlignedCoordX(x11, 'left')
            y1 = self.tracks[i1].returnAlignedCoordY(y11, 'topmost')
            x2 = self.tracks[i2].returnAlignedCoordX(x22, 'right')
            x20 = self.tracks[i2].returnAlignedCoordX(x22, 'left')
            y2 = self.tracks[i2].returnAlignedCoordY(y22, 'bottommost')            
            y20 = self.tracks[i2].returnAlignedCoordY(y22, 'nextbottommost')
        
        self.setRect(x1, y1, (x2-x1), (y2-y1))
        
        for i in range(0, len(self.tracks)):
#            self.tracks[i].shadeSelectedNumbers(x1, y1, x20, y20)
            self.tracks[i].shadeSelectedRegion(x1, y1, x20, y20)

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


    def expandUp(self):
        self.moveUpperBoundOneUnit('up')
        
    def contractDown(self):
        self.moveUpperBoundOneUnit('down')
        
    def expandDown(self):
        self.moveLowerBoundOneUnit('down')
        
    def contractUp(self):
        self.moveLowerBoundOneUnit('up')
        
    def expandLeft(self):
        self.moveLeftBoundOneUnit('left')

    def contractRight(self):
        self.moveLeftBoundOneUnit('right')        

    def expandRight(self):
        self.moveRightBoundOneUnit('right')

    def contractLeft(self):
        self.moveRightBoundOneUnit('left')
        
        
    def moveUpperBoundOneUnit(self, direction):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().top())
        
        jPos = self.tracks[i1].getCursorIndexY(self.rect().top())
        jPos2 = self.tracks[i1].getMovedIndexY(jPos, direction)
        y = self.tracks[i1].convertIndexToPositionY(jPos2)
        
        r1 = self.rect()
        x1 = r1.left()
        y1 = r1.top()
        h = r1.height()
        w = r1.width()
        self.setRect(x1, y, w, h + (y1-y))

    def moveLowerBoundOneUnit(self, direction):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().bottom())
        
        jPos = self.tracks[i1].getCursorIndexY(self.rect().bottom()) - 1
        jPos2 = self.tracks[i1].getMovedIndexY(jPos, direction)
        y = self.tracks[i1].convertIndexToPositionY(jPos2 + 1)
        
        r1 = self.rect()
        x1 = r1.left()
        y1 = r1.top()
        h = r1.height()
        w = r1.width()
        self.setRect(x1, y1, w, y - y1)
        
    def moveLeftBoundOneUnit(self, direction):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().top())
        
        iPos = self.tracks[i1].getCursorIndexX(self.rect().left())
        iPos2 = self.tracks[i1].getMovedIndexX(iPos, direction)
        x = self.tracks[i1].convertIndexToPositionX(iPos2)
        
        r1 = self.rect()
        x1 = r1.left()
        y1 = r1.top()
        h = r1.height()
        w = r1.width()
        self.setRect(x, y1, w + (x1-x), h)

    def moveRightBoundOneUnit(self, direction):
        i1 = self.whichTrackHasPoint(self.rect().right(), self.rect().top())
        
        iPos = self.tracks[i1].getCursorIndexX(self.rect().right()) - 1
        iPos2 = self.tracks[i1].getMovedIndexX(iPos, direction)
        x = self.tracks[i1].convertIndexToPositionX(iPos2 + 1)
        
        r1 = self.rect()
        x1 = r1.left()
        y1 = r1.top()
        h = r1.height()
        w = r1.width()
        self.setRect(x1, y1, x - x1, h)

    def getTopIndex(self):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().top())
        return self.tracks[i1].getCursorIndexY(self.rect().top())

    def getBottomIndex(self):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().bottom())
        return self.tracks[i1].getCursorIndexY(self.rect().bottom()) - 1
        
    def getLeftIndex(self):
        i1 = self.whichTrackHasPoint(self.rect().left(), self.rect().top())
        return self.tracks[i1].getCursorIndexY(self.rect().left())
        
    def getRightIndex(self):
        i1 = self.whichTrackHasPoint(self.rect().right(), self.rect().top())
        return self.tracks[i1].getCursorIndexY(self.rect().right()) - 1

