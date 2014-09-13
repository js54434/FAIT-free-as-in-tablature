#!/usr/bin/env python
# -*- coding: utf-8 -*-

# everything starts here.

import sys
from PyQt4 import QtGui, QtCore

import MainWindow

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow.MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 
