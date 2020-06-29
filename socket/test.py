import socket
import sys
import json
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Signal, QThread, Qt, QProcessEnvironment
from PySide2.QtWidgets import QDialog, QListWidget, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QWidget, \
    QHBoxLayout, QApplication, QListWidgetItem
from PySide2.QtGui import QIcon, QPixmap, QPalette, QBrush


class Client(QThread):
    trigger = Signal(str)

    def __init__(self):
        super(Client, self).__init__()
        self.client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def setupFun(self,port):

        self.PORT = port
        self.client.bind(('localhost',port))
        self.connectFun()

    def connectFun(self):

        data = {
            'message': 'connect',
            'to' : 'broadcast'
        }
        data = json.dumps(data)
        self.client.sendto(data.encode(),('localhost', 8888))
        # self.trigger.emit('connected to server')
        print('connected to server')

    def run(self):
        while True:
            data, addr = self.client.recvfrom(1024)
            self.trigger.emit(data.decode())

    def sendFun(self, message, addr):
        data = {
            'message': message,
            'to': addr
        }
        data = json.dumps(data)
        self.client.sendto(data.encode(),('localhost', 8888))

    def closeFun(self):
        data = {}
        data['message'] = 'close'
        data['to'] = 'broadcast'
        data = json.dumps(data)
        self.client.sendto(data.encode(),('localhost', 8888))


class ClientWindow(QDialog):

    def __init__(self):
        super(ClientWindow, self).__init__()

        self.resize(823,511)
        self.setWindowTitle('用户客户端')
        self.friendList = QListWidget()
        self.friendList.doubleClicked.connect(self.changeFriendText)
        self.friendList.clicked.connect(self.changeFriendText)
        self.portLine = QLineEdit()
        self.portLine.setText('12345')
        self.connectBtn = QPushButton('连接')
        self.connectBtn.clicked.connect(self.setupFun)
        self.messageText = QTextEdit()
        self.messageLine = QLineEdit()
        self.sendBtn = QPushButton('发送')
        self.sendBtn.clicked.connect(self.sendFun)

        self.text = ''
        self.userText = {}

        self.initUI()
        self.palette = QPalette()
        self.palette.setBrush(QPalette.Background, QBrush(QPixmap('./image/background.jpg')))
        self.setPalette(self.palette)
        self.client = Client()
        self.client.trigger.connect(self.updateTextFun)
        self.ininData()

    def changeFriendText(self):
        currentItem = self.friendList.currentItem().text()
        self.text = self.userText[currentItem]
        self.messageText.setText(self.text)

    def ininData(self):
        self.friendList.addItem('broadcast')
        self.userText['broadcast'] = ''
        self.friendList.setCurrentItem(self.friendList.item(0))

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

    def setupFun(self):
        port = int(self.portLine.text())
        self.client.setupFun(port)
        self.client.start()

    def sendFun(self):
        addr = self.friendList.currentItem().text()
        message = self.messageLine.text()
        if message != 'add' and message != 'del':
            self.userText[addr] += '我:' + message + '\n'
        self.changeFriendText()
        if addr != 'broadcast':
            addr = ('localhost',int(addr))
        self.client.sendFun(message,addr)
        self.messageLine.setText('')


    def updateTextFun(self,data):

        currentItem = self.friendList.currentItem().text()
        data = json.loads(data)
        if 'cmd' in data.keys():
            if data['cmd'] == 'add':
                fromUser = str(data['from'])
                addr = ('127.0.0.1',int(fromUser))
                item = self.friendList.findItems(fromUser,Qt.MatchExactly)
                if fromUser not in self.userText.keys():
                    self.userText[fromUser] = ''
                if len(item) == 0:
                    self.friendList.addItem(fromUser)
                    self.client.sendFun('add',addr)  # 已添加
            elif data['cmd'] == 'del':
                fromUser = str(data['from'])
                rows = self.friendList.count()
                for row in range(rows):
                    if fromUser == self.friendList.item(row).text():
                        self.friendList.takeItem(row)
        else:
            message = data['message']
            fromUser = str(data['from'])
            if fromUser != 'broadcast':
                addr = ('127.0.0.1', int(fromUser))
                item = self.friendList.findItems(fromUser, Qt.MatchExactly)
                if fromUser not in self.userText.keys():
                    self.userText[fromUser] = ''
                if len(item) == 0:
                    self.friendList.addItem(fromUser)
                    self.client.sendFun('add', addr)  # 已添加
            if message != 'add' and message != 'del':
                self.userText[fromUser] += fromUser + ':' + message + '\n'
                if fromUser == currentItem:
                    self.text = self.userText[fromUser]
                    self.messageText.setText(self.text)


    def closeEvent(self, event:PySide2.QtGui.QCloseEvent):
        self.client.closeFun()

if __name__ == '__main__':
    QProcessEnvironment.systemEnvironment().insert("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = ClientWindow()
    w.show()
    sys.exit(app.exec_())