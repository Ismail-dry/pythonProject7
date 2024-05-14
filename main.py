import sys
from PyQt5.QtWidgets import QApplication
from first import Window



def main():
    app = QApplication(sys.argv)
    forward_window = Window()
    forward_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()