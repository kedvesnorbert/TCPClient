import socket
import threading
import sys
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

IP = "127.0.0.1"
PORT = 27095
FORMAT = "UTF-8"
BUFLEN = 30
ClientSocket = 0
MYCLIENTNAME = ""


class ScrollLabel(QScrollArea):
    # contructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)
        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    def getText(self):
        #get text
        return self.label.text()


class LoginWindow(QWidget):
    signal_connect = pyqtSignal(bool)

    def openwindow(a):
        loginW.hide()
        chatW.show()
        global receive_thread
        receive_thread = threading.Thread(target=chatW.receive_msg)
        # will be killed after main program has finished execution
        receive_thread.daemon = True
        receive_thread.start()

    def start_connecting(self):
        t = threading.Thread(target=self.connect_to_server)
        t.start()

    def __init__(self):
        super().__init__()
        self.signal_connect.connect(self.openwindow)
        self.setGeometry(100, 100, 900, 900)
        self.setWindowTitle("Login")
        self.setStyleSheet("background-color:#09325D;")

        self.loginlayout = QVBoxLayout()
        self.loginlayout.setAlignment(Qt.AlignCenter)

        self.login_title = QLabel("Log In")
        self.login_title.setFixedWidth(400)
        self.login_title.setAlignment(Qt.AlignHCenter)
        self.login_title.setStyleSheet(
            "color:white; font-weight:bold;font-size:30pt;margin-bottom:80px;")
        self.loginlayout.addWidget(self.login_title)

        self.login_username = QLineEdit()
        self.login_username.setMaxLength(25)
        self.login_username.setFixedWidth(450)
        self.login_username.setPlaceholderText("Enter username")
        self.login_username.setStyleSheet(
            "color:white;font-size:13pt;background-color:transparent;width:100px;height:60px;border:none;border-bottom:3px solid black;")
        self.loginlayout.addWidget(self.login_username)

        self.login_pw = QLineEdit()
        self.login_pw.setMaxLength(25)
        self.login_pw.setFixedWidth(450)
        self.login_pw.setEchoMode(QLineEdit.Password)
        self.login_pw.setPlaceholderText("Enter password")
        self.login_pw.setStyleSheet(
            "color:white;font-size:13pt;background-color:transparent;width:100px;height:60px;border:none;border-bottom:3px solid black;")
        self.login_pw.returnPressed.connect(self.start_connecting)
        self.loginlayout.addWidget(self.login_pw)

        self.login_btn = QPushButton('CONNECT')
        self.login_btn.setFixedWidth(450)
        self.login_btn.setFixedHeight(100)
        self.login_btn.setStyleSheet(
            "font-size:20pt;color:white;margin-top:15px;border:none;background-color:#0D141A")
        self.loginlayout.addWidget(self.login_btn)
        self.login_btn.clicked.connect(self.start_connecting)

        self.login_errmsg = QLabel()
        self.login_errmsg.setFixedWidth(450)
        self.login_errmsg.setWordWrap(True)
        self.login_errmsg.setStyleSheet(
            "color:white;font-size:13pt;margin-top:20px;margin-bottom:20px;text-align:center")

        self.loginlayout.addWidget(self.login_errmsg)
        self.setLayout(self.loginlayout)

    def getLoginBtn(self):
        return self.login_btn

    def getUsernameEntered(self):
        return self.login_username

    def getPasswordEntered(self):
        return self.login_pw

    def getLoginErrorMsg(self):
        return self.login_errmsg

    def connect_to_server(self):
        loginW.getLoginBtn().setEnabled(False)
        loginW.getLoginErrorMsg().setText("LOADING ...\n")
        try:
            usernamepw = loginW.getUsernameEntered().text() + "\t" + \
                loginW.getPasswordEntered().text()
            if(len(loginW.getUsernameEntered().text()) < 3 or len(loginW.getPasswordEntered().text()) < 3):
                loginW.getLoginErrorMsg().setText(
                    "Nem írtál be felhasználónevet vagy jelszót!\nPlease enter username and password!")
            else:
                global MYCLIENTNAME
                MYCLIENTNAME = loginW.getUsernameEntered().text()
                usernamepw = "1\t \t \t" + usernamepw
                usernamepw = usernamepw.encode(FORMAT)
                len_usernamepw = len(usernamepw)
                len_usernamepw_full = len(str(len_usernamepw))
                usernamepw = usernamepw.decode(FORMAT)
                usernamepw = str(len_usernamepw +
                                 len_usernamepw_full + 1) + '\t' + usernamepw
                usernamepw = usernamepw.encode(FORMAT)
                print(usernamepw)

                global ClientSocket
                ClientSocket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                ClientSocket.connect((IP, PORT))
                ClientSocket.send(usernamepw)
                respi = ClientSocket.recv(BUFLEN)
                respi = respi.decode(FORMAT)
                print(respi)
                if respi == "E200\0":
                    self.signal_connect.emit(True)
                    print(MYCLIENTNAME)
                else:
                    ClientSocket.close()
                    if respi == "E404\0":
                        loginW.getLoginErrorMsg().setText(
                            "Hibás felhasználónév vagy jelszó!\nWrong username or password!\n")
                    if respi == "E403\0":
                        loginW.getLoginErrorMsg().setText(
                            "Ezzel a fiókkal már bejelentkeztek!\nThis account is currently is use!\n")
        except:
            loginW.getLoginErrorMsg().setText(
                "A szerver visszautasította a kapcsolódást! Server temporary not reachable.\nERR_CONNECTION_REFUSED\n")
            try:
                ClientSocket.close()
            except:
                print("Coulnd't close Clientsocket\n")
        loginW.getLoginBtn().setEnabled(True)


