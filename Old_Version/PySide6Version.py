from PySide6.QtWidgets import QMainWindow, QTreeView, QVBoxLayout, QPushButton, QWidget, QFileDialog, QApplication
from xml.etree import ElementTree as ET

# 从class文件夹导入XmlTreeModel.py
from classes.XmlTreeModel import XmlTreeModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个树视图和一个加载按钮
        self.tree_view = QTreeView()
        self.load_button = QPushButton("加载 XML 文件")

        # 创建一个垂直布局并添加树视图和按钮
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        layout.addWidget(self.load_button)

        # 创建一个主窗口小部件并设置其布局
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 连接按钮的信号到加载文件的槽
        self.load_button.clicked.connect(self.load_xml)

    def load_xml(self):
        # 打开一个文件对话框来选择XML文件
        file_name, _ = QFileDialog.getOpenFileName(self, "选择 XML 文件", "", "XML files (*.xml)")

        if file_name:
            # 使用ElementTree解析XML文件
            tree = ET.parse(file_name)
            root = tree.getroot()

            # 使用自定义的XmlTreeModel来表示XML数据
            model = XmlTreeModel(root)
            self.tree_view.setModel(model)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
