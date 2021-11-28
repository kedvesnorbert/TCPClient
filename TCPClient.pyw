import os
import socket
import threading
import sys
import time
from datetime import datetime
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from functools import partial

IP = "127.0.0.1"
PORT = 27095
FORMAT = "UTF-8"
BUFLEN = 4096
ClientSocket = 0
MYCLIENTNAME = ""
CLIENTS = []
CURRENT_CLIENT = "EVERYBODY"
CHATLOGS = []
CURRENT_CLIENT_FOR_FILETRANSMISSION = ""
CURRENT_FILENAME_RECEIVED = ""
CURRENT_FILESIZE_RECEIVED = 0
FILEPATH = ""

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        self.lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        self.label.setText(text)

    def getText(self):
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
                usernamepw = str(len_usernamepw + len_usernamepw_full + 1) + '\t' + usernamepw
                usernamepw = usernamepw.encode(FORMAT)
                print(usernamepw)

                global ClientSocket
                ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        #global CHATLOGS
        #CHATLOGS.append(self.tempchatlog)
        #print(CHATLOGS)
        a = self.tempchatlog[3] + " " + self.tempchatlog[1] + ":\t" + self.tempchatlog[4]
        self.getMessageLabel().setText(self.getMessageLabel().toPlainText() + a + "\n")
        self.getMessageLabel().moveCursor(QtGui.QTextCursor.End)

    def receive_msg(self):
        global CURRENT_FILESIZE_RECEIVED
        while True:
            try:
                print("Receiving data from server ...")
                self.received_data = ClientSocket.recv(BUFLEN)
                self.receiveddata_len = len(self.received_data)
                self.datalength = self.received_data[:8].decode(FORMAT)
                self.datatype = self.datalength.split("\t")[1]
                self.datalength = int(self.datalength.split("\t")[0])
                print(self.datatype)
                if self.datatype == "7":
                    self.disconnect_btn.setEnabled(False)
                    self.sendfile_btn.setEnabled(False)
                    self.chatmsg.setEnabled(False)
                    self.sendmsg_btn.setEnabled(False)
                    self.acceptfile_btn.setEnabled(False)
                    self.rejectfile_btn.setEnabled(False)
                    print("Writing file....\n")
                    global CURRENT_FILENAME_RECEIVED
                    self.filename = "F_" + str(datetime.now().strftime("%Y%m%d%H%M%S")) + str(CURRENT_FILENAME_RECEIVED)
                    self.eOK = 1
                    with open(self.filename, "wb") as f:
                        while True:
                            self.received_data = ClientSocket.recv(BUFLEN)
                            if self.received_data.decode(FORMAT, "ignore").endswith("*ERR*\0"):
                                self.eOK = 0
                                break
                            if self.received_data.decode(FORMAT, "ignore").endswith("*EOF*"):
                                f.write(self.received_data[:-5])
                                break
                            f.write(self.received_data)
                    f.close()
                    global CURRENT_CLIENT_FOR_FILETRANSMISSION
                    if self.eOK == 0:
                        os.rename(self.filename, "This file did not arrived successfully" +
                                  str(datetime.now().strftime("%Y%m%d%H%M%S")) + ".unknown")
                    else:
                        self.text = "6\t" + str(MYCLIENTNAME) + "\t" + str(CURRENT_CLIENT_FOR_FILETRANSMISSION) + "\t2"
                        self.text = self.text.encode(FORMAT)
                        self.len_text = len(self.text)
                        self.len_text_ = len(str(self.len_text))
                        self.text = self.text.decode(FORMAT)
                        self.text = str(self.len_text + self.len_text_ + 1) + '\t' + self.text
                        self.text = self.text.encode(FORMAT)
                        ClientSocket.send(self.text)

                    print("File closed and ready.\n")
                    self.filesendingstatus.setHidden(True)
                    self.disconnect_btn.setEnabled(True)
                    self.sendfile_btn.setEnabled(True)
                    self.chatmsg.setEnabled(True)
                    self.sendmsg_btn.setEnabled(True)
                    self.acceptfile_btn.setEnabled(True)
                    self.rejectfile_btn.setEnabled(True)
                else:
                    print(self.received_data)
                    while self.receiveddata_len < self.datalength:
                        self.received_data = self.received_data + ClientSocket.recv(BUFLEN)
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
                        if self.datatype == 5:
                            if self.receiveddata_len == self.datalength:
                                self.getUsername = self.received_data.split("\t")[2]
                                CURRENT_CLIENT_FOR_FILETRANSMISSION = self.getUsername
                                self.getFilename = self.received_data.split("\t")[4].split('*')[0]
                                CURRENT_FILENAME_RECEIVED = self.getFilename
                                self.getFilesize = self.received_data.split("\t")[4].split('*')[1]
                                CURRENT_FILESIZE_RECEIVED = self.getFilesize
                                self.getFilesize = '%.2f' % float(int(self.getFilesize) / 1024 / 1024)
                                self.filemessage.setHidden(False)
                                self.acceptfile_btn.setHidden(False)
                                self.rejectfile_btn.setHidden(False)
                                self.filemessage.setText(
                                    str(self.getUsername) + " wants to send you a file (" 
                                    + str(self.getFilesize) + " MB). Do you accept it?")
                            else:
                                print("Error receiving packagetype 5")
                        else:
                            if self.datatype == 6:
                                if self.receiveddata_len == self.datalength:
                                    if self.received_data.split("\t")[4] == "0":
                                        self.filesendingstatus.setHidden(True)
                                    else:
                                        if self.received_data.split("\t")[4] == "1":
                                            self.filesendingstatus.setText("Sending file...")
                                            self.sendFILE()
                                        else:
                                            if self.received_data.split("\t")[4] == "2":
                                                self.disconnect_btn.setEnabled(True)
                                                self.sendfile_btn.setEnabled(True)
                                                self.chatmsg.setEnabled(True)
                                                self.sendmsg_btn.setEnabled(True)
                                                self.filesendingstatus.setHidden(True)
                                                self.acceptfile_btn.setEnabled(True)
                                                self.rejectfile_btn.setEnabled(True)
                            else:
                                if self.datatype == 2 or self.datatype == 3:
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
                            "Megszűnt a kommunikáció a szerverrel.\nA kapcsolat alaphelyzetbe állt.\nERR_CONNECTION_RESET\nThe connection was forcibly closed by the remote host."
                    else:
                        #e_error = str(e)
                        e_error = "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_ABORTED\nThe estabilished connection was aborted by the client."
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
        
    def sendFILE(self):
        self.tempclientlist = CLIENTS.split(',')
        self.tempclientlist.insert(0, "EVERYBODY")
        if (CURRENT_CLIENT not in self.tempclientlist):
            print("Message cannot be sent since the target client has disconnected!\n")
        else:
            if len(str(FILEPATH)) > 0:
                text = "7\t" + str(MYCLIENTNAME) + "\t" + str(CURRENT_CLIENT) + "\t"
                text = text.encode(FORMAT)
                len_text = len(text)
                len_text_ = len(str(os.path.getsize(FILEPATH)))
                text = text.decode(FORMAT)
                text = str(len_text + len_text_ + 1) + '\t' + text
                text = text.encode(FORMAT)
                print(text)
                try:
                    print("File Opened for reading...")
                    ClientSocket.send(text)
                    self.disconnect_btn.setEnabled(False)
                    self.sendfile_btn.setEnabled(False)
                    self.chatmsg.setEnabled(False)
                    self.sendmsg_btn.setEnabled(False)
                    self.acceptfile_btn.setEnabled(False)
                    self.rejectfile_btn.setEnabled(False)
                    with open(FILEPATH, "rb") as f:
                        while True:
                            chunk = f.read(BUFLEN)
                            if not chunk:
                                break
                            ClientSocket.send(chunk)
                    f.close()
                    print("File Closed and left loop\n")
                    time.sleep(5)
                    print("Slept 5 seconds ...")
                    ClientSocket.send("*EOF*".encode(FORMAT))
                    print("EOF sent\n")           
                except Exception as e:
                    chatW.hide()
                    loginW.show()
                    loginW.getLoginErrorMsg().setText(
                        "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt." + str(e))
    
    def logout(self):
        try:
            global ClientSocket
            ClientSocket.shutdown(1)
            ClientSocket.close()
        except Exception as e:
            chatW.hide()
            loginW.show()
            loginW.getLoginErrorMsg().setText(
                "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt." + str(e))

    def __init__(self):
        super().__init__()
        self.signal_senddata.connect(self.data_sent)
        self.setGeometry(50, 50, 1250, 950)
        self.setMinimumWidth(1250)
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
        self.newchatroom_btn.setEnabled(False)
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
        self.sendfile_btn.clicked.connect(self.selectFile)

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

        #Asking permission for file sending layout#
        self.sendfilelayout = QHBoxLayout()
        self.filemessage = QLabel("Abrakadabra wants to send you a file (512000 KB). Do you accept it?")
        self.filemessage.setStyleSheet(
            "color:black;font-size:11pt;margin-left:20px;margin-right:5pt;")
        self.acceptfile_btn = QPushButton("Yes")
        self.acceptfile_btn.setMaximumWidth(110)
        self.acceptfile_btn.setMinimumHeight(40)
        self.acceptfile_btn.setStyleSheet(
            "color:black;font-size:12pt;margin-left:5px;margin-right:1px;")
        self.display_a = partial(self.responseForAcceptingFile, "1")
        self.acceptfile_btn.clicked.connect(self.display_a)
        self.rejectfile_btn = QPushButton("No")
        self.rejectfile_btn.setMaximumWidth(110)
        self.rejectfile_btn.setMinimumHeight(40)
        self.rejectfile_btn.setStyleSheet(
            "color:black;font-size:12pt;margin-left:5px;margin-right:1px;")
        self.display_b = partial(self.responseForAcceptingFile, "0")
        self.rejectfile_btn.clicked.connect(self.display_b)
        self.sendfilelayout.addWidget(self.filemessage)
        self.sendfilelayout.addWidget(self.acceptfile_btn)
        self.sendfilelayout.addWidget(self.rejectfile_btn)
        self.filemessage.setHidden(True)
        self.acceptfile_btn.setHidden(True)
        self.rejectfile_btn.setHidden(True)
        self.chatlayout.addLayout(self.sendfilelayout)

        self.filesendingstatus = QLabel("Waiting for client's response...")
        self.filesendingstatus.setMaximumHeight(40)
        self.filesendingstatus.setMinimumHeight(39)
        self.filesendingstatus.setStyleSheet(
            "color:black;font-size:12pt;margin-left:20px;margin-right:20px;margin-top:10px;margin-bottom:10px;height:50px;background-color:red;")
        self.filesendingstatus.setHidden(True)
        self.chatlayout.addWidget(self.filesendingstatus)

        self.chatsendlayout = QHBoxLayout()
        self.chatlayout.addLayout(self.chatsendlayout)

        self.chatmsg = QLineEdit()
        self.chatmsg.setMaxLength(BUFLEN)
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
    
    def selectFile(self):
        self.dialog = QFileDialog()
        self.filter = "TXT files (*.txt)"
        self.filepath = QFileDialog.getOpenFileName(self.dialog, self.filter)[0]
        if len(str(self.filepath)) < 1:
            return
        global FILEPATH
        FILEPATH = self.filepath
        self.filesize = os.path.getsize(self.filepath)
        print(self.filesize)

        self.tempclientlist = CLIENTS.split(',')
        self.tempclientlist.insert(0, "EVERYBODY")
        if (CURRENT_CLIENT not in self.tempclientlist):
            print("Message cannot be sent since the target client has disconnected!\n")
        else:
            text = str(os.path.basename(self.filepath)) + "*" + str(self.filesize)
            if self.filesize > 0:
                text = "5\t" + str(MYCLIENTNAME) + "\t" + str(CURRENT_CLIENT) + "\t" + text
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
                    self.filesendingstatus.setHidden(False)
                    self.filesendingstatus.setText(
                        "Waiting for " + str(CURRENT_CLIENT) + "'s response for accepting the file ...")
                except:
                    chatW.hide()
                    loginW.show()
                    loginW.getLoginErrorMsg().setText(
                        "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt.")
    
    def responseForAcceptingFile(self, resp):
        self.tempclientlist = CLIENTS.split(',')
        self.tempclientlist.insert(0, "EVERYBODY")
        if (CURRENT_CLIENT_FOR_FILETRANSMISSION not in self.tempclientlist):
            print("Message cannot be sent since the target client has disconnected!\n")
        else:
            text = resp
            text = "6\t" + str(MYCLIENTNAME) + "\t" + str(CURRENT_CLIENT_FOR_FILETRANSMISSION) + "\t" + text
            text = text.encode(FORMAT)
            len_text = len(text)
            len_text_ = len(str(len_text))
            text = text.decode(FORMAT)
            text = str(len_text + len_text_ + 1) + '\t' + text
            text = text.encode(FORMAT)
            print(text)
            try:
                ClientSocket.send(text)
                if resp == "0":
                    self.filemessage.setHidden(True)
                    self.acceptfile_btn.setHidden(True)
                    self.rejectfile_btn.setHidden(True)
                    self.filesendingstatus.setHidden(True)
                else:
                    self.filemessage.setHidden(True)
                    self.acceptfile_btn.setHidden(True)
                    self.rejectfile_btn.setHidden(True)
                    self.filesendingstatus.setHidden(False)
                    self.filesendingstatus.setText("Receiving file....")
                    
            except:
                chatW.hide()
                loginW.show()
                loginW.getLoginErrorMsg().setText(
                    "Megszűnt a kommunikáció a szerverrel.\nERR_CONNECTION_RESET\nA kapcsolat alaphelyzetbe állt.")


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

app = QApplication(sys.argv)
loginW = LoginWindow()
loginW.show()
chatW = ChatWindow()
chatW.hide()
sys._excepthook = sys.excepthook
sys.excepthook = exception_hook
sys.exit(app.exec_())