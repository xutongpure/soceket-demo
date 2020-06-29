import socket
import threading
import json
from PySide2.QtWidgets import QApplication,QPlainTextEdit
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
import config

from PySide2.QtCore import Signal, QObject


# 自定义信号源对象类型，一定要继承自 QObject
class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    text_print = Signal(QPlainTextEdit, str)
    # 还可以定义其他信号
    update_table = Signal(str)


class Server(object):
    def __init__(self):
        # 在线客户端

        self.online_pool = {}
        self.listenSocket_class = server()    #窗体类服务器对象，这种写法在窗体类创建时自动创建服务类
        self.listenSocket = self.listenSocket_class.start_server()
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        self.ui = QUiLoader().load("server_UI.ui")
        # 实例化
        self.ms = MySignals()

        # 自定义信号的处理函数
        self.ms.text_print.connect(self.printToGui)

        IP1 = 'IP：' + config.IP
        PORT1 = 'PORT：' + str(config.PORT)
        self.ui.plainTextEdit_2.setPlainText(IP1)
        self.ui.port_txt.setPlainText(PORT1)
        self.ui.pushButton.clicked.connect(self.handels)
    def printToGui(self, fb, text):
        fb.appendPlainText(str(text))
        # fb.ensureCursorVisible()
        #清屏
    def handels(self):
        self.ui.server_text.clear()
    # 消息广播方法
    def broadcast(self, msg):
        for i in self.online_pool:
            self.online_pool[i].send(msg.encode('utf-8'))

    # 客户端登录方法
    def login(self, dataSocket, addr,username):
        # print('{} Login'.format(addr))
        print(f'{username}{addr} Login')
        print(type(username))
        str1=username + str(addr)+'Login'
        str2=(str1)
        # self.ui.server_text.appendPlainText(str2)
        self.ms.text_print.emit(self.ui.server_text, str2)
        if len(self.online_pool) >= 1:
            self.broadcast(f"{username}{addr}上线了...")
            str1=username  +str(addr)+"上线了"
            str2=str(str1)
            # self.ui.server_text.appendPlainText(str2)

            self.ms.text_print.emit(self.ui.server_text, str2)

        self.online_pool[username] = dataSocket

        # 通知新用户当前在线列表
        msg = '当前在线用户:\n'
        self.ui.server_text.appendPlainText(msg)
        # self.ms.text_print.emit(self.ui.server_text, msg)
        for i in self.online_pool:
            msg += (str(i) + '\n')
        print(msg)
        str2=str(msg)
        # self.ui.server_text.appendPlainText(str2)
        self.ms.text_print.emit(self.ui.server_text, str2)
        msg = msg.encode('utf-8')
        dataSocket.send(msg)

    # 客户端登出方法
    def logout(self, username):
        del self.online_pool[username]
        msg = '{} 下线了'.format(username)
        msg1=str(msg)
        self.ui.server_text.appendPlainText(msg1)
        # self.ms.text_print.emit(self.ui.server_text, msg1)
        self.broadcast(msg)

    # 发送消息方法
    def send_msg(self, username, msg):
        msg = msg.encode('utf-8')
        # print(self.online_pool)
        if username in self.online_pool:
            self.online_pool[username].send(msg)

    # 会话管理方法
    def session(self,dataSocket, addr):
        # 新用户登录,执行login()
        # self.login(dataSocket, addr)
        num=0
        while True:
            num=num+1
            data1 =dataSocket.recv(1024).decode('utf-8')
            # 如果收到长度为0的数据包,说明客户端 调用了secket.close()
            data2=json.loads(data1)
            # print(data2)
            data=data2[1]
            username=data2[0]
            id=data2[2]
            if num ==1:
                self.login(dataSocket, addr,username)
            if len(data) == 0:
                # print('{}客户端断开...'.format(addr))
                print('{}客户端断开...'.format(username))
                str1=username+'客户端断开...'
                str2=str(str1)
                # self.ui.server_text.appendPlainText(str2)
                self.ms.text_print.emit(self.ui.server_text, str2)
                # 此时需要调通客户端 登出 方法
                self.logout(username)
                break

            if id in self.online_pool.keys():
                print(username, ':', data)
                str1 = '(私聊)'+username + ':' + data
                str2 = (str1)
                # self.ui.server_text.appendPlainText(str2)
                self.ms.text_print.emit(self.ui.server_text, str2)
                # 此时服务端接收到正常的消息并发送给指定id的用户
                # content = str(addr) + ': '
                content = '(私聊)'+username + ': '
                data3 = content + data
                self.send_msg(id, data3)
                self.send_msg(username,data3)

            else:
                # print(addr, ':', data)
                print(username, ':', data)
                str1=username + ':' + data
                str2=(str1)
                # self.ui.server_text.appendPlainText(str2)
                self.ms.text_print.emit(self.ui.server_text, str2)
                # 此时服务端接收到正常的消息,广播给所有客户端
                content = username + ': '
                data = content + data
                for i in self.online_pool:
                    self.send_msg(i, data)

    # 开启显示信息和监听用户连接函数的线程
    def startNewThread(self):
        while True:
            # 在循环中，一直接受新的连接请求
            dataSocket, addr = self.listenSocket.accept()  # 返回一个元组addr，，产生一个新的socket对象 用来传输数据
            # 创建新线程处理和这个客户端的消息收发
            th = threading.Thread(target=self.session, args=(dataSocket, addr))
            th.setDaemon(True)
            th.start()

# socket类
class server():
    def start_server(self):
        # BUF_SIZE = 1024
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #创建socket对象
        listenSocket.bind(config.settings['addr_port']) #绑定soket
        listenSocket.listen(20)  # 接收的连接数，最大允许多少个socket连接
        return listenSocket   #运行socket

if __name__ == '__main__':
    print('服务器{}已启动!'.format(config.settings['addr_port']))
    app = QApplication([])
    server1 = Server()
    server1.ui.show()
    server1.ui.server_text.appendPlainText('服务器{}已启动!'.format(config.settings['addr_port']))
    th = threading.Thread(target=server1.startNewThread, args=())
    th.start()
    app.exec_()
