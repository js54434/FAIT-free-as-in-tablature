#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
import sys
import threading
from PyQt4 import QtGui, QtCore

import MainWindow

#import Tracks
#import AudioTracks
#import MidiPlayer
#import AudioPlayer
#import SelectionRectangle
#import Cursor
#import GenerateData

import fluidsynth

                

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow.MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 
