# 导入所需的库
import logging
import re
import xml.etree.ElementTree as ET

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel, QAction
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QGroupBox, QListWidgetItem, QDialogButtonBox, QLayout)
from PySide6.QtWidgets import QFileDialog, QListWidget, QTextEdit, QMainWindow, QSplitter, \
    QTreeView, QWidget, QErrorMessage

from Alart_class import AlertWindows
from localization.localization_dict import localization_func

DEBUGTEST = 1
logging.addLevelName(DEBUGTEST, "DEBUGTEST")


def debugtest(self, message, *args, **kws):
    if self.isEnabledFor(DEBUGTEST):
        self._log(DEBUGTEST, message, args, **kws)
logging.Logger.debugtest = debugtest


# 配置logger模块以输出信息到console和一个文件
logger = logging.getLogger(__name__)
logger.setLevel(DEBUGTEST)

logger = logging.getLogger(__name__)
logger.setLevel(DEBUGTEST)

ch = logging.StreamHandler()
ch.setLevel(DEBUGTEST)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.debugtest("This is a debugtest log message!")


# 函数：在指定的布局中根据组件类型和索引来查找特定组件
def find_items_in_layout_recursive(layout, item_type=None):
    """
    递归地在指定的布局中查找指定类型的部件或布局。

    :param layout: 要搜索的布局。
    :param item_type: 要查找的部件或布局的类型。如果为None，则返回所有部件和布局。
    :return: 匹配的部件或布局的列表。
    """
    count = layout.count()
    matched_items = []

    for i in range(count):
        item = layout.itemAt(i)
        widget = item.widget()
        child_layout = item.layout()

        if widget:
            logger.debug(f"Checking widget: {widget} of type {type(widget)}")  # 调试输出

            if not item_type or isinstance(widget, item_type):
                matched_items.append(widget)
                logger.info(f"Found widget: {widget} of type {type(widget)}")  # 信息输出

            if hasattr(widget, 'layout') and widget.layout():
                matched_items.extend(find_items_in_layout_recursive(widget.layout(), item_type))

        elif child_layout:
            if not item_type or isinstance(child_layout, item_type):
                matched_items.append(child_layout)
                logger.info(f"Found layout of type {type(child_layout)}")  # 信息输出
            matched_items.extend(find_items_in_layout_recursive(child_layout, item_type))

    return matched_items


# 定义一个函数，用于将 XML 元素转换为树节点
def xml_to_tree(parent, xml_element):
    # Logging the function parameters
    logger.debug(f"Called xml_to_tree with parent: {parent}, xml_element tag: {xml_element.tag}")

    # 使用标签创建新的树节点
    item_text = localization_func(xml_element.tag)
    item = QStandardItem(item_text)

    # Logging the creation of a new tree node
    logger.debug(f"Created new tree node with text: {item_text}")

    # 创建一个字典来存储节点的相关信息
    node_data = {
        "type": "element",
        "tag": xml_element.tag,
        "attributes": xml_element.attrib
    }

    # Logging the node data
    logger.debug(f"Node data: {node_data}")

    # 将字典作为节点的数据存储
    item.setData(node_data, QtCore.Qt.UserRole + 1)
    parent.appendRow(item)

    # Logging the appending of new node to the parent
    logger.info(f"Appended new node with tag: {xml_element.tag} to parent")

    # 将每个属性作为新树节点的子节点
    for attr_name, attr_value in xml_element.attrib.items():
        attr_text = localization_func(attr_name) + ": " + localization_func(attr_value)
        attr_item = QStandardItem(attr_text)

        # 为属性创建一个字典来存储其相关信息
        attr_data = {
            "type": "attribute",
            "name": attr_name,
            "value": attr_value
        }

        # Logging the attribute data
        logger.debug(f"Attribute data: {attr_data}")

        # 将字典作为属性的数据存储
        attr_item.setData(attr_data, QtCore.Qt.UserRole + 1)
        item.appendRow(attr_item)

        # Logging the appending of the attribute to the node
        logger.info(f"Appended attribute {attr_name} with value {attr_value} to node with tag: {xml_element.tag}")

    # 继续递归处理子元素
    for child in xml_element:
        xml_to_tree(item, child)


