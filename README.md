# TCPClient written in Python (PyQT5)

Usage and conditions:

- The application can be used for communicating / chating with others that have this application.
- The TCP server must be running and must accept the clients.
- A login with username and password is also required.

Information:
  - A client only receives the messages that are addressed to him.
  - Messages are received in packages and in the order they were sent.
  - Functionalities:
      1. Log In (1)
      2. Sending message to everybody (2)
      3. Sending Private message (3)
      4. Receiving the updated list of the connected clients from the server (4)
      5. Sending a confirmation message in private before sending a file (5)
      6. Sending a confirmation message in private for (not) accepting the file transmission (6)
      7. File transmission in private with no limits (7)
  - The application's protocol is based on the TCP protocol. (TCP is connection-oriented, data transmission is reliable, but also slower, packages are received in order. TCP has no limits since the data is transmitted in STREAMING)
  - Package types are written at the Functionalities in the brackets
  - Exemple: 22\t3\tUser4\tUser123\tHy!

        -This is a private message where the length of the package is 22 bytes, packagetype is 3, the sender client is User4, the recipient is User123 and the message content is: Hy!.
        
###########################################
## Note
The client can send and receive message at the same time since the application uses a thread for sending data and another thread for receiving messages.


### Login
- After the application has started, the client needs to connect to the TCP server. This operation is hidden by the login method. If the username and password are correct, the connection to the server successfully builds, else the server closes that connection. It should be mentioned that an account can be used once at the same time.

![image](https://user-images.githubusercontent.com/93404199/143767149-0bce5d09-4380-4cae-8bf9-89a6241ef921.png)
- If the client has successfully logged in, the following window appears:
![image](https://user-images.githubusercontent.com/93404199/143767223-af181c98-8094-48f7-a16b-b6066cfb368c.png)

### Sending message to EVERYBODY
- In order to send a message to every single user that are currently conntected (these clients' names are shown at the left side of the window), you need to click on the EVERYBODY button, then type your message in the box at bottom of the window and hit the Enter or press the SEND button.
- This message appears in the message box that has lightblue background-color, with the current time and the clients' username.

### Sending PRIVATE message
- This functionality works the same way as the -Sending message to EVERYBODY-, except that you have to click on the button that contains the target clients' name. This type of message is sent between you and the selected client.
![image](https://user-images.githubusercontent.com/93404199/143767885-52c5f4a1-00bc-46bf-9dd5-af06ac27305a.png)

### Receiving the list of connected clients
- This happens automatically whenever a client logs in successfully, or disconnects. This list shows who is still connected. Note that you can send message only to a connected client.

### Sending a confirmation message in private before sending a file
- First of all, file transmitting is only allowed in private message sending.
- You need to select the file by clicking the SEND FILE button. After you selected the file, the application sends automatically a private message to the recipient to ask him whether he accepts the file or not. This message contains the selected file's name with its extension and the size of the file in Megabytes. A red background-colored label appears above the SEND button to inform you that you are waiting for the recipient's answer. If you get the YES answer from the client, the file transfer starts automatically, else the red background-colored label disappears and nothing will happen.

### Sending a confirmation message in private for (not) accepting the file transmission
- If a client wants to send you a file, you must confirm the transfer. A private message appears above the SEND button that contains the filename to receive and its size in MegaBytes. If you click the Yes button, you accep the file transmission and it starts automatically, else if you click the No button, the transfer will not happen.

