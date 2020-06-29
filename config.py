import os
import threading
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader


IP = '127.0.0.1'
PORT = 8099
IP1='127.0.0.1'
PORT1=8099


class Confing(object):
    global IP, PORT
    global IP1, PORT1
    def __init__(self):
        global IP, PORT
        global IP1, PORT1
        self.ui = QUiLoader().load("config_UI.ui")
        self.ui.s_ip.setPlainText(IP)
        self.PORT = str(PORT)
        self.IP=IP
        self.ui.s_port.setPlainText(self.PORT)
        self.ui.p_ip.setPlainText(IP1)
        self.IP1=IP1
        self.PORT1 = str(PORT1)
        self.ui.c_port.setPlainText(self.PORT1)
        self.ui.sbutton.clicked.connect(self.start_server)
        self.ui.cbutton.clicked.connect(self.client_server)

    def start_oss(self):
        self.cmd = r'd:\terminal_jw\server.py'
        os.system(self.cmd)

    def start_server(self):
        th1 = threading.Thread(target=self.start_oss, args=())
        th1.start()

    def client_oss(self):
        self.cmd1 = r'd:\terminal_jw\client.py'
        os.system(self.cmd1)

    def client_server(self):
        th2 = threading.Thread(target=self.client_oss, args=())
        th2.start()








    def handleCalc(self):
        global IP, PORT
        global IP1, PORT1
        self.IP = self.ui.s_ip.toPlainText()
        self.PORT = self.ui.s_port.toPlainText()
        self.IP1= self.ui.p_ip.toPlainText()
        self.PORT1 = self.ui.c_port.toPlainText()

        IP=self.IP
        IP1 = self.IP1
        PORT=self.PORT
        PORT1=self.PORT1

        print(f'Server_IP:{IP}')
        print(f'Server_IP:{PORT}')
        print(f'Client_IP:{IP1}')
        print(f'Client_PORT:{PORT1}')
        QMessageBox.about(self.ui,
                          '修改成功',
                          f'''Server_IP:{IP}\nServer_IP:：{PORT}\nServer_IP:{IP1}\nServer_IP:：{PORT1}'''
                          )



settings = {
    'addr_port': (IP, PORT),
    'IP': IP,
    'PORT': PORT
}



client_settings={
'addr_port': (IP1, PORT1),
    'IP': IP1,
    'PORT': PORT1
}


if __name__ == '__main__':
    app = QApplication([])
    confing=Confing()
    confing.ui.show()
    app.exec_()