class ChatWindow(QWidget):
    signal_recvdata = pyqtSignal(str)
    signal_senddata = pyqtSignal(bool)

    def data_sent(self):
        print("Data sent!")

    def start_senddata_thread(self):
        t = threading.Thread(target=self.sendMSG)
        t.start()

    def display_msg(self, a):
        self.getMessageLabel().setText(self.getMessageLabel().toPlainText() + a + "\n")
        self.getMessageLabel().moveCursor(QtGui.QTextCursor.End)

    def receive_msg(self):
        while True:
            try:
                print("Receiving data from server ...")
                self.received_data = ClientSocket.recv(BUFLEN)
                self.receiveddata_len = len(self.received_data)
                self.datalength = self.received_data[:5].decode(FORMAT)
                self.datalength = int(self.datalength.split("\t")[0])
                print(self.received_data)
                while self.receiveddata_len < self.datalength:
                    self.received_data = self.received_data + ClientSocket.recv(BUFLEN)
                    self.receiveddata_len = len(self.received_data)
                    print(self.received_data)

                self.received_data = self.received_data.decode(FORMAT)
                self.datatype = int(self.received_data.split("\t")[1])
                self.received_data = self.received_data.split("\t")[2] + "\t" + self.received_data.split("\t")[4]
                if self.receiveddata_len == self.datalength:
                    self.signal_recvdata.emit(self.received_data)
                else:
                    self.signal_recvdata.emit(self.received_data + " MISSING DATA!!!")

            except Exception as e:
                print(str(e))
                chatW.hide()
                loginW.show()
                loginW.getLoginErrorMsg().setText(
                    "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt.")
                break

    def sendMSG(self):
        self.signal_senddata.emit(True)
        text = self.getChatmsg().text().strip()
        if len(text) > 0:
            text = "2\t" + str(MYCLIENTNAME) + "\t \t" + text
            text = text.encode(FORMAT)
            len_text = len(text)
            len_text_ = len(str(len_text))
            text = text.decode(FORMAT)
            text = str(len_text + len_text_ + 1) + '\t' + text
            text = text.encode(FORMAT)
            print(text)
            self.getChatmsg().setText('')
            try:
                ClientSocket.send(text)
                self.getMessageLabel().moveCursor(QtGui.QTextCursor.End)
            except:
                chatW.hide()
                loginW.show()
                loginW.getLoginErrorMsg().setText(
                    "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt.")

    def __init__(self):
        super().__init__()
        self.signal_senddata.connect(self.data_sent)
        self.setGeometry(100, 100, 900, 900)
        self.setWindowTitle("CHAT Client")

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.clients_label = ScrollLabel()
        self.clients_label.setText(
            "<center>List of connected clients</center><br>")
        self.clients_label.setAlignment(Qt.AlignTop)
        self.clients_label.setFixedWidth(400)
        self.clients_label.setStyleSheet("color:black;font-size:15pt;")
        self.layout.addWidget(self.clients_label)

        self.clients_label = self.clients_label.setText(
            self.clients_label.getText() + "\nElső\nmásodik\n...")

        self.chatlayout = QVBoxLayout()
        self.layout.addLayout(self.chatlayout)

        self.message_label = QTextEdit()
        self.message_label.setReadOnly(True)
        self.message_label.maximumWidth()

        self.message_label.setText("\n")
        self.message_label.moveCursor(QtGui.QTextCursor.End)
        self.message_label.setAlignment(Qt.AlignTop)
        self.message_label.setMinimumWidth(650)
        self.message_label.setStyleSheet(
            "color:black;font-size:13pt;margin-left:20px;margin-right:13pt;background-color:lightblue;")
        self.chatlayout.addWidget(self.message_label)

        self.chatsendlayout = QHBoxLayout()
        self.chatlayout.addLayout(self.chatsendlayout)

        self.chatmsg = QLineEdit()
        self.chatmsg.setMaxLength(BUFLEN+130)
        self.chatmsg.setPlaceholderText("Enter message to send!")

        # calling sendMSG() if Enter was pressed
        self.chatmsg.returnPressed.connect(self.start_senddata_thread)
        self.chatmsg.setStyleSheet(
            "margin-left:20px;margin-right:5px;font-size:12pt;color:black;height:75px;")

        self.chatsendlayout.addWidget(self.chatmsg)

        self.sendmsg_btn = QPushButton('SEND')
        self.sendmsg_btn.setStyleSheet(
            "font-size:12pt;color:red;height:65px;width:140px;")
        self.chatsendlayout.addWidget(self.sendmsg_btn)
        self.sendmsg_btn.clicked.connect(self.start_senddata_thread)
        self.sendmsg_btn.setAutoDefault(True)
        self.setLayout(self.layout)
        self.signal_recvdata.connect(self.display_msg)

    def getChatmsg(self):
        return self.chatmsg

    def getMessageLabel(self):
        return self.message_label


app = QApplication(sys.argv)
loginW = LoginWindow()
loginW.show()
chatW = ChatWindow()
chatW.hide()

sys.exit(app.exec_())
