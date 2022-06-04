from PyQt5 import QtWidgets, QtCore, QtGui
from mainwindow import Ui_MainWindow
import sys
import socket
import threading
import errno
import time
connected = True


class Interface(QtWidgets.QMainWindow):
    def __init__(self):
        super(Interface, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Your Virtual Doctor")
        self.setWindowIcon(QtGui.QIcon("assets/doctor_logo.png"))

        self.questions = ['Do you have a cough?', 'Do you have a fever?', 'Do you have shortness of breath?',
                          'Are you experiencing any fatigue?', 'Do you have a sore throat?', 'Do you have a runny nose?',
                          'Do you have any muscle pain?', 'Do you have a headache?', 'Are you experiencing loss of taste or smell?']

        self.questionIndex = 0  
        
        self.ui.Question.setText(self.questions[self.questionIndex])
        self.answers = [] 
        self.ui.Yes.clicked.connect(lambda: self.reply("Yes"))
        self.ui.No.clicked.connect(lambda: self.reply("No"))

        self.HEADER = 30  
        self.PORT = 8000  
        self.FORMAT = 'utf-8'   
        self.connected = True

        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDRESS = (self.SERVER, self.PORT) 
        self.idle_status = False 
        self.status = "" 

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client.connect(self.ADDRESS)
        self.timer = QtCore.QTimer(self)

        self.timer.timeout.connect(self.time)

        self.timer.start(100)

        self.thread = threading.Thread(target=self.client_status)
        self.thread.start()

    def client_status(self):
        global connected
        while connected:
            try:
                try:
                    status_length = int(self.client.recv(self.HEADER).decode(self.FORMAT)) 
                except ValueError:
                    print(
                        "Connection ended because you got the required result")
                    connected = False
                
                self.status = self.client.recv(status_length).decode(self.FORMAT)
                print(self.status)
                if self.status == '!DISCONNECT':
                    self.idle_status = True
                    connected = False
                
            except ConnectionAbortedError:
                print("The GUI was closed ... ")
        self.client.close()
        print("Exiting recieving thread .. ")
        sys.exit()

    def reply(self, answer):
        global connected
        if not self.idle_status:
            if self.questionIndex < 9:
                message = answer.encode(self.FORMAT)  
                msg_length = f"{len(message):<{self.HEADER}}".encode(
                    self.FORMAT)  
                self.client.send(msg_length) 
                self.client.send(message)  
                self.answers.append(answer)
                item = QtWidgets.QTableWidgetItem(
                    "Auto Doctor:   " + str(self.questions[self.questionIndex]))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.ui.Chat.setItem(self.questionIndex*2, 0, item)
                item = QtWidgets.QTableWidgetItem(
                    str(self.answers[self.questionIndex]) + "   :You")
                item.setTextAlignment(QtCore.Qt.AlignRight)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.ui.Chat.setItem(self.questionIndex*2+1, 1, item)
                self.questionIndex += 1
                if self.questionIndex < 9:
                    self.ui.Question.setText(
                        self.questions[self.questionIndex])

            if self.questionIndex == 9:
                if self.ui.Yes.text() == "Okay, thank you":
                    if answer == "Yes":
                        item = QtWidgets.QTableWidgetItem(
                            self.ui.Yes.text() + "   :You")
                        item.setTextAlignment(QtCore.Qt.AlignRight)
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                        self.ui.Chat.setItem(self.questionIndex*2+1, 1, item)
                        self.ui.Yes.setText("")
                        self.ui.No.setText("")
                        self.ui.Question.setText("")
                        self.questionIndex += 1

                        finished_message = f"{len('!DISCONNECT'):<{self.HEADER}}" + \
                            '!DISCONNECT'
                        self.client.send(finished_message.encode(self.FORMAT))
                        connected = False
                    else:
                        for i in range(self.questionIndex+1):
                            item = QtWidgets.QTableWidgetItem("")
                            item.setFlags(QtCore.Qt.ItemIsEnabled)
                            self.ui.Chat.setItem(i*2, 0, item)
                            item = QtWidgets.QTableWidgetItem("")
                            item.setTextAlignment(QtCore.Qt.AlignRight)
                            item.setFlags(QtCore.Qt.ItemIsEnabled)
                            self.ui.Chat.setItem(
                                i*2+1, 1, item)

                        self.questionIndex = 0
                        self.ui.Yes.setText("Yes")
                        self.ui.No.setText("No")
                        self.ui.Question.setText(
                            self.questions[self.questionIndex])
                        self.answers = []

                else:
                    time.sleep(1)
                    diagnosis = self.detect()
                    item = QtWidgets.QTableWidgetItem(
                        "Auto Doctor:   " + diagnosis)
                    self.ui.Question.setText(diagnosis)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.ui.Chat.setItem(self.questionIndex*2, 0, item)
                    self.ui.Chat.horizontalHeader().setSectionResizeMode(0,
                                                                         QtWidgets.QHeaderView.ResizeToContents)
                    self.ui.Chat.horizontalHeader().setSectionResizeMode(
                        1, QtWidgets.QHeaderView.Stretch)
                    self.ui.Yes.setText("Okay, thank you")
                    self.ui.No.setText("I want to answer the questions again.")

    def stop_event(self, event):
        global connected
        print("EXITING ... ")
        connected = False
        if connected:
            finished_message = f"{len('!DISCONNECT'):<{self.HEADER}}" + \
                '!DISCONNECT'
            self.client.send(finished_message.encode(self.FORMAT))
        self.client.close()
        time.sleep(1)
        
    def detect(self):
        print(self.answers)
        return self.status

    def time(self):
        if self.idle_status:
            QtWidgets.QMessageBox.warning(
                self, "Connection Lost", "Connection was closed please open the UI again")
            sys.exit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = Interface()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
