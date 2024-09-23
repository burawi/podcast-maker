import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

class SimpleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Simple PyQt Test')
        label = QLabel('Hello, PyQt!', self)
        label.move(50, 50)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleWindow()
    sys.exit(app.exec_())