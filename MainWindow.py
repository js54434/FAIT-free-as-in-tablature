# the main window that contains the tablature window, menus, etc.
# and coordinates dialog messages and keyboard shortcuts
#
# It also contains the midiPlayer object. 

from PyQt4 import QtGui, QtCore

import MidiPlayer
#import AudioPlayer
import TablatureWindow


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        self.prev_saveFilename = ''
    
        super(MainWindow, self).__init__()
        
        self.midiPlayer = MidiPlayer.MidiPlayer()  
#        self.audioPlayer = AudioPlayer.AudioPlayer()      
                
        self.initUI()
        
    def initUI(self):
        # menus and statusbar
        self.statusBar()
        
        # add TablatureWindow
        self.stackedWidget = QtGui.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.setWindowTitle('FAIT Tablature Editor')    

        self.tablatureWindow = TablatureWindow.TablatureWindow(self)
        self.setWindowTitle('Untitled')
        self.stackedWidget.addWidget(self.tablatureWindow)
        self.stackedWidget.setCurrentWidget(self.tablatureWindow)
        self.tablatureWindow.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.tablatureWindow.setFocus()
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        editMenu = menubar.addMenu('&Edit')
        trackMenu = menubar.addMenu('&Track')
        
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
        
        runScript = QtGui.QAction('Run Script...', self)
        runScript.setStatusTip('Run script')
        runScript.triggered.connect(self.runScript)
        
        quitApp = QtGui.QAction('Quit', self)
        quitApp.setShortcut(QtGui.QKeySequence.Quit)
        quitApp.setStatusTip('Quit')
        quitApp.triggered.connect(self.quitApp)
        
        fileMenu.addAction(newFile)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)
        fileMenu.addAction(runScript)
        fileMenu.addAction(quitApp)

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
        
        changeInstrument = QtGui.QAction('change instrument', self)
        changeInstrument.setShortcut('Ctrl+I')
        changeInstrument.setStatusTip('change instrument')
        changeInstrument.triggered.connect(self.changeInstrument)
        
        changeTempo = QtGui.QAction('change tempo', self)
        changeTempo.setShortcut('Ctrl+T')
        changeTempo.setStatusTip('change tempo')
        changeTempo.triggered.connect(self.changeTempo)
        
        trackMenu.addAction(changeInstrument)
        trackMenu.addAction(changeTempo)
        
#        icon = QtGui.QIcon("drawnStartButton.png")
#        icon = QtGui.QIcon("startButton-AsIs.png")
#        icon = QtGui.QIcon("startButton-grainy.png")
        icon = QtGui.QIcon("startButton-sharp.png")
#        icon = QtGui.QIcon("pauseButton.png")

        self.playButton = QtGui.QPushButton(icon, "")
        self.playButton.setIconSize(QtCore.QSize(110, 110))
        self.playButton.setParent(self)
        self.playButton.setGeometry(0, 0, 100, 100)

        self.connectWidgets()

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
                self.setWindowTitle(fname)
                
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
                self.tablatureWindow.close()
                self.disconnectWidgets()
                
                self.tablatureWindow = TablatureWindow.TablatureWindow(self, loadFile=f)
                self.stackedWidget.addWidget(self.tablatureWindow)
                self.stackedWidget.setCurrentWidget(self.tablatureWindow)
                self.setWindowTitle(fname)
                self.connectWidgets()                
                self.tablatureWindow.setFocus()

    # play with ctrl-N
    def startNewTablature(*args, **kwargs):
        self = args[0]
        self.tablatureWindow.close()
        self.disconnectWidgets()        

        self.tablatureWindow = TablatureWindow.TablatureWindow(self)
        self.stackedWidget.addWidget(self.tablatureWindow)
        self.stackedWidget.setCurrentWidget(self.tablatureWindow)
        self.setWindowTitle('Untitled')
        self.connectWidgets()        
        self.tablatureWindow.setFocus()
        
    def runScript(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                '~/Documents/coding/Tab Program/')
        if fname != '':
            f = open(fname, 'r')
            
            with f:
                self.tablatureWindow.runScript(f)
                
    def quitApp(self):
        # stop playback before quitting so stuff doesn't hang
        self.tablatureWindow.stopPlayback()
        time.sleep(0.1)
        
        self.close()
            
    def disconnectWidgets(self):
        QtCore.QObject.disconnect(self.playButton, QtCore.SIGNAL("released()"), 
            self.tablatureWindow.togglePlayback)
            
    def connectWidgets(self):
        QtCore.QObject.connect(self.playButton, QtCore.SIGNAL("released()"), 
            self.tablatureWindow.togglePlayback)

    def resizeWidgets(self):
        print('resizeWidgets()')
        self.leftBar.setGeometry(0, 0, 100, self.tablatureWindow.viewport().height())
        self.topBar.setGeometry(0, 0, self.tablatureWindow.viewport().width(), 100)
                
    def cutSelection(self):
        self.tablatureWindow.cutSelection()

    def copySelection(self):
        self.tablatureWindow.copySelection()
        
    def pasteSelection(self):
        self.tablatureWindow.pasteSelection()
        
    def changeInstrument(self):
        numStr, ok = QtGui.QInputDialog.getText(self, '', 'Type instrument number (1-128):')

        if ok:
            if self.is_number(numStr):
                if int(numStr) >= 1:
                    if int(numStr) <= 128:
                        self.tablatureWindow.changeInstrument(int(numStr))
                    else:
                        self.showError('number too large')
                else:
                    self.showError('number must be 1 or greater')
            else:
                self.showError('instrument number must be an integer 0 or greater')
                
    def changeTempo(self):
        numStr, ok = QtGui.QInputDialog.getText(self, '', 'Type tempo in bpm (30-500)')
        
        if ok:
            if self.is_number(numStr):
                if int(numStr) >= 30 and int(numStr) <= 500:
                    self.tablatureWindow.setTempo(int(numStr))
                else:
                    self.showError('Tempo must be between 30 and 500 bpm.')
            else:
                self.showError('Tempo must be a number.')

    def showError(self, errorStr):
        QtGui.QMessageBox.warning(self, "Error:", errorStr)


    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False
