#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from cs_client import *
from PyQt4 import QtGui, QtCore
from time import ctime, time
from cont_chat import Chat_Server, Chat_Client
import threading
import thread
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class gridLayoutWindow(QtGui.QWidget, QtCore.QObject):
    newMsgSignal = QtCore.pyqtSignal(str)
    newPrvMsgSignal = QtCore.pyqtSignal(str)
    chatSwitch = QtCore.pyqtSignal()

    def __init__(self, client, parent):
        
        super(gridLayoutWindow, self).__init__()
        self.client = client
        self.client.userEnterTalkingRoom()
        self.peers = {}
        self.chatHistory = {"Group Chat":[]}
        self.currentChat = "Group Chat"
        self.parent = parent
        self.chatServer = Chat_Server(client.port, \
            self.newPrvMsgSignal)
        print "client.port", client.port
        self.chatClient = Chat_Client(client.username)
        self.chatServer.start()
        self.chatClient.start()
        self.getUi()
        
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
        
        self.sendBtn.clicked.connect(self.send_msg)
        
        self.users = QtGui.QListWidget(self)
        self.users.itemSelectionChanged.connect(self.chat_switch)
        self.onlineUserListControl()
        self.users.setMaximumWidth(100)
        self.add_group_chat_item()
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
        self.newMsgSignal.connect(self.show_msg)
        self.newPrvMsgSignal.connect(self.show_prv_msg)
        self.chatSwitch.connect(self.chat_switch)
        self.update.start()
        #self.show() 

    def add_group_chat_item(self):
        item = QtGui.QListWidgetItem()
        item.setText("Group Chat")
        self.users.addItem(item)

    def get_peers(self):
        namePacks = self.client.getOnlineUsers()
        for pck in namePacks:
            name, host, port = pck.split(' ')
            self.peers[name] = (host, int(port))
    
    def refresh_user_list(self):
        namesToAdd = self.peers.keys()
        itemRange = range(self.users.count())
        itemRange.reverse()
        for i in itemRange:
            name = str(self.users.item(i).text())
            if name == "Group Chat": continue
            if name not in namesToAdd:
                self.users.takeItem(i)
            else:
                namesToAdd.remove(name)

        for name in namesToAdd:
            item = QtGui.QListWidgetItem()
            item.setText(name)
            self.users.addItem(item)
            
        #self.users.addStretch(1)

    def chat_switch(self):
        if self.users.currentItem() != None:
            self.currentChat = str(self.users.currentItem().text())
        user = self.currentChat
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []

        self.dialog.clear()
        chatCache = self.chatHistory[user][-5:]
        for info in chatCache:
            self.insert_single_chat(info)
    
    def onlineUserListControl(self):
        self.get_peers()
        self.refresh_user_list()
    
    def updateDialogs(self):
        while self.client.protocol.connected:
            s = self.client.getMessage()
            if s == "talk":
                content = self.client.getRecentDialog()
                self.newMsgSignal.emit(content)
            else:
                self.onlineUserListControl()
    
    def center(self):   
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def extract_user_from_info(self, info):
        info = str(info)
        user = info.split("\n")[0].split(" ")[-1]
        return user
    
    def generate_icon(self, info):
        pixmap = QtGui.QPixmap(20, 20)
        user = self.extract_user_from_info(info)
        color = QtGui.QColor(hash(user)%255,
            (hash(user)/2)%255,
            (hash(user)/3)%255,
            255)
        pixmap.fill(color)
        icon = QtGui.QIcon(pixmap)
        return icon

    def insert_single_chat(self, info):
        item = QtGui.QListWidgetItem()
        item.setText(info)
        item.setIcon(self.generate_icon(info))
        self.dialog.addItem(item)

    def show_msg(self, info):
        user = self.currentChat
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []

        self.chatHistory[user].append(info)
        if self.currentChat == user:
            self.insert_single_chat(info)
        else:
            self.chat_switch()

    def show_prv_msg(self, info):
        user = self.extract_user_from_info(info)
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []

        print "history:"
        print self.chatHistory

        self.chatHistory[user].append(info)
        if self.currentChat == user:
            self.insert_single_chat(info)
        else:
            self.chat_switch()
    
    def send_msg(self):
        msg = str(self.user_talk.toPlainText())

        name = self.currentChat
        if name == "Group Chat":
            self.client.send_to_all(msg)
        else:
            host, port = self.peers[name]
            self.chatClient.send(msg, name, host, int(port))
            info = ctime()+" "+self.client.username+"\n"+msg
            self.newMsgSignal.emit(info)
        self.user_talk.clear()
    
    def closeEvent(self, event):
        self.client.leaveApplication()
        print 'Already Leave'
        event.accept()
        # self.exit()
        print self.parent

# def main():
  
#   app = QtGui.QApplication(sys.argv)
#   w = gridLayoutWindow()
#   sys.exit(app.exec_())
  
# if __name__ == '__main__':
#   main()
