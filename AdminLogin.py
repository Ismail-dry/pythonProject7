
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import sys
import sqlite3
from cryptography.fernet import Fernet








class LoginWindowForAdmin(QWidget):

    def __init__(self):

        super().__init__()

        self.setGeometry(50,50,1080,640)
        self.setWindowTitle("login")
        self.setWindowIcon(QIcon('x.ico'))
        self.WidgetsForLogin()

        self.show()




    def WidgetsForLogin(self):
        hbox = QHBoxLayout()


        hbox.addStretch(1)
        self.lblname=QLabel("Name:",self)
        self.txtname=QLineEdit(self)
        self.txtname.setStyleSheet("background-color: white;"+"border-radius: 10px;")
        self.txtname.setFixedWidth(300)
        self.txtname.setFixedHeight(20)
        pixmap = QPixmap("name2.png")

        sized_pixmap = pixmap.scaled(25, 25)
        self.lblname.setPixmap(sized_pixmap)
        hbox.addWidget(self.lblname)
        hbox.addWidget(self.txtname)

        hbox.addStretch(1)

        hbox2=QHBoxLayout()

        hbox2.addStretch(1)
        self.lblpsw = QLabel("psw:", self)
        self.txtpsw = QLineEdit( self)
        self.txtpsw.setEchoMode(QLineEdit.Password)
        self.txtpsw.setFixedHeight(20)
        self.txtpsw.setFixedWidth(300)



        pixmap = QPixmap("password2.png")
        sized2_pixmap = pixmap.scaled(25, 25)
        self.lblpsw.setPixmap(sized2_pixmap)
        self.txtpsw.setStyleSheet("background-color: white;"+"border-radius: 10px;")

        hbox2.addWidget(self.lblpsw)
        hbox2.addWidget(self.txtpsw)
        hbox2.addStretch(1)



        #button
        hbox3=QHBoxLayout()
        self.login_button=QPushButton("Login",self)
        self.login_button.setFixedHeight(20)
        self.login_button.setFixedWidth(100)
        self.login_button.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.login_button.clicked.connect(self.login)
        self.login_button.setCursor(Qt.PointingHandCursor)






        self.register_button=QPushButton("Register",self)
        self.register_button.setFixedHeight(20)
        self.register_button.setFixedWidth(100)
        self.register_button.setCheckable(True)
        self.register_button.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.register_button.clicked.connect(self.register)
        self.register_button.setCursor(Qt.PointingHandCursor)


        self.cancel_button=QPushButton("Cancel",self)
        self.cancel_button.setFixedHeight(20)
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.cancel_button.clicked.connect(self.cancel_to)
        self.cancel_button.setCursor(Qt.PointingHandCursor)







        hbox3.addStretch(2)
        hbox3.addWidget(self.cancel_button)
        hbox3.addWidget(self.login_button)
        hbox3.addWidget(self.register_button)
        hbox3.addStretch(2)

        # image
        hbox4=QHBoxLayout()

        self.image=QLabel(self)
        pixmapImage=QPixmap("indir.png")
        sized_pixmap3=pixmapImage.scaled(200,150)
        self.image.setPixmap(sized_pixmap3)


        self.admin_text=QLabel("Admin")
        font=QFont("Arial",18)
        font.setWeight(QFont.Bold)
        self.admin_text.setFont(font)

        hbox4.addStretch(1)
        hbox4.addWidget(self.image)

        hbox4.addStretch(1)

        hbox5=QHBoxLayout()
        hbox5.addStretch(1)
        hbox5.addWidget(self.admin_text)
        hbox5.addStretch(1)







        vbox=QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox4)
        vbox.addStretch(1)
        vbox.addLayout(hbox5)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addLayout(hbox3)

        vbox.addStretch(4)



        self.setLayout(vbox)

    def pop_message(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.setWindowTitle(" ")
        msg.setWindowIcon(QIcon('x.ico'))
        msg.exec_()

    def login(self):
        #username check
        xx=True
        if xx==False:
            self.pop_message('Enter Valid data!')
        else:
            username = self.txtname.text()
            password = self.txtpsw.text()
            conn = sqlite3.connect('Admin.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Username,Password,Key_F FROM Admin")
            val = cursor.fetchall()

            if len(val) >= 1:

                for x in val:
                    enc_name2 = x[0].encode()
                    key2 = x[2].encode()
                    chipher2 = Fernet(key2)
                    decr_name = chipher2.decrypt(enc_name2).decode()

                    enc_pw2 = x[1].encode()
                    key3 = x[2].encode()
                    chipher3 = Fernet(key3)
                    decr_pw = chipher3.decrypt(enc_pw2).decode()
                    if username == decr_name and password == decr_pw:
                        self.pop_message("Welcome " + "{}".format(username))
                        from AdminPanel import WindowAdminPanel

                        self.windowToProcess = WindowAdminPanel()
                        self.windowToProcess.show()
                        self.close()
                        break

                    else:
                        pass



                else:
                    self.pop_message("No User Found")

    def register(self):
        from AdminRegiter import AdminRegisterWindow
        self.windowForAdminRegister=AdminRegisterWindow()
        self.windowForAdminRegister.show()
        self.close()
    def cancel_to(self):
        from first import Window
        self.wi=Window()
        self.wi.show()
        self.close()










if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindowForAdmin()
    window.show()
    sys.exit(app.exec_())