# 定义一个 ModEditor 类，用来封装我们的应用
class ModEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化变量
        self.file_path = ""
        self.selected_node_full_path = ""

        # 设置窗口标题
        self.setWindowTitle("七日杀 Mod 编辑器")

        self.create_search_and_item_list()
        self.create_text_editor_and_tree()
        self.create_indent_settings()
        self.create_show_hide_buttons()
        self.assemble_main_layout()

        # 初始时隐藏设置部分
        self.indent_widget.hide()

        """
        ==========
        ↓↓↓ 绑定事件 ↓↓↓
        ==========
        """

        # 绑定列表框的选择事件，当用户在列表框中选择一个物品时调用 show_item_xml 方法
        self.item_listbox.itemSelectionChanged.connect(self.show_item_xml)

        # 绑定搜索框的变化事件，当搜索框的内容改变时调用 search_items 方法
        self.search_entry.textChanged.connect(self.search_items)

        # 将按钮的点击信号连接到 set_tab_width 方法
        self.indent_button.clicked.connect(self.set_tab_width)

        # 绑定树状图的点击事件，当用户点击树状图中的一个节点时调用 tree_item_clicked 方法
        self.tree_view.clicked.connect(self.tree_item_clicked)

        # 定义一个列表来存储所有的物品名称
        self.items = []

        # 定义一个字典来存储每个物品的 XML
        self.item_xmls = {}

        """
        ==========
        ↓↓↓ 菜单栏 ↓↓↓
        ==========
        """

        # 在菜单栏中添加一个“文件”菜单
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('文件')

        # 在“文件”菜单中添加一个“导入”菜单项，triggered 参数指定了点击菜单项时调用的函数
        open_action = QAction('导入', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # 启用文件拖放
        self.setAcceptDrops(True)

    def create_search_and_item_list(self):
        """
        创建搜索框和物品列表组件：本方法用于创建并配置搜索框和物品列表。

        - self.search_entry: QLineEdit组件，用于接收用户输入的搜索关键字。
        - self.item_listbox: QListWidget组件，用于展示物品列表。
        - self.list_layout: QVBoxLayout组件，垂直布局，用于组织搜索框和物品列表。
        - self.list_widget: QWidget组件，容纳整个垂直布局。

        通过这些组件，用户可以在搜索框中输入关键字进行搜索，然后在物品列表中查看和选择特定的物品。
        """
        self.search_entry = QLineEdit()
        self.item_listbox = QListWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.addWidget(self.search_entry)
        self.list_layout.addWidget(self.item_listbox)
        self.list_widget = QtWidgets.QWidget()
        self.list_widget.setLayout(self.list_layout)

    def create_text_editor_and_tree(self):
        """
        创建文本编辑器和树状图组件：本方法用于创建并配置文本编辑器、树状图和选择按钮。

        - self.text_editor: QTextEdit组件，用户可以在其中编辑文本。
        - self.editor_splitter: QSplitter组件，垂直分割，用于容纳文本编辑器和树状图。
        - self.tree_view: QTreeView组件，用于显示树状图结构。
        - self.tree_model: QStandardItemModel组件，用于为树状图提供数据。
        - self.select_button: QPushButton组件，显示“选择”，点击时将调用select_tree_item方法。

        通过这些组件，用户可以在文本编辑器中编辑文本，同时在树状图中查看和选择结构化的内容。
        """
        self.text_editor = QTextEdit()
        self.text_editor.setTabStopDistance(40)
        self.editor_splitter = QSplitter(QtCore.Qt.Vertical)
        self.editor_splitter.addWidget(self.text_editor)
        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.editor_splitter.addWidget(self.tree_view)
        self.select_button = QPushButton('选择')
        self.select_button.clicked.connect(self.select_tree_item)
        self.editor_splitter.addWidget(self.select_button)

    def create_indent_settings(self):
        """
        创建缩进设置组件：本方法用于创建并配置文本框缩进的设置组件。

        - self.indent_label: 一个标签，用于显示设置提示"设置文本框缩进"。
        - self.indent_input: 一个文本输入框，用于用户输入缩进的大小。
        - self.indent_button: 一个按钮，显示"确定"，用户点击后将应用缩进设置。
        - self.indent_layout: 一个水平布局，包含以上三个组件。
        - self.indent_widget: 一个窗口部件，使用水平布局。

        通过这些组件，用户可以方便地定义和更改文本框的缩进设置。
        """
        self.indent_label = QLabel('设置文本框缩进')
        self.indent_input = QLineEdit()
        self.indent_button = QPushButton('确定')
        self.indent_layout = QHBoxLayout()
        self.indent_layout.addWidget(self.indent_label)
        self.indent_layout.addWidget(self.indent_input)
        self.indent_layout.addWidget(self.indent_button)
        self.indent_widget = QWidget()
        self.indent_widget.setLayout(self.indent_layout)

    def create_show_hide_buttons(self):
        """
        创建显示/隐藏按钮组件：本方法用于创建并配置显示和隐藏设置部分的按钮。

        - self.show_button: 显示"显示'/'n设置"的按钮，点击时将显示设置部分。
        - self.hide_button: 显示"隐藏'/'n设置"的按钮，点击时将隐藏设置部分。
        - self.show_hide_button_layout: 垂直布局，包括显示和隐藏按钮，并设置其对齐方式为顶部对齐。

        通过这些组件，用户可以方便地在应用程序窗口中显示和隐藏设置部分。
        """
        self.show_button = QPushButton("显示\n设置")
        self.show_button.clicked.connect(self.show_settings)
        self.hide_button = QPushButton("隐藏\n设置")
        self.hide_button.clicked.connect(self.hide_settings)
        self.show_button.setStyleSheet("padding-left: 5px; padding-right: 5px; padding-top: 0px; padding-bottom: 0px;")
        self.hide_button.setStyleSheet("padding-left: 5px; padding-right: 5px; padding-top: 0px; padding-bottom: 0px;")
        self.show_hide_button_layout = QVBoxLayout()
        self.show_hide_button_layout.addWidget(self.show_button)
        self.show_hide_button_layout.addWidget(self.hide_button)
        self.show_hide_button_layout.setAlignment(QtCore.Qt.AlignTop)

    def assemble_main_layout(self):
        """
            组装主布局：本方法用于组装整个应用程序窗口的主要布局部分。

            1. 首先，将显示/隐藏按钮和缩进设置部分添加到设置布局中。
            2. 接着，将缩进设置部分和编辑器（包括文本编辑器和树状图）添加到垂直布局中。
            3. 将设置部分、左侧的搜索框和物品列表、右侧的编辑器组合到一个水平布局中。
            4. 最后，将这个水平布局设置为主窗口的中心窗口部件。

            整个布局结构如下：
            - 主水平分隔器（QSplitter）
                - 设置部分（垂直布局）
                    - 显示/隐藏按钮（垂直布局）
                    - 缩进设置部分（水平布局）
                - 左侧搜索框和物品列表（垂直布局）
                - 右侧编辑器部分（垂直布局）
                    - 缩进设置部分（水平布局）
                    - 编辑器分隔器（QSplitter）
                        - 文本编辑器（QTextEdit）
                        - 树状图（QTreeView）
        """
        self.setting_layout = QVBoxLayout()
        self.setting_layout.addLayout(self.show_hide_button_layout)
        self.setting_layout.addWidget(self.indent_widget)
        self.setting_widget = QtWidgets.QWidget()
        self.setting_widget.setLayout(self.setting_layout)

        self.qvbox_layout = QVBoxLayout()
        self.qvbox_layout.addWidget(self.indent_widget)
        self.qvbox_layout.addWidget(self.editor_splitter)  # 将编辑器和树状图组合到一起，放在一个垂直布局<--qvbox_layout>中
        self.editor_widget = QtWidgets.QWidget()
        self.editor_widget.setLayout(self.qvbox_layout)  # 将垂直布局<--qvbox_layout>放在一个窗口部件<--editor_widget>中

        self.main_splitter = QSplitter(QtCore.Qt.Horizontal)
        self.main_splitter.addWidget(self.setting_widget)
        self.main_splitter.addWidget(self.list_widget)  # 注意这里是list_widget，不是list_layout
        self.main_splitter.addWidget(self.editor_widget)  # 将设置部分、左侧的搜索框和物品列表和右侧的编辑器组合到一起，放在一个水平布局<--main_splitter>中

        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)
        layout.addWidget(self.main_splitter)

    def start_modify_mod(self, return_text):
        #
        pass

    # 当用户点击选择按钮时，这个方法会被调用
    def select_tree_item(self):
        logger.debug("进入 select_tree_item 函数")

        # 获取当前选择的树节点
        indexes = self.tree_view.selectedIndexes()

        # 如果没有选中的树节点，记录日志并返回
        if not indexes:
            logger.warning("没有选中的树节点")
            return

        # 使用已经保存的路径
        full_node_path = self.selected_node_full_path

        logger.info("选中节点的完整路径: %s", full_node_path)
        logger.info("文件路径: %s", self.file_path)

        # 弹出节点选择窗口
        dialog = NodeSelectionDialog(full_node_path, self.file_path)
        result = dialog.exec_()
        try:
            if result == 1:
                # 从对话框中获取返回的文本值
                returned_text = dialog.accepted_text
            else:
                returned_text = result

            logger.info("对话框结果: %s", returned_text)

            # 如果返回的文本以你选择的节点开头，那么就使用返回的文本
            if returned_text.startswith("你选择的节点:"):
                self.start_modify_mod(returned_text)
            # 向主界面添加一个布局，在文本编辑框和树状图的右边并且有一个分割器
        except Exception as e:
            logger.error("对话框错误: %s", e)
        logger.debug("退出 select_tree_item 函数")

    def get_full_node_path(self):
        path = self.selected_node_full_path
        logger.debug("获取节点的完整路径: %s", path)
        return path

    def tree_item_clicked(self, index):
        logger.info("点击了树状图中的一个节点")

        item = self.tree_model.itemFromIndex(index)
        path = []

        while item:
            # 使用 data 方法获取存储的字典
            node_data = item.data(QtCore.Qt.UserRole + 1)

            # 检查字典的类型（节点或属性）
            if node_data["type"] == "element":
                # 对于节点，直接添加标签名
                path.append(node_data["tag"])
                logger.debug("添加了节点: %s 到路径中", node_data["tag"])
            elif node_data["type"] == "attribute":
                # 对于属性，添加形如 [@name='value'] 的表示
                attr_name = node_data["name"]
                attr_value = node_data["value"]
                path.append("[@{}='{}']".format(attr_name, attr_value))
                logger.debug("添加了属性: %s 到路径中", "[@{}='{}']".format(attr_name, attr_value))

            item = item.parent()

        # 反转路径并连接
        path = path[::-1]
        if path and path[-1].startswith("[@"):
            self.selected_node_full_path = "/".join(path[:-1]) + path[-1]
        else:
            self.selected_node_full_path = "/".join(path)

        logger.info("完成节点路径解析，选中了节点: %s", self.selected_node_full_path)

    def show_settings(self):
        logger.debug("开始显示设置部分")
        self.indent_widget.show()
        logger.info("设置部分已显示")

    def hide_settings(self):
        logger.debug("开始隐藏设置部分")
        self.indent_widget.hide()
        logger.info("设置部分已隐藏")

    def set_tab_width(self):
        new_width = int(self.indent_input.text())
        logger.debug("从输入框中获取新的缩进宽度: %s", new_width)
        self.text_editor.setTabStopDistance(new_width)
        logger.info("文本编辑器的缩进宽度已设置为: %s", new_width)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.info("拖放的内容包含URL，已接受拖放操作")

    def dropEvent(self, event):
        logger.debug("正在处理拖放事件")
        for url in event.mimeData().urls():  # 遍历所有拖放的文件
            file_path = url.toLocalFile()  # 获取文件路径
            logger.info("拖放了文件: %s", file_path)
            self.load_file(file_path)  # 这个方法需要你自己实现
        logger.info("所有拖放的文件已处理完毕")

    # 创建一个新的方法来加载文件
    def load_file(self, filename):
        logger.info("开始加载文件: %s", filename)

        try:
            # 解析选中的 XML 文件
            tree = ET.parse(filename)
            root = tree.getroot()
            logger.debug("成功解析文件")

            # 清空物品名称列表和物品 XML 字典
            self.items.clear()
            self.item_xmls.clear()

            # 定义一个列表来存储我们感兴趣的属性
            interested_attributes = ['name', 'id', 'file', 'key', 'xpath']

            # 递归函数，用于遍历XML文件中的每个节点
            def process_node(node):
                for attr in interested_attributes:
                    value = node.get(attr)
                    if value and value not in self.items:  # To ensure no duplicates
                        self.items.append(value)
                        self.item_xmls[value] = ET.tostring(node, encoding='unicode')
                        logger.debug(f"添加了 {attr}: {value} 到列表中")

                # 递归处理每个子节点
                for child in node:
                    process_node(child)

            process_node(root)

            # 更新列表框
            self.update_listbox()
            logger.info("列表框已更新")

            # 如果没有出现错误，将文件路径存储在 self.file_path 中
            self.file_path = filename
            logger.info("文件路径已存储: %s", self.file_path)

        except ET.ParseError:
            # 如果在解析 XML 文件时出现错误，显示一个错误对话框
            logger.error("解析文件时出现错误: %s", filename)
            error_dialog = QErrorMessage()
            error_dialog.showMessage('无法读取文件，可能文件类型不正确或者文件内容无法解析')
            error_dialog.exec_()

        except ET.ParseError:
            # 如果在解析 XML 文件时出现错误，显示一个错误对话框
            logger.error("解析文件时出现错误: %s", filename)
            error_dialog = QErrorMessage()
            error_dialog.showMessage('无法读取文件，可能文件类型不正确或者文件内容无法解析')
            error_dialog.exec_()

    # open_file 方法会在用户点击“导入”菜单项时被调用
    def open_file(self):
        logger.info("开始打开文件选择对话框")

        # 打开一个文件选择对话框，让用户选择要打开的文件
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "XML files (*.xml)")

        # 如果用户选择了一个文件
        if filename:
            logger.debug("用户选择了文件: %s", filename)
            # 在加载新文件之前清空 self.file_path
            self.file_path = ""
            self.load_file(filename)
        else:
            logger.warning("用户未选择文件")

    def search_items(self):
        # 获取搜索框中的文本
        search_text = self.search_entry.text()
        logger.debug("搜索框中的文本为: %s", search_text)

        # 清空列表框
        self.item_listbox.clear()

        # 添加所有包含搜索文本的物品名称到列表框中
        matched_items = [item for item in self.items if search_text.lower() in item.lower()]
        for item in matched_items:
            self.item_listbox.addItem(item)

        logger.info("找到 %d 个匹配的物品", len(matched_items))

    # show_item_xml 方法会在用户在列表框中选择一个物品时被调用
    def show_item_xml(self):
        logger.info("开始显示选中的物品的XML内容")

        # 获取选中的物品名称
        item_name = self.item_listbox.currentItem().text()
        logger.debug("选中的物品名称为: %s", item_name)

        # 获取物品的 XML
        item_xml = self.item_xmls.get(item_name, "")

        if not item_xml:
            logger.warning("未找到 %s 的 XML 内容", item_name)
            return

        # 显示物品的 XML 在文本编辑器中
        self.text_editor.setText(item_xml)
        logger.debug("物品的XML已加载到文本编辑器中")

        # 将物品的 XML 显示在树状图中
        self.tree_model.clear()
        root = ET.fromstring(item_xml)
        xml_to_tree(self.tree_model.invisibleRootItem(), root)
        logger.info("%s 的 XML 已加载到树状图中", item_name)

    def update_listbox(self):
        logger.info("开始更新列表框内容")

        # 清空列表框
        self.item_listbox.clear()

        # 添加所有物品名称到列表框中
        for item in self.items:
            self.item_listbox.addItem(item)
        logger.debug("所有物品名称已添加到列表框中")


