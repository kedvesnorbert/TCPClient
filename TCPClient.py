import socket
import threading
import sys
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

IP = "127.0.0.1"
PORT = 27095
FORMAT = "UTF-8"
BUFLEN = 300
ClientSocket = 0
MYCLIENTNAME = ""
CLIENTS = []
CURRENT_CLIENT = "EVERYBODY"
CHATLOGS = []


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
        self.lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        self.lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    def getText(self):
        #get text
        return self.label.text()

    def addMyWidget(self, w):
        self.lay.addWidget(w)
        self.lay.setAlignment(Qt.AlignTop)

    def removeMyWidget(self):
        while self.lay.count():
            item = self.lay.takeAt(0)
            widget = item.widget()
            widget.deleteLater()


class LoginWindow(QWidget):
    signal_connect = pyqtSignal(bool)

    def openwindow(a):
        loginW.hide()
        chatW.show()
        chatW.setWindowTitle("CHAT Client - " + str(MYCLIENTNAME))
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
        self.setGeometry(50, 50, 900, 950)
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
    signal_recvclientlist = pyqtSignal(str)

    def data_sent(self):
        print("Success!")

    def start_senddata_thread(self):
        t = threading.Thread(target=self.sendMSG)
        t.start()

    def display_msg(self, a):
        self.a_array = a.split("\t")
        self.tempchatlog = []
        self.tempchatlog.append(self.a_array[1]) # 0. type
        self.tempchatlog.append(self.a_array[2]) # 1. from_who
        self.tempchatlog.append(self.a_array[3]) # 2. to_whom
        self.tempchatlog.append(str(datetime.now().strftime("%H:%M"))) #3. time
        self.tempchatlog.append(self.a_array[4]) # 4. MESSAGE
        if self.tempchatlog[1] == MYCLIENTNAME:
            self.tempchatlog[1] = "You"
        global CHATLOGS
        CHATLOGS.append(self.tempchatlog)
        print(CHATLOGS)
        a = self.tempchatlog[3] + " " + self.tempchatlog[1] + ":\t" + self.tempchatlog[4]
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
                    self.received_data = self.received_data + \
                        ClientSocket.recv(BUFLEN)
                    self.receiveddata_len = len(self.received_data)
                    print(self.received_data)

                self.received_data = self.received_data.decode(FORMAT)
                self.datatype = int(self.received_data.split("\t")[1])
                if self.datatype == 4:
                    global CLIENTS
                    CLIENTS = self.received_data.split("\t")[4]
                    print("CLIENTS: " + CLIENTS)
                    self.signal_recvclientlist.emit(CLIENTS)
                else:
                    if self.datatype == 2:
                        if self.receiveddata_len == self.datalength:
                            self.signal_recvdata.emit(self.received_data)
                        else:
                            self.signal_recvdata.emit(self.received_data + " MISSING DATA!!!")
                    if self.datatype == 3:
                        if self.receiveddata_len == self.datalength:
                            self.signal_recvdata.emit(self.received_data)
                        else:
                            self.signal_recvdata.emit(self.received_data + " MISSING DATA!!!")
                    

            except Exception as e:
                print(str(e))
                if str(e)[0:16] == "[WinError 10053]":
                    e_error = \
                        "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_ABORTED\nThe estabilished connection was aborted by the client."
                else:
                    if str(e)[0:16] == "[WinError 10054]":
                        e_error = \
                            "Megszűnt a kommunikáció a szerverrel.\nA kapcsolat alaphelyzetbe állt.\nERR_CONNECTION_RESET\nThe connection was forcibly closed by the remote server."
                    else:
                        e_error = str(e)
                chatW.hide()
                loginW.show()
                loginW.getLoginErrorMsg().setText(e_error)
                return

    def sendMSG(self):
        self.signal_senddata.emit(True)

        self.tempclientlist = CLIENTS.split(',')
        self.tempclientlist.insert(0, "EVERYBODY")
        if (CURRENT_CLIENT not in self.tempclientlist):
            print("Message cannot be sent since the target client has disconnected!\n")
        else:
            text = self.getChatmsg().text().strip()
            if len(text) > 0:
                if str(CURRENT_CLIENT) == "EVERYBODY":
                    text = "2\t" + str(MYCLIENTNAME) + "\t" + \
                        str(CURRENT_CLIENT) + "\t" + text
                else:
                    text = "3\t" + str(MYCLIENTNAME) + "\t" + \
                        str(CURRENT_CLIENT) + "\t" + text
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

    def logout(self):
        try:
            ClientSocket.close()
        except:
            pass

    def __init__(self):
        super().__init__()
        self.signal_senddata.connect(self.data_sent)
        self.setGeometry(50, 50, 900, 950)
        self.setWindowTitle("CHAT Client")

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.clients_label_layout = QVBoxLayout()
        self.clients_label_layout.setAlignment(Qt.AlignTop)

        self.clients_labeltitle = QLabel()
        self.clients_labeltitle.setText(
            "<center>List of connected clients</center><br>")
        self.clients_labeltitle.setAlignment(Qt.AlignTop)
        self.clients_labeltitle.setFixedWidth(400)
        self.clients_labeltitle.setFixedHeight(50)
        self.clients_labeltitle.setStyleSheet(
            "color:black;font-size:15pt;margin-top:5px;")
        self.clients_label_layout.addWidget(self.clients_labeltitle)

        self.clients_label = ScrollLabel()
        self.clients_label.setAlignment(Qt.AlignTop)
        self.clients_label.setFixedWidth(400)
        self.clients_label.setFixedHeight(600)
        self.clients_label.setStyleSheet(
            "color:black;font-size:15pt;height:50px;text-align:left;")
        self.clients_label_layout.addWidget(self.clients_label)

        self.extrabutton_layout = QHBoxLayout()
        self.extrabutton_layout.setAlignment(Qt.AlignBottom)

        self.disconnect_btn = QPushButton("DISCONNECT")
        self.disconnect_btn.setStyleSheet(
            "text-align:center;font-size:12pt;color:white;height:62px;background-color:red")
        self.disconnect_btn.clicked.connect(self.logout)
        self.newchatroom_btn = QPushButton("NEW CHATROOM")
        self.newchatroom_btn.setStyleSheet(
            "text-align:center;font-size:12pt;color:black;height:62px;background-color:lightgray")
        self.extrabutton_layout.addWidget(self.disconnect_btn)
        self.extrabutton_layout.addWidget(self.newchatroom_btn)

        self.clients_label_layout.addLayout(self.extrabutton_layout)

        self.layout.addLayout(self.clients_label_layout)

        #Chat layout*******************#
        self.chatlayout = QVBoxLayout()
        self.layout.addLayout(self.chatlayout)

        self.chatheaderlayout = QHBoxLayout()
        self.chatheaderinfo = QLabel()
        self.chatheaderinfo.setStyleSheet(
            "background-color:lightblue;font-size:14pt;font-weight:bold;text-align:left;margin-left:20px;margin-left:20px;")
        self.chatheaderinfo.setMinimumHeight(47)
        self.chatheaderlayout.addWidget(self.chatheaderinfo)

        self.sendfile_btn = QPushButton("SEND FILE")
        self.sendfile_btn.setStyleSheet("font-size:12pt;")
        self.sendfile_btn.setMinimumHeight(47)
        self.sendfile_btn.setMaximumWidth(150)
        self.chatheaderlayout.addWidget(self.sendfile_btn)

        self.chatlayout.addLayout(self.chatheaderlayout)

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
            "font-size:12pt;color:black;height:65px;width:140px;")
        self.chatsendlayout.addWidget(self.sendmsg_btn)
        self.sendmsg_btn.clicked.connect(self.start_senddata_thread)
        self.sendmsg_btn.setAutoDefault(True)

        self.setLayout(self.layout)
        self.signal_recvdata.connect(self.display_msg)
        self.signal_recvclientlist.connect(self.addClientButtons)

    def getChatmsg(self):
        return self.chatmsg

    def getMessageLabel(self):
        return self.message_label

    def addClientButtons(self):
        self.clients_label.removeMyWidget()
        global CLIENTS
        global CURRENT_CLIENT
        tempCLIENTS = CLIENTS
        CLIENTS = CLIENTS.split(',')
        CLIENTS.insert(0, 'EVERYBODY')
        if str(MYCLIENTNAME) in CLIENTS: CLIENTS.remove(MYCLIENTNAME)

        for client in CLIENTS:
            self.clientbutton = QPushButton()
            self.clientbutton.setText(str(client))
            self.clientbutton.setObjectName(str(client))
            self.buttontext = self.clientbutton.text()
            if self.buttontext == CURRENT_CLIENT:
                self.clientbutton.setStyleSheet(
                    "height:50px;font-size:12pt;text-align:center;background-color:lightblue;border: 3px solid red;")
                self.clientbutton.setDisabled(True)
            else:
                self.clientbutton.setStyleSheet(
                    "height:50px;font-size:12pt;text-align:center;background-color:lightgray;")
                self.clientbutton.setDisabled(False)
            self.clients_label.addMyWidget(self.clientbutton)
            self.clientbutton.clicked.connect(self.switchChatUser)
        self.chatheaderinfo.setText(
            str(MYCLIENTNAME) + " --> " + str(CURRENT_CLIENT))
        if str(CURRENT_CLIENT) == "EVERYBODY":
            self.sendfile_btn.hide()
        else:
            self.sendfile_btn.show()
        CLIENTS = tempCLIENTS

    def switchChatUser(self):
        sending_button = self.sender()
        global CURRENT_CLIENT
        CURRENT_CLIENT = str(sending_button.objectName())
        print(CURRENT_CLIENT)

        self.clients_label.removeMyWidget()
        global CLIENTS
        tempCLIENTS = CLIENTS
        CLIENTS = CLIENTS.split(',')
        CLIENTS.insert(0, 'EVERYBODY')
        if str(MYCLIENTNAME) in CLIENTS: CLIENTS.remove(MYCLIENTNAME)

        for client in CLIENTS:
            self.clientbutton = QPushButton()
            self.clientbutton.setText(str(client))
            self.clientbutton.setObjectName(str(client))
            self.buttontext = self.clientbutton.text()
            if self.buttontext == CURRENT_CLIENT:
                self.clientbutton.setStyleSheet(
                    "height:50px;font-size:12pt;text-align:center;background-color:lightblue;border: 3px solid red;")
                self.clientbutton.setDisabled(True)
            else:
                self.clientbutton.setStyleSheet(
                    "height:50px;font-size:12pt;text-align:center;background-color:lightgray;")
                self.clientbutton.setDisabled(False)
            self.clients_label.addMyWidget(self.clientbutton)
            self.clientbutton.clicked.connect(self.switchChatUser)
        self.chatheaderinfo.setText(
            str(MYCLIENTNAME) + " --> " + str(CURRENT_CLIENT))
        if str(CURRENT_CLIENT) == "EVERYBODY":
            self.sendfile_btn.hide()
        else:
            self.sendfile_btn.show()
        CLIENTS = tempCLIENTS


app = QApplication(sys.argv)
loginW = LoginWindow()
loginW.show()
chatW = ChatWindow()
chatW.hide()

sys.exit(app.exec_())
