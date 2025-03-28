#!/usr/bin/env python
# -*- coding: utf-8 -*-

# everything starts here.

import sys
from PyQt5 import QtGui, QtCore, QtWidgets

import MainWindow

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow.MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 
