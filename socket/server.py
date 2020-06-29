import threading
import sys
import socket
from PySide2 import QtCore
from PySide2.QtCore import QThread, Signal, QProcessEnvironment
from PySide2.QtWidgets import QPushButton,QApplication,QMainWindow,QWidget,QTextEdit,QLineEdit,QVBoxLayout,QHBoxLayout,QLabel,QGroupBox
from client import ClientWindow
import json

class SocketServer(QThread):
    trigger = Signal(str)

    def __init__(self):
        super(SocketServer, self).__init__()
        self.server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.aliveClient = ()


    def setupFunc(self,port):
        self.server.bind(('127.0.0.1',port))
        # self.server.listen()
        self.trigger.emit('server start on 127.0.0.1:{}'.format(port))

    def run(self):
        while True:
            conn, addr = self.server.accept()
            t = threading.Thread(target=self.handle,args=(conn,addr))
            t.start()


    def handle(self,conn,addr):
        self.trigger.emit('connected by {}'.format(addr))
        self.aliveClient = (*self.aliveClient,addr)
        print(self.aliveClient)
        while True:
            try:
                data = conn.recv(1024).strip()
                if data:
                    self.trigger.emit(data.decode())
                    # conn.sendall(data)
                    conn.sendto(data, ('127.0.0.1',12346))
                    # conn.sendto(data,('localhost', 12346))
                    print(data,addr)
            except Exception as e:
                self.trigger.emit('{} disconnect'.format(addr))
                removeIndex = self.aliveClient.index(addr)
                del(self.aliveClient[removeIndex])
                print(e)
                break


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(800,680)
        self.setWindowTitle('Sock Server')

        self.addClientBtn = QPushButton('添加客户端')
        self.addClientBtn.clicked.connect(self.addClientFunc)
        self.clearTextBtn = QPushButton('清除文本')
        self.setupBtn = QPushButton('启动服务器')
        self.setupBtn.clicked.connect(self.setupFunc)
        self.portLabel = QLabel('端口:')
        self.chatText = QTextEdit()
        self.portLine = QLineEdit()
        self.portLine.setText('8888')

        self.server = SocketServer()
        self.server.trigger.connect(self.updateText)

        self.text = ''
        self.windowList = []

        self.initUI()

    def initUI(self):

        mainWidget = QWidget()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.chatText)
        rightWidget = self.creatRightWidget()
        mainLayout.addWidget(rightWidget)
        mainLayout.setStretch(0,2)
        mainLayout.setStretch(1,1)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def creatRightWidget(self):

        rightWidget = QGroupBox('操作')
        rightLayout = QVBoxLayout()

        rightLayout.addWidget(self.portLabel)
        rightLayout.addWidget(self.portLine)
        rightLayout.addWidget(self.setupBtn)
        rightLayout.addStretch(1)
        rightLayout.addWidget(self.addClientBtn)
        rightLayout.addWidget(self.clearTextBtn)

        rightWidget.setLayout(rightLayout)

        return rightWidget

    def setupFunc(self):

        port = int(self.portLine.text())
        self.server.setupFunc(port)
        self.server.start()


    def updateText(self,msg):
        self.text += msg + '\n'
        self.chatText.setText(self.text)

    def addClientFunc(self):

        w = ClientWindow()
        w.show()
        self.windowList.append(w)



if __name__ == "__main__":

    # server = socketserver.ThreadingTCPServer((HOST, PORT), ServerHandle)
    # server.serve_forever()
    QProcessEnvironment.systemEnvironment().insert("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())