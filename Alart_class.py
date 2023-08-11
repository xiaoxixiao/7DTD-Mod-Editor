import sys

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox


class AlertWindows(QWidget):
    def __init__(self, text="警告", parent=None):
        super().__init__()

        # 创建一个警告框
        alert = QMessageBox(self)
        alert.setIcon(QMessageBox.Warning)
        alert.setText(f"{text}!")
        alert.setWindowTitle("警告")
        alert.setStandardButtons(QMessageBox.Ok)

        alert.exec_()  # 显示警告框


if __name__ == '__main__':
    app = QApplication(sys.argv)
    alert_window = AlertWindows("特定的警告文本")
    sys.exit(app.exec_())
