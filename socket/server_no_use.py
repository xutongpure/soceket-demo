import socketserver
from PySide2.QtCore import QThread, Signal
from PySide2.QtWidgets import QPushButton,QApplication,QMainWindow,QWidget,QTextEdit,QLineEdit,QVBoxLayout,QHBoxLayout,QLabel,QGroupBox
import threading
import sys

HOST = '127.0.0.1'
PORT = 8888

class ServerHandle(socketserver.BaseRequestHandler):


    def handle(self) -> None:

        while True:
            try:
                data = self.request.recv(1024)
                self.request.sendall(data)
            except ConnectionResetError as e:
                break


    def setup(self) -> None:
        print('{} connected'.format(self.client_address))

    def finish(self) -> None:
        print('server finish')


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(800,680)
        self.setWindowTitle('Sock Server')

        self.addClientBtn = QPushButton('添加客户端')
        self.clearTextBtn = QPushButton('清除文本')
        self.setupBtn = QPushButton('启动服务器')
        self.setupBtn.clicked.connect(self.setupFunc)
        self.portLabel = QLabel('端口:')
        self.chatText = QTextEdit()
        self.portLine = QLineEdit()

        self.server = SocketServer()

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


        # self.server.serve_forever()
        self.server.start()

class SocketServer(QThread):

    def __init__(self):
        super(SocketServer, self).__init__()
        self.server = socketserver.ThreadingTCPServer((HOST, PORT), ServerHandle)


    def run(self):

        self.server.serve_forever()


if __name__ == "__main__":

    # server = socketserver.ThreadingTCPServer((HOST, PORT), ServerHandle)
    # server.serve_forever()
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())