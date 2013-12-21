#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from tsTclnt import *
from PyQt4 import QtGui, QtCore

CODEC = 'utf-8'

class LoginWindow(QtGui.QWidget):
  
  def __init__ (self):
    super(LoginWindow, self).__init__()
    
    self.initUI()
  
  def initUI(self):
    
    
    name = QtCore.QString(u"用户名:")
    username = QtGui.QLabel(name)
    self.userEdit = QtGui.QLineEdit()
    #userEdit.setFixedSize(130, 30)
    
    grid = QtGui.QGridLayout()
    grid.setSpacing(10)
    
    grid.addWidget(username, 1, 0)
    grid.addWidget(self.userEdit, 1, 1)
    
    title = QtGui.QLabel('MINET', self)
    title.setFont(QtGui.QFont('SansSerif', 20))
    title.resize(80, 40)
    title.move(115, 20)
    
    btn = QtGui.QPushButton('Enter', self)
    btn.setToolTip('enter the app')
    btn.resize(btn.sizeHint())
    btn.move(115, 150)
    btn.clicked.connect(self.sendData)
    
    self.setLayout(grid)
    
    self.resize(300, 200)
    self.center()
    self.setWindowTitle('login')
    self.setWindowIcon(QtGui.QIcon('icon.gif'))
    
    self.show()
  
  def center(self):   
    qr = self.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())
    
  def sendData(self):
    s = self.userEdit.text()
    self.tcp = ClientProtocol()
    self.tcp.makeConnection()
    print 'connected'
    self.connect = self.tcp.testConnected()
    print self.connect
    if s:
      self.tcp.sendUserInfo(s)
      self.tcp.dataRecived()
      self.login = self.tcp.getLogin()
      if self.login:
        #self.hide()
        pass
      else:
        reply2 = QtGui.QMessageBox.question(self, 'Message',
        'Repetition, please change a name', QtGui.QMessageBox.Yes |
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
    else:
      reply3 = QtGui.QMessageBox.question(self, 'Message',
        'Can not be empty name', QtGui.QMessageBox.Yes |
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
    
    

def main():
  
  app = QtGui.QApplication(sys.argv)
  w = LoginWindow()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()

    
