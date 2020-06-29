import socket
import json
import sys
import logging
from PySide2.QtGui import QIcon, QFont, QPixmap, QImage, QPalette, QBrush
from PySide2 import QtCore
from PySide2.QtCore import QProcessEnvironment, Signal, QThread
from PySide2.QtWidgets import QMainWindow, QPushButton, QLabel, QTextEdit, QLineEdit, QWidget, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QApplication
from test import ClientWindow


class SocketServer(QThread):
    trigger = Signal(str)

    def __init__(self):
        super(SocketServer, self).__init__()
        self.server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.activeClient = []  # 端口 和 用户名

        self.PORT = 8888
        self.IP = '127.0.0.1'

    def setupFun(self,port):

        self.PORT = port
        self.server.bind(('localhost',port))
        # self.activeClient[('127.0.0.1', port)] = 'broadcast'
        self.activeClient.append('broadcast')
        self.trigger.emit('服务器启动于端口 {}'.format(self.PORT))

    def run(self):
        while True:
            try:
                data, addr = self.server.recvfrom(1024)  # 如果没有收到发往这个绑定端口的消息，会一直阻塞在这里
                data = json.loads(data.decode())
                print(data)
                message = data['message']
                to = data['to']
                if message == 'connect':
                    # self.activeClient[addr] = str(addr[1])
                    self.activeClient.append(str(addr[1]))
                    self.trigger.emit('{} 已连接'.format(addr[1]))
                    for to in self.activeClient:   # 广播连接
                        if to==str(self.PORT) or to=='broadcast':
                            continue
                        data = {
                            'from': addr[1],
                            'cmd': 'add',    # 命令
                        }
                        data = json.dumps(data)
                        self.server.sendto(data.encode(), ('127.0.0.1',int(to)))
                elif message == 'close':
                    self.activeClient.remove(str(addr[1]))
                    self.trigger.emit('{} 已断开连接'.format(addr[1]))
                    for to in self.activeClient:   # 广播连接
                        if to == 'broadcast' or to==str(self.PORT):
                            continue
                        data = {
                            'from': addr[1],
                            'cmd': 'del',    # 命令
                        }
                        data = json.dumps(data)
                        self.server.sendto(data.encode(), ('127.0.0.1',int(to)))
                else:
                    if to == 'broadcast':
                        for to in self.activeClient:
                            if to == str(self.PORT) or to == 'broadcast':
                                continue
                            data = {
                                'message': message,
                                'from': 'broadcast'
                            }
                            data = json.dumps(data)
                            self.server.sendto(data.encode(), ('127.0.0.1', int(to)))
                    else:
                        data = {
                            'message': message,
                            'from': str(addr[1]),
                        }
                        data = json.dumps(data)
                        self.server.sendto(data.encode(),('127.0.0.1',int(to[1])))
                        # self.server.sendto(data.encode(),('127.0.0.1',addr[1]))
                    self.trigger.emit(str(to[1]) + ':' + str(message))

            except Exception as e:
                logging.log(e)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(562,381)
        self.setWindowTitle('服务器')
        self.addClientBtn = QPushButton('添加客户端')
        self.addClientBtn.clicked.connect(self.addClientFunc)
        self.clearTextBtn = QPushButton('清除文本')
        self.setupBtn = QPushButton('启动服务器')
        self.setupBtn.clicked.connect(self.setupFunc)
        self.portLabel = QLabel('端口:')
        self.chatText = QTextEdit()
        self.portLine = QLineEdit()
        self.portLine.setText('8888')
        self.setupBtn1 = QPushButton('关闭服务器')
        self.setupBtn1.clicked.connect(lambda: self.updateText('服务器已关闭'))
        self.server = SocketServer()
        self.server.trigger.connect(self.updateText)
        self.palette = QPalette()
        self.palette.setBrush(QPalette.Background, QBrush(QPixmap('./image/background.jpg')))
        self.setPalette(self.palette)
        self.text = ''
        self.windowList = []

        self.ipLine = QLineEdit('127.0.0.1')
        self.ipLabel = QLabel('IP:')

        self.initUI()
        self.initData()

    def initData(self):
        hostname = socket.gethostname()
        # 获取本机ip
        ip = socket.gethostbyname(hostname)
        self.ipLine.setText(str(ip))

    def initUI(self):

        mainWidget = QWidget()
        mainLayout = QHBoxLayout()

        rightWidget = self.creatRightWidget()
        mainLayout.addWidget(rightWidget)

        mainLayout.addWidget(self.chatText)
        mainLayout.setStretch(0,1)
        mainLayout.setStretch(1,3)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def creatRightWidget(self):

        rightWidget = QGroupBox('操作')
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.ipLabel)
        rightLayout.addWidget(self.ipLine)
        rightLayout.addWidget(self.portLabel)
        rightLayout.addWidget(self.portLine)
        rightLayout.addWidget(self.setupBtn)
        rightLayout.addWidget(self.setupBtn1)
        rightLayout.addStretch(1)
        rightLayout.addWidget(self.addClientBtn)
        rightLayout.addWidget(self.clearTextBtn)
        rightWidget.setLayout(rightLayout)

        return rightWidget

    def setupFunc(self):

        port = int(self.portLine.text())
        self.server.setupFun(port)
        self.server.start()


    def updateText(self,msg):
        if 'add' not in msg and 'del' not in msg:
            self.text += msg + '\n'
            self.chatText.setText(self.text)

    def addClientFunc(self):

        w = ClientWindow()
        w.show()
        self.windowList.append(w)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())