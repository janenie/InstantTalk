#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from tsTclnt import *
from PyQt4 import QtGui, QtCore

class DialogWindow(QtGui.QWidget):
  
  def __init__(self):
    super(DialogWindow, self).__init__()
    
    self.initUI()
  
  def initUI(self):
    
    hbox = QtGui.QHBoxLayout(self)
    vbox = QtGui.QVBoxLayout(self)
    self.topLeft = QtGui.QListWidget(self)
    self.topLeft.setSortingEnabled(1)
    self.topLeft.resize(480, 270)
    self.topLeft.move(10, 10)
    #self.topLeft.append('LLLLLLL')
    
    #l = QtGui.QLabel('LLLLLLL', self)
    
    self.topRight = QtGui.QFrame(self)
    self.topRight.setStyleSheet("QWidget {background-color: red}")
    self.topRight.resize(200, 500)
    self.topRight.move(505, 0)
    #topRight.setFrameShape(QtGui.QFrame.StyledPanel)
    #topRight.setBackground(QtGui.QColor('red'))
    #topRight.resize(180, 480)
    
    
    
    self.content = QtGui.QTextEdit(self)
    self.content.resize(480, 160)
    self.content.move(10, 285)
    
    self.btn = QtGui.QPushButton('Send', self)
    self.btn.resize(50, 30)
    self.btn.move(440, 455)
    
    #vbox.addWidget(topLeft)
    #vbox.addWidget(content)
    #vbox.addWidget(btn, 1)
    #vbox.setSpacing(4)
    #vbox.resize(500, 480)
    
    #hbox.addWidget(topRight)
    #hbox.addLayout(vbox)
    #hbox.setSpacing(5)
    
    #self.setLayout(hbox)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    
    self.resize(700, 500)
    self.center()
    self.setWindowTitle('Common talking room')
    p = self.palette()
    p.setColor(self.backgroundRole(), QtGui.QColor('white'))
    #QtGui.QApplication.setBackground(QtGui.QColor('#F8F8FF'))
    #self.setWindowIcon(QtGui.QIcon('icon.gif'))
    
    self.show()
  
  def center(self):   
    qr = self.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())
    

def main():
  
  app = QtGui.QApplication(sys.argv)
  w = DialogWindow()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()