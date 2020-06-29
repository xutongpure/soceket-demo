import socket
import sys
import json
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import QThread, Signal, QProcessEnvironment, Qt
from PySide2.QtWidgets import QWidget, QListWidget, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, \
    QApplication, QDialog

flag = True



class ClientWindow(QDialog):

    def __init__(self):
        super(ClientWindow, self).__init__()
        self.setWindowModality(Qt.NonModal)
        self.resize(450,300)
        self.friendList = QListWidget()
        self.portLine = QLineEdit()
        self.portLine.setText('12345')
        self.connectBtn = QPushButton('连接')
        self.connectBtn.clicked.connect(self.connectFun)
        self.messageText = QTextEdit()
        self.messageLine = QLineEdit()
        self.sendBtn = QPushButton('发送')
        self.sendBtn.clicked.connect(self.sendFun)
        self.text = ''
        self.initUI()
        self.client = Client()
        self.client.trigger.connect(self.updateTextFun)


    def initUI(self):
        mainLayout = QVBoxLayout()
        mainWidget = QWidget()
        widget1 = QWidget()
        layout1 = QHBoxLayout()
        layout1.addWidget(self.portLine)
        layout1.addWidget(self.connectBtn)
        widget1.setLayout(layout1)
        mainLayout.addWidget(widget1)
        widget2 = QWidget()
        layout2 = QHBoxLayout()
        layout2.addWidget(self.messageText)
        layout2.addWidget(self.friendList)
        layout2.setStretch(0,2)
        layout2.setStretch(0,1)
        widget2.setLayout(layout2)
        mainLayout.addWidget(widget2)

        # mainLayout.addStretch(1)
        widget3 = QWidget()
        layout3 = QHBoxLayout()
        layout3.addWidget(self.messageLine)
        layout3.addWidget(self.sendBtn)
        widget3.setLayout(layout3)
        mainLayout.addWidget(widget3)

        self.setLayout(mainLayout)

    def connectFun(self):
        port = int(self.portLine.text())
        self.client.connectFun(port)
        self.client.start()

    def sendFun(self):

        message = self.messageLine.text()
        self.client.sendMessage(message)
        # self.text = self.text + message

    def updateTextFun(self,message):

        self.text += message + '\n'
        self.messageText.setText(self.text)

    def closeEvent(self, event:PySide2.QtGui.QCloseEvent):
        self.client.closeFun()

class Client(QThread):
    trigger = Signal(str)

    def __init__(self):
        super(Client, self).__init__()
        self.client = socket.socket()


    def run(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if data:
                    self.trigger.emit(data)
            except Exception as e:
                print(e)
                break

    def connectFun(self,port):
        self.client.bind(('127.0.0.1',port))
        self.client.connect(('127.0.0.1', 8888))
        self.trigger.emit('connected to server')

    def sendMessage(self,message):
        self.client.sendall(message.encode())

        # self.client.sendto(message.encode(),('<broadcast>', 8888))
        self.trigger.emit(message)

    def closeFun(self):
        self.trigger.emit('断开连接')
        self.client.close()


if __name__ == '__main__':

    QProcessEnvironment.systemEnvironment().insert("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = ClientWindow()
    w.show()
    sys.exit(app.exec_())