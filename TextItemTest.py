
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this is practice for dealing with lyrics lines

import sys
from PyQt5 import QtGui, QtCore


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):    
        QtGui.QMainWindow.__init__(self, parent)
                
        # add TablatureWindow
        self.tabWidget = QtGui.QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle('FAIT Tablature Editor')    

        self.startNewTablature()
        self.tabWidget.addTab(self.tablatureWindow, 'Untitled')
        self.tablatureWindow.setFocus()
        
        self.positionWindow()       # center and almost maximize window
        
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
        
    def startNewTablature(*args, **kwargs):
        self = args[0]
        self.tablatureWindow = TablatureWindow(self)
        self.tabWidget.removeTab(0)
        self.tabWidget.addTab(self.tablatureWindow, 'Untitled')
        self.tablatureWindow.setFocus()
        

class TablatureWindow(QtGui.QGraphicsView):    
    def __init__(*args, **kwargs):
        self = args[0] 
        self._parent = args[1]
                       
        QtGui.QGraphicsView.__init__(self)    
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)

        self.scene.setSceneRect(QtCore.QRectF(0, 0, 2000, 10000))

        self.centerOn(0,0)
        
        # draw something in the window
        self.rectItem = QtGui.QGraphicsRectItem(10, 100, 1000, 20)
        self.rectItem.setZValue(-10)
        self.scene.addItem(self.rectItem)
        
        self.lyricsItems = []
        self.lyricsItemInFocus = None
        
    def keyPressEvent(self, e):
        QtGui.QGraphicsView.keyPressEvent(self, e)

        # with each keystroke, return size of item in focus
        if self.lyricsItemInFocus != None:
            w = self.lyricsItemInFocus.boundingRect().width()
            h = self.lyricsItemInFocus.boundingRect().height()
            print('w = ' + str(w) + ', h = ' + str(h))

            # print warning if boundingRect gets wide enough to overlap with over items
            # TODO

            # when enter is pressed, enlargen rectangle
            if e.key() == QtCore.Qt.Key_Return:
                rect1 = self.rectItem.rect()
                h2 = rect1.height()
                if h > h2:
                    rect1.setHeight(h)
                    self.rectItem.setRect(rect1)            
        
    def mousePressEvent(self, e):
        scenePoint = self.mapToScene(e.x(), e.y())
        xPos, yPos = scenePoint.x(), scenePoint.y()

        # if mouse clicked on rectItem, create textItem there if it isn't there already
#        if self.rectItem.contains(QtCore.QPointF(e.x(), e.y())):
        if self.rectItem.contains(QtCore.QPointF(xPos, yPos)):
            print('contains')
#            item = self.itemAt(xPos, yPos)
            item = self.itemAt(e.x(), e.y())
            if item == None:
                print('Warning: None found')
                self.lyricsItemInFocus = None
            elif item is self.rectItem:
                print('item was self.rectItem; len(self.lyricsItems) = ' + str(len(self.lyricsItems)))
                # first check previous item to see if it's empty
                if len(self.lyricsItems) > 0:
                    if self.lyricsItems[-1].toPlainText() == '':
                        print('empty')
                        # delete this item
                        self.scene.removeItem(self.lyricsItems[-1])
                        self.lyricsItems.pop()  #remove most recent item
                
                # make new textItem
                textItem = QtGui.QGraphicsTextItem()
                textItem.setPos(xPos, self.rectItem.rect().y())
                textItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
                self.scene.addItem(textItem)
                self.lyricsItems.append(textItem)
                self.lyricsItemInFocus = textItem
                textItem.setFocus()
#                QtGui.QGraphicsView.mousePressEvent(self, e)

            # if there's an item and it isn't our rectItem, we assume it must be a textItem
            else:                
                self.lyricsItemInFocus = item
                QtGui.QGraphicsView.mousePressEvent(self, e)
            
            
            

if __name__ == "__main__":
 
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
