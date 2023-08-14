import logging
import re

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem, QBrush
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QFileDialog, \
    QLabel, QTreeView, QSplitter, QTextEdit

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('log.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)


class XPathSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.file_path = ""
        # 允许外部文件拖入
        self.setAcceptDrops(True)

    def init_ui(self):
        # 创建主窗口
        self.setWindowTitle("XPath Selector V0.0.1")
        self.resize(800, 600)

        # 设置主布局
        self.main_widget = QWidget()  # 创建主窗口的主部件
        # 添加背景调色板
        palette = QPalette()
        # 设置背景颜色为深灰
        palette.setColor(QPalette.Window, QColor(32, 32, 32))
        # 设置背景调色板
        self.main_widget.setPalette(palette)
        # 设置主部件的自动填充背景
        self.main_widget.setAutoFillBackground(True)
        self.setCentralWidget(self.main_widget)  # 设置主窗口的主部件为主窗口的中心部件
        self.主布局 = QVBoxLayout()  # 创建主窗口的主部件的主布局为垂直布局
        self.main_widget.setLayout(self.主布局)  # 设置主窗口的布局为垂直布局

        # 创建一个横向布局
        self.h_layout = QHBoxLayout()
        # 设置布局外边距
        self.h_layout.setContentsMargins(10, 10, 10, 10)
        # 添加背景调色板
        palette = QPalette()
        # 设置背景颜色为浅灰
        palette.setColor(QPalette.Window, QColor(96, 96, 96))
        # 设置背景调色板
        self.main_widget.setPalette(palette)
        # 设置主部件的自动填充背景
        self.main_widget.setAutoFillBackground(True)

        # 向h_layout中添加按钮
        self.刷新按钮 = QPushButton("刷新")
        self.选择文件按钮 = QPushButton("选择文件")
        self.h_layout.addWidget(self.刷新按钮)
        self.h_layout.addWidget(self.选择文件按钮)
        # 绑定按钮的点击事件
        self.选择文件按钮.clicked.connect(self.选择文件事件)
        self.刷新按钮.clicked.connect(self.刷新事件)
        # 按钮下添加一个标签
        self.标签文本 = QLabel()
        self.h_layout.addWidget(self.标签文本)
        # 设置标签的文本
        self.标签文本.setText("文件路径：")

        # 在横向布局下面创建一个纵向布局
        self.v_layout = QVBoxLayout()
        # 添加一个树
        self.tree = QTreeView()
        self.tree.setStyleSheet("background-color: #454545;")
        self.v_layout.addWidget(self.tree)
        # 项目的点击事件
        self.tree.clicked.connect(self.tree_item_clicked)

        # 创建一个纵向布局，将横向布局和纵向布局添加到里面
        self.纵_左侧xpath选择器 = QVBoxLayout()
        self.纵_左侧xpath选择器.addLayout(self.h_layout)
        self.纵_左侧xpath选择器.addLayout(self.v_layout)

        # 创建一个标签
        self.标签文本_代码编辑区 = QLabel()
        self.标签文本_代码编辑区.setText("xpath路径：")
        self.标签文本2_代码编辑区 = QLabel()
        self.标签文本2_代码编辑区.setText("选择你的Xpath编辑模版（点击一下会用上面的xpath路径作为模板添加进去：")
        # 创建一个横向布局的按钮组
        self.横_代码编辑区_按钮组 = QHBoxLayout()
        self.xpath_set模板按钮 = QPushButton("set")
        self.xpath_append模块按钮 = QPushButton("append")
        self.xpath_remove模块按钮 = QPushButton("remove")
        self.横_代码编辑区_按钮组.addWidget(self.xpath_set模板按钮)
        self.横_代码编辑区_按钮组.addWidget(self.xpath_append模块按钮)
        self.横_代码编辑区_按钮组.addWidget(self.xpath_remove模块按钮)
        self.xpath_set模板按钮.clicked.connect(self.set_xpath_set模板)
        self.xpath_append模块按钮.clicked.connect(self.set_xpath_append模块)
        self.xpath_remove模块按钮.clicked.connect(self.set_xpath_remove模块)
        # 创建一个文本编辑框
        self.文本编辑框_代码编辑区 = QTextEdit()
        self.文本编辑框_代码编辑区.setStyleSheet("background-color: #454545; color: #ffffff;")

        # 创建一个纵向布局
        self.纵_代码编辑区 = QVBoxLayout()
        self.纵_代码编辑区.addWidget(self.标签文本_代码编辑区)
        self.纵_代码编辑区.addWidget(self.标签文本2_代码编辑区)
        self.纵_代码编辑区.addLayout(self.横_代码编辑区_按钮组)
        self.纵_代码编辑区.addWidget(self.文本编辑框_代码编辑区)

        # 创建一个分割器
        self.分割器 = QSplitter(Qt.Horizontal)     # 创建一个分割器，并设置为水平分割
        self.左侧部分 = QWidget()
        self.右侧部分 = QWidget()
        self.左侧部分.setLayout(self.纵_左侧xpath选择器)
        self.右侧部分.setLayout(self.纵_代码编辑区)
        self.分割器.addWidget(self.左侧部分)
        self.分割器.addWidget(self.右侧部分)

        # 创建一个标签
        self.底部标签 = QLabel()
        self.底部标签.setText("本软件由 泉户 黑崎 开发，仅供学习交流使用，不得用于商业用途！联系方式：QQ：1624910218")
        # 设置内外边距
        self.底部标签.setContentsMargins(10, 10, 10, 10)

        # 将分割器添加到主布局中
        self.主布局.addWidget(self.分割器)
        self.主布局.addWidget(self.底部标签)
        self.主布局.setStretch(0, 1)  # 设置分割器的伸缩因子为1
        self.主布局.setStretch(1, 0)  # 设置底部标签的伸缩因子为0

    def tree_item_clicked(self, index):
        logger.debug("检测到点击事件")
        # 获取点击的项目
        item = self.tree.model().itemFromIndex(index)
        # 获取项目的文本
        text = item.text()
        # ========== #
        # 递归获取父项目的文本
        父项目文本列表: list = []
        i = -1
        def 获取父项目文本(item, i) -> list:
            if item.parent() is not None:
                父项目文本列表.append({i: item.text()})
                i -= 1
                return 获取父项目文本(item.parent(), i)
            if item.parent() is None:
                父项目文本列表.append({i: item.text()})
                logger.debug(f"父项目文本列表：{父项目文本列表}")
                return 父项目文本列表
        # ========== #
        父项目文本列表 = 获取父项目文本(item, i)
        # ========== #
        def 处理父项目文本列表(父项目文本列表):
            拼接列表 = []

            def 提取信息(target):
                tag = 属性 = 值 = ""
                if "[@" in target:
                    匹配对象 = re.search(r'(.*?)\[@(.*?)\](?:=(.*))?', target)
                    if 匹配对象:
                        tag, 属性, 值 = 匹配对象.groups()
                elif "|" in target:
                    tag, 后部 = [part.strip() for part in target.split("|")]
                    后部 = 后部.replace("...", "").strip()
                    if "=" in 后部:
                        属性, 值 = [part.strip() for part in 后部.split("=")]
                elif "=" not in target:
                    tag = target.strip()
                return tag, 属性, 值

            if len(父项目文本列表) > 1:
                target1 = list(父项目文本列表[0].values())[0]
                target2 = list(父项目文本列表[1].values())[0]
                tag1, 属性1, 值1 = 提取信息(target1)
                tag2, 属性2, 值2 = 提取信息(target2)

                if tag1 == tag2 and 属性1 == 属性2 and 值1 == 值2:
                    拼接列表.append(f'{tag1}[@{属性1}]')
                elif tag1 == tag2:
                    拼接列表.append(f'{tag1}[@{属性1}]')
                else:
                    拼接列表.append(f'{tag1}[@{属性1}={值1}]')
                    拼接列表.append(f'{tag2}[@{属性2}={值2}]')

                for item in 父项目文本列表[2:]:
                    target = list(item.values())[0]
                    tag, 属性, 值 = 提取信息(target)
                    if tag and 属性:
                        拼接列表.append(f'{tag}[@{属性}={值}]')
                    elif tag:
                        拼接列表.append(tag)

            else:
                for item in 父项目文本列表:
                    target = list(item.values())[0]
                    tag, 属性, 值 = 提取信息(target)
                    if tag and 属性:
                        拼接列表.append(f'{tag}[@{属性}={值}]')
                    elif tag:
                        拼接列表.append(tag)

            拼接列表.reverse()
            print(f"拼接列表：{拼接列表}")
            return 拼接列表
        # ========== #
        拼接列表 = 处理父项目文本列表(父项目文本列表)
        # ========== #
        def 拼接列表元素(列表):
            路径名无后缀 = self.file_path.replace('.xml', '').split('/')[-1]
            拼接结果 = f'{路径名无后缀}/'
            for i in range(len(列表)):
                当前元素 = 列表[i].strip()  # 删除空白字符
                拼接结果 += 当前元素

                # 如果当前元素不是最后一个，且下一个元素不是[@xxx]形式，则添加/
                if i < len(列表) - 1 and not re.match(r'\[@.*?\]', 列表[i + 1].strip()):
                    拼接结果 += '/'
            logger.debug(f"拼接结果：{拼接结果}")
            return 拼接结果
        # ========== #
        拼接结果 = 拼接列表元素(拼接列表)
        # 设置标签文本_代码编辑区的文本
        self.标签文本_代码编辑区.setText(f'xpath路径：{拼接结果}')


    def 刷新事件(self):
        # 清空树控件
        self.tree_model.clear()
        # 清空标签文本
        self.标签文本.setText("文件路径：")

    def 选择文件事件(self):
        # 弹出文件选择对话框
        self.file_path = ""
        self.file_path = QFileDialog.getOpenFileName(self, "选择文件", "./", "xml文件(*.xml)")[0]
        # 连接标签文本更新槽函数
        self.标签文本.setText("文件路径：" + self.file_path)
        # 解析xml文件
        root = self.解析xml文件()

        self.创建标准项模型_设置树控件(root)

    def 解析xml文件(self):
        import xml.etree.ElementTree as ET
        try:
            root = ET.parse(self.file_path).getroot()
            logger.info("解析xml文件成功")
        except Exception as e:
            # 从字符串中解析xml
            root = ET.fromstring(self.file_path)
            if root is None:
                logger.error(e)
        return root

    # 重写外部文件拖入事件
    def dragEnterEvent(self, event):
        logger.debug("拖入文件")
        # 判断拖入的文件是否是xml文件
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.fileName().endswith(".xml"):
                    event.acceptProposedAction()    # 接受拖入文件

    def dropEvent(self, event: PySide6.QtGui.QDropEvent) -> None:
        logger.debug("放下文件")
        # 判断拖入的文件是否是xml文件
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.fileName().endswith(".xml"):
                    self.file_path = url.toLocalFile()
                    # 连接标签文本更新槽函数
                    self.标签文本.setText("文件路径：" + self.file_path)
                    # 解析xml文件
                    root = self.root_load = self.解析xml文件()
                    logger.debug("放下事件完成")
                    self.创建标准项模型_设置树控件(root)

    def 加载xml到树(self, xml节点, 树节点):
        for 子节点 in xml节点:
            # 获取第一个属性的描述
            第一个属性描述 = ""
            属性列表 = list(子节点.attrib.items())     # 将属性转换为列表
            if 属性列表:
                第一个属性, 值 = 属性列表[0]
                第一个属性描述 = f" | {第一个属性}={值}"
                if len(属性列表) > 1:
                    第一个属性描述 += "  ..."

            # 创建树中的节点
            子树节点 = QStandardItem(子节点.tag + 第一个属性描述)
            # 设置字体颜色为亮灰色
            子树节点.setForeground(QBrush(Qt.white))
            树节点.appendRow(子树节点)

            # 如果节点有内容，添加内容节点
            if 子节点.text and 子节点.text.strip():
                内容节点 = QStandardItem(子节点.text.strip())
                # 设置字体颜色为亮灰色
                内容节点.setForeground(QBrush(Qt.white))
                子树节点.appendRow(内容节点)

            # 如果有属性，创建属性子树
            if 子节点.attrib:
                # 属性子树节点 = QStandardItem(f'{子节点.tag}[@属性]')
                # 属性子树节点.setForeground(QBrush(Qt.white))
                # 子树节点.appendRow(属性子树节点)
                for 属性, 值 in 子节点.attrib.items():
                    属性节点 = QStandardItem(f'{子节点.tag}[@{属性}]={值}')
                    属性节点.setForeground(QBrush(Qt.white))
                    子树节点.appendRow(属性节点)

            # 递归调用
            self.加载xml到树(子节点, 子树节点)

    def 创建标准项模型_设置树控件(self, root):
        # 创建一个标准项模型
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['XML结构'])  # 设置表头
        # 添加root节点到模型
        根节点 = self.tree_model.invisibleRootItem()
        self.加载xml到树(root, 根节点)
        # 设置树控件的模型
        self.tree.setModel(self.tree_model)
        logger.info("解析xml文件成功")

    def set_xpath_set模板(self):
        xpath路径 = self.标签文本_代码编辑区.text().split("：")[-1]
        模板set = f"""<config>
    <set xpath="{xpath路径}"></set>
</config>
        """
        if xpath路径:
            self.文本编辑框_代码编辑区.append(模板set)
        else:
            self.文本编辑框_代码编辑区.append("请先选择好xpath路径")

    def set_xpath_append模块(self):
        xpath路径 = self.标签文本_代码编辑区.text().split("：")[-1]
        模板append = f"""<config>
    <append xpath="{xpath路径}"></append>
</config>
        """
        if xpath路径:
            self.文本编辑框_代码编辑区.append(模板append)
        else:
            self.文本编辑框_代码编辑区.append("请先选择好xpath路径")

    def set_xpath_remove模块(self):
        xpath路径 = self.标签文本_代码编辑区.text().split("：")[-1]
        模板remove = f"""<config>
    <remove xpath="{xpath路径}"></remove>
</config>
        """
        if xpath路径:
            self.文本编辑框_代码编辑区.append(模板remove)
        else:
            self.文本编辑框_代码编辑区.append("请先选择好xpath路径")


if __name__ == "__main__":
    app = QApplication([])
    window = XPathSelector()
    window.show()
    app.exec()
