import sys
from PyQt4 import QtGui

class IconWindow(QtGui.QWidget):
  
  def __init__(self):
    super(IconWindow, self).__init__()
    
    self.initUI()
  
  def initUI(self):
    
    QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
    
    self.setToolTip('add this to <b>LOGIN</b>')
    
    btn = QtGui.QPushButton('Enter', self)
    btn.setToolTip('enter the app')
    btn.resize(btn.sizeHint())
    btn.move(115, 150)
    
    self.resize(300, 200)
    self.center()
    self.setWindowTitle('login')
    self.setWindowIcon(QtGui.QIcon('icon.gif'))
    
    self.show()
  
  def closeEvent(self, event):
    
    reply = QtGui.QMessageBox.question(self, 'Message',
      'Are you sure to quit?', QtGui.QMessageBox.Yes |
      QtGui.QMessageBox.No, QtGui.QMessageBox.No)
    
    if reply == QtGui.QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()
      
  def center(self):
    
    qr = self.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

def main():
  
  app = QtGui.QApplication(sys.argv)
  w = IconWindow()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()

