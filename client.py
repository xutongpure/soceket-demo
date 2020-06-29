import socket
import threading
import json

import PySide2
import config
from PySide2.QtWidgets import QApplication, QPlainTextEdit
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Signal, QObject
dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 客户端socket连接到 服务端
dataSocket.connect(config.client_settings['addr_port'])

class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    text_print = Signal(QPlainTextEdit, str)
    # 还可以定义其他信号
    update_table = Signal(str)



class Client(object):
    global dataSocket
    def __init__(self):
        self.name=None
        self.list=['ujhghcdf','ujhghcdf','ujhghcdf']
        self.msg=None
        self.id=None
        self.sock=dataSocket

        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        self.ui = QUiLoader().load("client_UI.ui")
        self.ms = MySignals()

        # 自定义信号的处理函数
        self.ms.text_print.connect(self.printToGui)



        # self.ui = QUiLoader().load(qfile_stats)
        IP1 = 'IP：' + config.IP1
        PORT1 = 'PORT：' + str(config.PORT1)
        self.ui.iip_text.setPlainText(IP1)
        self.ui.pport_text.setPlainText(PORT1)
        self.ui.button_confirm.clicked.connect(self.xingming)  #连接确认按钮
        self.ui.name_text.toPlainText()   #获取姓名框
        self.ui.fsck.toPlainText()#发送窗口
        self.ui.button_send.clicked.connect(self.fasong)  # 连接发送按钮
        self.ui.send_text.toPlainText()#私聊输入好友姓名
        self.ui.button_confirm.clicked.connect(self.siliao)  # 连接确认按钮

    def printToGui(self, fb, text):
        fb.appendPlainText(str(text))
        # fb.setPlainText(str(text))
        # fb.ensureCursorVisible()


    def siliao(self):
        self.id = self.ui.send_text.toPlainText()
        self.list[2] = self.id

    def fasong(self):
        self.msg = self.ui.fsck.toPlainText()
        if len(self.msg) == 0:
            self.ui.tongzh.setPlainText("空消息无法发送，请重试~！")
        self.list[1] = self.msg
        json_str = json.dumps(self.list)
        message = json_str.encode('utf-8')
        print(self.msg)
        try:
            self.sock.send(message)
            self.ui.tongzh.setPlainText("发送成功")
            print('发送成功~！')
        except :
            self.ui.tongzh.setPlainText("error")

    def xingming(self):
        self.name= self.ui.name_text.toPlainText()   #获取文本
        self.list[0] = self.name
        self.ui.tongzh.setPlainText("成功")
        print(self.name)
        print(self.id)          #[name,ms,silao]
        if self.name is None:
            # print("未注册，请重试")
            self.ui.tongzh.setPlainText("未注册，请重试")

    def send_msg(self):
        self.id = 'none'
        while True:
            self.ui.button_confirm.clicked.connect(self.xingming)
            self.ui.button_send.clicked.connect(self.fasong)
            self.ui.button_confirm.clicked.connect(self.siliao)

    def receive_msg(self,dataSocket):
        while True:
            data= dataSocket.recv(1024).decode('utf-8')
            if len(data) == 0:
                print('服务端主动断开...')
                break
            else:
                # self.ui.neiro.appendPlainText(data)
                self.ms.text_print.emit(self.ui.neiro, data)

    # def closeEvent(self, event:PySide2.QtGui.QCloseEvent):
    #     dataSocket.close()

if __name__ == '__main__':
    app = QApplication([])
    client = Client()
    client.ui.show()
    recv_theard = threading.Thread(target=client.receive_msg, args=(dataSocket,))
    recv_theard.setDaemon(True)
    recv_theard.start()
    app.exec_()