class NodeSelectionDialog(QDialog):
    """
    选择节点路径的对话框
    """

    def __init__(self, node_path, file_path, parent=None):
        super().__init__(parent)
        self.level_dict = {}
        self.setWindowTitle("选择节点路径")
        self.file_path = file_path
        self.node_path = node_path
        self.accepted_text = None

        # 主布局
        layout = QVBoxLayout(self)
        # 添加标签
        label = QLabel(f"你选择的节点: {self.node_path}")
        layout.addWidget(label)
        # 添加横向布局<---h_layout--->
        h_layout = QHBoxLayout()
        self.all_list_layout = h_layout
        layout.addLayout(h_layout)

        # 创建按钮（确认、取消）
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        # 将确认取消按钮放置到中心
        layout.setAlignment(button_box, Qt.AlignCenter)


        # 设置布局
        self.setLayout(layout)

        level_dict, xml_root = self.xml_tree()  # 获取xml树
        self.create_list(level_dict, h_layout)  # 创建列表
        # 获取h_layout中的所有窗体
        widgets = self.get_all_widgets(h_layout)
        logger.info(f"widgets:{widgets}")

    def accept(self):
        """
        从all_list_layout的父布局中查找所有QLabel部件，并返回第一个文本不符合"选择第n级节点"格式的QLabel的文本。
        """
        try:
            logger.info("执行accept方法...")

            # 获取all_list_layout的父对象
            parent_of_all_list_layout = self.all_list_layout.parentWidget()  # 使用parentWidget()方法
            if parent_of_all_list_layout:
                logger.debug(f"找到all_list_layout的父部件: {parent_of_all_list_layout}")

                # 使用find_items_in_layout_recursive函数查找所有的QLabel部件
                all_labels = find_items_in_layout_recursive(parent_of_all_list_layout.layout(), QLabel)
                logger.debug(f"找到的QLabel总数: {len(all_labels)}")

                for label in all_labels:
                    # 确保找到的对象确实是QLabel的实例，并且文本不符合 "选择第n级节点" 的格式
                    if isinstance(label, QLabel) and not re.match(r"选择第\d+级节点", label.text()):
                        logger.info(f"返回文本: {label.text()}")
                        self.accepted_text = label.text()
                        self.setResult(1)  # 设置返回值为 1
                        self.done(1)  # 关闭窗口并设置返回值
                        return

            logger.warning("未找到合适的QLabel文本。")
            self.setResult(0)
            self.done(0)
        except Exception as e:
            logger.error(e)
            self.setResult(0)
            self.done(0)

    def get_all_widgets(self, layout):
        """
        获取布局中的所有部件
        :param layout:
        :return:
        """
        logger.debug("开始从布局中获取所有部件")

        widgets = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:  # 确保找到的项目是部件（因为布局可以包含其他布局或空白空间）
                widgets.append(widget)
                if hasattr(widget, 'text') and callable(widget.text):
                    logger.info(f"找到部件: {widget.text()}")
                else:
                    logger.info(f"找到部件: {str(widget)}")

        return widgets

    def create_list(self, level_dict, layout):
        """
        根据 level_dict 创建列表
        :param level_dict:
        :param layout:
        :return:
        """
        logger.info("开始根据 level_dict 创建列表")

        for key, value in level_dict.items():
            # 在value最前面添加一个空字符串，用于表示不选择该节点
            value = [''] + list(value)
            logger.debug(f"处理 key: {key}, value: {value}")
            self.add_list_widget(layout, value, key)
        logger.info("列表创建完成")

    def xml_tree(self):
        """
        解析当前选择的XML文件
        :return: level_dict, xml_root；level_dict是一个字典，key是层级，value是该层级的所有节点，xml_root是XML的根节点
        """
        logger.info("开始解析 XML 文件: %s", self.file_path)

        # Parse the XML file
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            logger.debug("成功解析 XML 文件")

            def traverse(node, level=1, path=""):
                if level not in self.level_dict:
                    self.level_dict[level] = set()

                # Update the path
                current_path = path + '/' + node.tag if path else node.tag

                # Add the current path to the set
                self.level_dict[level].add(current_path)
                logger.debug(f"添加路径 {current_path} 到 level {level}")

                for child in node:
                    traverse(child, level + 1, current_path)  # Pass the current path to the next recursion

            self.level_dict = {}
            traverse(root)

            # Convert sets to lists
            for key, value in self.level_dict.items():
                self.level_dict[key] = list(value)
            logger.info(f"完整的 level_dict: {self.level_dict}")

        except ET.ParseError:
            logger.error(f"解析 XML 文件时出现错误: {self.file_path}")
        except FileNotFoundError:
            logger.error(f"未找到 XML 文件: {self.file_path}")
        except Exception as e:
            logger.error(f"出现意外错误: {e}")

        return self.level_dict, root

    def add_list_widget(self, layout, values, key):
        """
        为布局(变量)添加列表部件
        :param layout:
        :param values:
        :param key:
        :return:
        """
        try:
            logger.debug("开始为布局添加列表部件")
            # 创建GroupBox
            group_box = QGroupBox(self)
            # 设置标题
            group_box.setTitle(f"选择第 {key} 级节点")
            group_layout = QVBoxLayout()
            group_box.setLayout(group_layout)  # 设置 QGroupBox 的布局
            layout.addWidget(group_box)  # 将 QGroupBox 添加到布局中

            # 创建输入框，输入事件和列表框绑定，用于搜索列表框中的内容
            # 创建输入框
            search_edit = QLineEdit(self)
            group_layout.addWidget(search_edit)


            # 创建列表框体
            list_widget = QListWidget(self)
            group_layout.addWidget(list_widget)

            # 输入事件和列表框绑定，用于搜索列表框中的内容
            search_edit.textChanged.connect(lambda text, lw=list_widget: self.filter_list_widget(lw, text))
        except Exception as e:
            logger.error(f"在 add_list_widget 函数中出现异常: {e}")
            return None
        try:
            for stored_value in values:
                logger.debug("添加值: %s", stored_value)
                display_value = stored_value.split('/')[-1]  # 只显示最后一级的名称
                logger.debug("显示值: %s", display_value)
                item = QListWidgetItem(display_value)  # 显示的值
                logger.debug("为列表部件添加条目: %s", display_value)
                item.setData(Qt.UserRole, stored_value)  # 存储的值
                logger.debug("为列表部件添加数据: %s", stored_value)
                list_widget.addItem(item)

            logger.info("成功为布局添加了一个列表部件，其中包含 %d 个条目", len(values))

        except Exception as e:
            logger.error(f"在 add_list_widget 函数中出现异常: {e}")

        # 连接 itemClicked 信号到 handle_item_click 函数
        list_widget.itemClicked.connect(self.list_item_click)
        self.update_list_widget_max_width(list_widget)

    def list_item_click(self, item):
        """
        处理列表部件的条目点击事件
        :param item:
        :return:
        """
        # 获取显示的值
        display_value = item.text()

        # 获取存储的值
        stored_value = item.data(Qt.UserRole)
        logger.info(f"点击了条目: 显示值 = {display_value}, 存储值 = {stored_value}")

        # 获取所有 QListWidget 部件和 XML 的层级结构
        matched_widgets = find_items_in_layout_recursive(self.all_list_layout, QListWidget)
        level_dict = self.level_dict

        # 获取点击的 QListWidget 的父对象QGroupBox
        parent_widget = item.listWidget().parent()
        # 打印父对象的类名以验证
        logger.debug(f"父对象的类名: {parent_widget.__class__.__name__}")
        # 获取父对象的标题
        parent_title = parent_widget.title()
        # 提取出 选择第{}级节点 中的数字
        this_level = int(re.findall(r'\d+', parent_title)[0])
        logger.debug(f"选择层级: {this_level}")

        # 检查display_value是否有多个xml路径
        matching_paths_before = []
        for value in level_dict.get(this_level, []):  # 使用.get()以确保在键不存在时返回空列表
            if value.split('/')[-1] == display_value:
                matching_paths_before.append(value)

        if len(matching_paths_before) > 1:
            logger.info(f"在当前层级{this_level}中找到了多个匹配的XML路径: {matching_paths_before}")
        else:
            logger.info(
                f"在当前层级{this_level}中找到了一个匹配的XML路径: {matching_paths_before[0] if matching_paths_before else 'None'}")

        # 检查display_value后面是否还有子节点
        matching_paths_after = []

        # 从level_dict中获取所有可能的子节点路径
        all_paths = [path for paths in level_dict.values() for path in paths]

        for matching_path in matching_paths_before:
            for path in all_paths:
                # 检查是否存在以matching_path为前缀的路径
                if path.startswith(matching_path) and path != matching_path:
                    matching_paths_after.append(path)

        if matching_paths_after:
            logger.info(f"找到了以下子节点: {matching_paths_after}")
        else:
            logger.info(f"{display_value} 没有子节点")
        logger.debug(f"matching_paths_before: {matching_paths_before}")
        logger.debug(f"matching_paths_after: {matching_paths_after}")

        # 遍历matched_widgets，依次检查每个列表中的QGroupBox的标题
        for widget in matched_widgets:
            # 获取每个QListWidget的父对象QGroupBox
            parent_of_widget = widget.parent()

            # 打印每个父对象QGroupBox的标题
            if parent_of_widget and isinstance(parent_of_widget, QGroupBox):  # 确保父对象存在并且是QGroupBox
                groupbox_title = parent_of_widget.title()
                logger.debug(f"QGroupBox的标题: {groupbox_title}")

                # 提取出 选择第{n}级节点 中的数字
                widget_level = int(re.findall(r'\d+', groupbox_title)[0])

                # 记录标签的当前状态
                logger.debug(
                    f"QListWidget (层级 {widget_level}) 内容: {[item.text() for item in widget.findItems('*', Qt.MatchWildcard)]}")

                # 判断是在当前层级还是在后面的层级
                if widget_level == this_level:
                    # 如果是当前层级，首先隐藏所有的条目
                    for i in range(widget.count()):
                        widget.item(i).setHidden(True)

                    # 然后显示与 matching_paths_before 匹配的条目
                    for path in matching_paths_before:
                        display_value = path.split('/')[-1]
                        items = widget.findItems(display_value, Qt.MatchExactly)
                        for item in items:
                            item.setHidden(False)

                elif widget_level > this_level:
                    # 如果是后面的层级，根据层级深度更新列表的内容
                    paths_for_this_widget = [path for path in matching_paths_after if
                                             len(path.split('/')) == widget_level]
                    display_values = [path.split('/')[-1] for path in paths_for_this_widget]
                    for i in range(widget.count()):
                        if widget.item(i).text() not in display_values:
                            widget.item(i).setHidden(True)
                        else:
                            widget.item(i).setHidden(False)
            else:
                logger.debugtest(f"QListWidget的父对象不是QGroupBox或不存在")

        # 查找self.all_list_layout的父对象下的所有QLabel，并将其更新为所选的stored_value，但排除文本格式为 "选择第n级节点" 的标签
        parent_of_all_list_layout = self.all_list_layout.parentWidget()  # 注意这里使用parentWidget()方法

        if parent_of_all_list_layout and isinstance(parent_of_all_list_layout, (QWidget, QLayout)):
            # 使用find_items_in_layout_recursive函数查找所有的QLabel部件
            all_labels = find_items_in_layout_recursive(parent_of_all_list_layout.layout(), QLabel)
            for label in all_labels:
                logger.debug(f"正在检查标签: {label.text()}")
                if isinstance(label, QLabel):  # 确保找到的对象确实是QLabel的实例
                    logger.debug(f"找到的QLabel: {label.text()}")
                    # 检查标签的文本是否符合 "选择第n级节点" 的格式
                    if not re.match(r"选择第\d+级节点", label.text()):
                        logger.debug(f"更新标签: {label.text()} 为: {stored_value}")
                        label.setText(stored_value)
        else:
            logger.warning("self.all_list_layout没有父对象或其父对象不是QWidget或QLayout的实例")

    def update_list_widget_max_width(self, list_widget):
        """
        更新QListWidget的最大宽度
        :param list_widget:
        :return:
        """
        logger.info("开始更新 QListWidget 的最大宽度")

        # 获取QListWidget的字体度量
        font_metrics = list_widget.fontMetrics()
        logger.debug(f"获取的字体度量为: {font_metrics}")

        # 初始化最大宽度为0
        max_width = 0

        # 遍历每个条目
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            width = font_metrics.horizontalAdvance(item.text())
            # width = font_metrics.width(item.text()) # 弃用的方法
            if width > max_width:
                max_width = width
                logger.debug(f"新的最大宽度为: {max_width}, 来自条目: {item.text()}")

        # 设置QListWidget的最大宽度。你可能还希望添加一些额外的宽度作为缓冲。
        padding = 50  # 例如，增加10像素的缓冲
        list_widget.setMaximumWidth(max_width + padding)
        logger.info(f"QListWidget 的最大宽度设置为: {max_width + padding}")

    def filter_list_widget(self, list_widget, search_text):
        """
        过滤QListWidget中的条目，根据给定的搜索文本
        """
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setHidden(search_text not in item.text())


# 创建应用实例
app = QtWidgets.QApplication([])

# 创建 ModEditor 对象
editor = ModEditor()
editor.show()

# 进入应用的主循环
app.exec_()
