#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from cs_client import *
from PyQt4 import QtGui, QtCore
from time import ctime, time
import threading
import thread

class gridLayoutWindow(QtGui.QWidget, QtCore.QObject):
    newMsgSignal = QtCore.pyqtSignal(str)

    def __init__(self, client, parent):
        super(gridLayoutWindow, self).__init__()
        self.client = client
        self.client.userEnterTalkingRoom()
        self.otherusers = {}
        self.getUi()
        self.parent = parent
        
    def getUi(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.dialog = QtGui.QListWidget(self)
        self.user_talk = QtGui.QTextEdit(self)
        
        self.sendBtn = QtGui.QPushButton('send', self)
        self.sendBtn.resize(50, 30)
        btnGrid = QtGui.QGridLayout()
        spaceGrid = QtGui.QHBoxLayout()
        btnGrid.addLayout(spaceGrid, 0, 1, 1, 3)
        btnGrid.addWidget(self.sendBtn, 0, 4)
        
        self.sendBtn.clicked.connect(self.talkAndSend)
        
        self.users = QtGui.QListWidget(self)
        self.onlineUserListControl()
        # usr1 = QtGui.QPushButton('jane', self)
        # usr2 = QtGui.QPushButton('jack', self)
        # self.users.addWidget(usr1)
        # self.users.addWidget(usr2)
        # self.users.addStretch(1)
            
        # grid.addWidget(self.dialog, 0, 0, 6, 1)
        # grid.addWidget(self.user_talk, 6, 0, 2, 1)
        # grid.addWidget(btnGrid, 9, 0, 1, 3)
        # grid.addLayout(self.users, 0, 4, 8, 1)
        self.users.setMaximumWidth(100)
        grid.addWidget(self.users, 0, 1, 8, 1)
        grid.addWidget(self.dialog, 0, 0, 6, 1)
        grid.addWidget(self.user_talk, 6, 0, 2, 1)
        grid.addLayout(btnGrid, 9, 0, 1, 1)
        
        self.setLayout(grid)
        self.resize(700, 500)
        self.center()
        
        self.setWindowTitle('Common talking room')
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor('white'))
        
        self.update = threading.Thread(target=self.updateDialogs)
        self.newMsgSignal.connect(self.showDialogContent)
        self.update.start()
        #self.show() 

    def getUsernames(self):
        names = self.client.getOnlineUsers()
        print 'getUsernames: {}'.format(names)
        for msg in names:
            info = msg.split(' ')
            self.otherusers[info[0]] = (info[1], info[2])
    
    def refreshUserList(self):
        #self.users.clear()
        self.users.clear()
        for name in self.otherusers.keys():
            print 'refreshUserList: {}'.format(name)
            item = QtGui.QListWidgetItem(name)
            self.users.addItem(item)
        
        #self.users.addStretch(1)
    
    def onlineUserListControl(self):
        self.getUsernames()
        self.refreshUserList()
    
    def updateDialogs(self):
        while self.client.protocol.connected:
            s = self.client.getMessage()
            if s == "talk":
                content = self.client.getRecentDialog()
                # self.showDialogContent(content)
                self.newMsgSignal.emit(content)
            else:
                self.onlineUserListControl()
    
    def center(self):   
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def generateIcon(self, info):
        pixmap = QtGui.QPixmap(20, 20)
        user = info.split("\n")[0].split(" ")[-1]
        print "user:", user
        color = QtGui.QColor(hash(user)%255,
            (hash(user)/2)%255,
            (hash(user)/3)%255,
            255)
        pixmap.fill(color)
        icon = QtGui.QIcon(pixmap)
        return icon

    def showDialogContent(self, info):
        item = QtGui.QListWidgetItem()
        item.setText(info)
        item.setIcon(self.generateIcon(info))
        self.dialog.addItem(item)
    
    def talkAndSend(self):
        s = self.user_talk.toPlainText()
        #Add sending info to server
        info = str(s)
        self.client.sendTalkMsg(info)
        self.user_talk.clear()
    
    def closeEvent(self, event):
        self.client.leaveApplication()
        print 'Already Leave'
        event.accept()
        #self.exit()
        print self.parent
        self.parent.close()

# def main():
  
#   app = QtGui.QApplication(sys.argv)
#   w = gridLayoutWindow()
#   sys.exit(app.exec_())
  
# if __name__ == '__main__':
#   main()
