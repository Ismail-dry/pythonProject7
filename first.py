from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import *
import sys


class PasswordDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Doğrulama")
        self.setGeometry(540, 320, 300, 150)
        self.setWindowIcon(QIcon("x.ico"))

        layout = QHBoxLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.check_password)
        self.cancelButon=QPushButton("Cancel")
        self.cancelButon.clicked.connect(self.cancel)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.cancelButon)

        self.setLayout(layout)
    def cancel(self):
        self.n=Window()
        self.n.show()
        self.close()
    def check_password(self):
        password = self.password_input.text()

        if password == "ucgen":


            from AdminLogin import LoginWindowForAdmin


            self.x = LoginWindowForAdmin()
            self.x.show()



            self.close()



        else:
            QMessageBox.warning(self, "Hata", "Yanlış parola! Lütfen tekrar deneyin.")




class Window(QWidget):

    def __init__(self):

        super().__init__()

        self.setGeometry(50,50,1080,640)
        self.setWindowTitle("REGISTER FOR")
        self.setWindowIcon(QIcon('x.ico'))
        self.show()
        self.Widget_For_first_screen()




    def Widget_For_first_screen(self):
        hbox=QHBoxLayout()

        #Admin için oluşturduğumuz button ile ilgili kodlar
        self.admin_button=QPushButton("Admin",self)
        self.admin_button.setFixedHeight(30)
        self.admin_button.setFixedWidth(200)
        self.admin_button.setStyleSheet("background-color: white; color black; border: 2px solid red; border-radius: 5px; font-family: Arial; font-size: 8pt;")
        self.admin_button.clicked.connect(self.open_admin_screen)



        #Users Bölümü için oluşturuduğumuz button ve kodları
        self.users_button=QPushButton("Users",self)
        self.users_button.setFixedWidth(200)
        self.users_button.setFixedHeight(30)
        self.users_button.setStyleSheet("background-color: white; color:black;border:2px solid red;border-radius:5px;font-family:Arial;font-size:8pt;")
        self.users_button.clicked.connect((self.open_user_screen))

        #layoutw
        hbox.addStretch()
        hbox.addWidget(self.users_button)
        hbox.addWidget(self.admin_button)
        hbox.addStretch()


        vbox=QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)



    def open_admin_screen(self):
        self.checkadminWindow=PasswordDialog()
        self.checkadminWindow.show()
        self.close()





    def open_user_screen(self):
      from UserLogin import LoginWindow
      self.w=LoginWindow()
      self.w.show()
      self.close()












if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
