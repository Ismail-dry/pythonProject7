from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import sys
import sqlite3
from cryptography.fernet import Fernet
baglanti=sqlite3.connect("Admin.db")
islem=baglanti.cursor()
baglanti.commit()

table=islem.execute("Create Table if not Exists Admin(Name text,Username text,Password text,Key_F text)")
baglanti.commit()

class AdminRegisterWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(50,50,1080,640)
        self.setWindowTitle("Register For Admin")
        self.setWindowIcon(QIcon('x.ico'))
        self.WidgetForRegister()
        self.show()


    def WidgetForRegister(self):
        font = QFont("Arial", 8)
        font.setWeight(QFont.Bold)
        self.namelbl=QLabel("Name:")
        self.userLabel=QLabel("Username:")
        self.passLabel=QLabel("Password:")
        self.passLabel2=QLabel("Confirm Password:")
        self.tokenLabel=QLabel("Token")

        self.namelbl.setFont(font)
        self.userLabel.setFont(font)
        self.passLabel.setFont(font)
        self.passLabel2.setFont(font)



        self.nameEdit=QLineEdit(self)
        self.userEdit=QLineEdit(self)
        self.passEdit=QLineEdit(self)
        self.pass2Edit=QLineEdit(self)


        self.nameEdit.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.userEdit.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.passEdit.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.pass2Edit.setStyleSheet("background-color: white; color: black; border: 2px solid red; border-radius: 10px; font-family: Arial; font-size: 8pt;")


        self.nameEdit.setFixedWidth(300)
        self.nameEdit.setFixedHeight(30)
        self.userEdit.setFixedWidth(300)
        self.userEdit.setFixedHeight(30)
        self.passEdit.setFixedWidth(300)
        self.passEdit.setFixedHeight(30)
        self.pass2Edit.setFixedWidth(300)
        self.pass2Edit.setFixedHeight(30)


        self.passEdit.setEchoMode(QLineEdit.Password)
        self.pass2Edit.setEchoMode(QLineEdit.Password)



        self.register_button=QPushButton("Register",self)
        self.register_button.setFixedHeight(25)
        self.register_button.setFixedWidth(125)
        self.register_button.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.register_button.setFont(font)
        self.register_button.setCursor(Qt.OpenHandCursor)
        self.register_button.clicked.connect(self.newRegister)

        self.back_to_login=QPushButton("Cancel",self)
        self.back_to_login.setFixedHeight(25)
        self.back_to_login.setFixedWidth(125)
        self.back_to_login.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 10px; font-family: Arial; font-size: 8pt;")
        self.back_to_login.setFont(font)
        self.back_to_login.setCursor(Qt.OpenHandCursor)
        self.back_to_login.clicked.connect(self.backToLogin)



        hbox2=QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.back_to_login)
        hbox2.addWidget(self.register_button)
        hbox2.addStretch(1)




        vbox=QVBoxLayout()

        vbox.addStretch(1)
        vbox.addWidget(self.namelbl)
        vbox.addWidget(self.nameEdit)
        vbox.addStretch(1)
        vbox.addWidget(self.userLabel)
        vbox.addWidget(self.userEdit)
        vbox.addStretch(1)
        vbox.addWidget(self.passLabel)
        vbox.addWidget(self.passEdit)
        vbox.addStretch(1)
        vbox.addWidget(self.passLabel2)
        vbox.addWidget(self.pass2Edit)
        vbox.addStretch(1)
        vbox.addLayout( hbox2)
        vbox.addStretch(1)

        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def pop_message(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.setWindowTitle(" ")
        msg.setWindowIcon(QIcon('x.ico'))
        msg.exec_()

    def newRegister(self):
        name = self.nameEdit.text()
        username = self.userEdit.text()
        password = self.passEdit.text()
        password2 = self.pass2Edit.text()

        key = Fernet.generate_key()
        chipher = Fernet(key)
        encr_name = chipher.encrypt(name.encode()).decode()
        encr_Uname = chipher.encrypt(username.encode()).decode()
        encr_pw = chipher.encrypt(password.encode()).decode()

        islem.execute("SELECT Username,Password,Key_F FROM Admin")
        val = islem.fetchall()
        if not val:
            print("table is empty")
        flagF = False
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
                if username == decr_name:
                    self.pop_message("Kullanıcı mevcut")
                    flagF = True
                    break

                else:
                    pass



        else:
            print("dsas")
            if password == password2:
                try:
                    ekle = "insert into Admin(Name,Username,Password,Key_F) values(?,?,?,?)"
                    islem.execute(ekle, (encr_name, encr_Uname, encr_pw,  key.decode()))
                    baglanti.commit()

                    self.pop_message("Register Successful")



                except:
                    self.pop_message("Unsuccessful!")

            else:
                self.pop_message("Şifreler Eşleşmedi")

        if flagF == False:
            print("dsas")
            if password == password2:
                try:
                    ekle = "insert into Admin(Name,Username,Password,Key_F) values(?,?,?,?)"
                    islem.execute(ekle, (encr_name, encr_Uname, encr_pw,  key.decode()))
                    baglanti.commit()

                    self.pop_message("Register Successful")



                except:
                    self.pop_message("Unsuccessful!")
            else:
                self.pop_message("Şifreler Eşleşmedi")


    def backToLogin(self):
        from AdminLogin import LoginWindowForAdmin
        self.windowForLogin=LoginWindowForAdmin()
        self.windowForLogin.show()
        self.close()


if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = AdminRegisterWindow()
        window.show()
        sys.exit(app.exec_())
