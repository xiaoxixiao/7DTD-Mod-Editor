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
        self.main_layout = QVBoxLayout()  # 创建主窗口的主部件的主布局为垂直布局
        self.main_widget.setLayout(self.main_layout)  # 设置主窗口的布局为垂直布局

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
        self.refresh_button = QPushButton("刷新")
        self.select_file_button = QPushButton("选择文件")
        self.h_layout.addWidget(self.refresh_button)
        self.h_layout.addWidget(self.select_file_button)
        # 绑定按钮的点击事件
        self.select_file_button.clicked.connect(self.select_file_event)
        self.refresh_button.clicked.connect(self.refresh_event)
        # 按钮下添加一个标签
        self.label_text = QLabel()
        self.h_layout.addWidget(self.label_text)
        # 设置标签的文本
        self.label_text.setText("文件路径：")

        # 在横向布局下面创建一个纵向布局
        self.v_layout = QVBoxLayout()
        # 添加一个树
        self.tree = QTreeView()
        self.tree.setStyleSheet("background-color: #454545;")
        self.v_layout.addWidget(self.tree)
        # 项目的点击事件
        self.tree.clicked.connect(self.tree_item_clicked)

        # 创建一个纵向布局，将横向布局和纵向布局添加到里面
        self.vertical_left_xpath_selector = QVBoxLayout()
        self.vertical_left_xpath_selector.addLayout(self.h_layout)
        self.vertical_left_xpath_selector.addLayout(self.v_layout)

        # 创建一个标签
        self.Label_Text_Code_Editing_Area = QLabel()
        self.Label_Text_Code_Editing_Area.setText("xpath路径：")
        self.Label_text_2_code_editing_area = QLabel()
        self.Label_text_2_code_editing_area.setText(
            "选择你的Xpath编辑模版（点击一下会用上面的xpath路径作为模板添加进去：")
        # 创建一个横向布局的按钮组
        self.Horizontal_code_editing_area_button_group = QHBoxLayout()
        self.xpath_set_template_button = QPushButton("set")
        self.xpath_append_module_button = QPushButton("append")
        self.xpath_remove_module_button = QPushButton("remove")
        self.Horizontal_code_editing_area_button_group.addWidget(self.xpath_set_template_button)
        self.Horizontal_code_editing_area_button_group.addWidget(self.xpath_append_module_button)
        self.Horizontal_code_editing_area_button_group.addWidget(self.xpath_remove_module_button)
        self.xpath_set_template_button.clicked.connect(self.set_xpath_set模板)
        self.xpath_append_module_button.clicked.connect(self.set_xpath_append模块)
        self.xpath_remove_module_button.clicked.connect(self.set_xpath_remove模块)
        # 创建一个文本编辑框
        self.text_edit_box_code_edit_area = QTextEdit()
        self.text_edit_box_code_edit_area.setStyleSheet("background-color: #454545; color: #ffffff;")

        # 创建一个纵向布局
        self.vertical_code_editing_area = QVBoxLayout()
        self.vertical_code_editing_area.addWidget(self.Label_Text_Code_Editing_Area)
        self.vertical_code_editing_area.addWidget(self.Label_text_2_code_editing_area)
        self.vertical_code_editing_area.addLayout(self.Horizontal_code_editing_area_button_group)
        self.vertical_code_editing_area.addWidget(self.text_edit_box_code_edit_area)

        # 创建一个分割器
        self.splitter = QSplitter(Qt.Horizontal)  # 创建一个分割器，并设置为水平分割
        self.left_part = QWidget()
        self.right_part = QWidget()
        self.left_part.setLayout(self.vertical_left_xpath_selector)
        self.right_part.setLayout(self.vertical_code_editing_area)
        self.splitter.addWidget(self.left_part)
        self.splitter.addWidget(self.right_part)

        # 创建一个标签
        self.bottom_label = QLabel()
        self.bottom_label.setText("本软件由 泉户 黑崎 开发，仅供学习交流使用，不得用于商业用途！联系方式：QQ：1624910218")
        # 设置内外边距
        self.bottom_label.setContentsMargins(10, 10, 10, 10)

        # 将分割器添加到主布局中
        self.main_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.bottom_label)
        self.main_layout.setStretch(0, 1)  # 设置分割器的伸缩因子为1
        self.main_layout.setStretch(1, 0)  # 设置底部标签的伸缩因子为0

    def tree_item_clicked(self, index):
        logger.debug("检测到点击事件")
        # 获取点击的项目
        item = self.tree.model().itemFromIndex(index)
        # 获取项目的文本
        text = item.text()
        # ========== #
        # 递归获取父项目的文本
        parent_item_text_list: list = []
        i = -1

        def get_parent_item_text(item, i) -> list:
            if item.parent() is not None:
                parent_item_text_list.append({i: item.text()})
                i -= 1
                return get_parent_item_text(item.parent(), i)
            if item.parent() is None:
                parent_item_text_list.append({i: item.text()})
                logger.debug(f"父项目文本列表：{parent_item_text_list}")
                return parent_item_text_list

        # ========== #
        parent_item_text_list = get_parent_item_text(item, i)

        # ========== #
        def handle_the_parent_item_text_list(parent_item_text_list):
            spliced_list = []

            def extract_information(target):
                tag = attribute = value = ""
                if "[@" in target:
                    match_the_object = re.search(r'(.*?)\[@(.*?)\](?:=(.*))?', target)
                    if match_the_object:
                        tag, attribute, value = match_the_object.groups()
                elif "|" in target:
                    tag, after_part = [part.strip() for part in target.split("|")]
                    after_part = after_part.replace("...", "").strip()
                    if "=" in after_part:
                        attribute, value = [part.strip() for part in after_part.split("=")]
                elif "=" not in target:
                    tag = target.strip()
                return tag, attribute, value

            if len(parent_item_text_list) > 1:
                target1 = list(parent_item_text_list[0].values())[0]
                target2 = list(parent_item_text_list[1].values())[0]
                tag1, attribute_1, value_1 = extract_information(target1)
                tag2, attribute_2, value_2 = extract_information(target2)

                if tag1 == tag2 and attribute_1 == attribute_2 and value_1 == value_2:
                    spliced_list.append(f'{tag1}[@{attribute_1}]')
                elif tag1 == tag2:
                    spliced_list.append(f'{tag1}[@{attribute_1}]')
                else:
                    spliced_list.append(f'{tag1}[@{attribute_1}={value_1}]')
                    spliced_list.append(f'{tag2}[@{attribute_2}={value_2}]')

                for item in parent_item_text_list[2:]:
                    target = list(item.values())[0]
                    tag, attribute, value = extract_information(target)
                    if tag and attribute:
                        spliced_list.append(f'{tag}[@{attribute}={value}]')
                    elif tag:
                        spliced_list.append(tag)

            else:
                for item in parent_item_text_list:
                    target = list(item.values())[0]
                    tag, attribute, value = extract_information(target)
                    if tag and attribute:
                        spliced_list.append(f'{tag}[@{attribute}={value}]')
                    elif tag:
                        spliced_list.append(tag)

            spliced_list.reverse()
            print(f"拼接列表：{spliced_list}")
            return spliced_list

        # ========== #
        stitch_list_elements_ = handle_the_parent_item_text_list(parent_item_text_list)

        # ========== #
        def stitch_list_elements(list_):
            the_path_name_has_no_suffix = self.file_path.replace('.xml', '').split('/')[-1]
            result = f'{the_path_name_has_no_suffix}/'
            for i in range(len(list_)):
                this_element = list_[i].strip()  # 删除空白字符
                result += this_element

                # 如果当前元素不是最后一个，且下一个元素不是[@xxx]形式，则添加/
                if i < len(list_) - 1 and not re.match(r'\[@.*?\]', list_[i + 1].strip()):
                    result += '/'
            logger.debug(f"拼接结果：{result}")
            return result

        # ========== #
        result = stitch_list_elements_(stitch_list_elements_)
        # 设置标签文本_代码编辑区的文本
        self.Label_Text_Code_Editing_Area.setText(f'xpath路径：{result}')

    def refresh_event(self):
        # 清空树控件
        self.tree_model.clear()
        # 清空标签文本
        self.label_text.setText("文件路径：")

    def select_file_event(self):
        # 弹出文件选择对话框
        self.file_path = ""
        self.file_path = QFileDialog.getOpenFileName(self, "选择文件", "./", "xml文件(*.xml)")[0]
        # 连接标签文本更新槽函数
        self.label_text.setText("文件路径：" + self.file_path)
        # 解析xml文件
        root = self.parsing_xml_files()

        self.create_a_standard_item_model_settings_tree_control(root)

    def parsing_xml_files(self):
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
                    event.acceptProposedAction()  # 接受拖入文件

    def dropEvent(self, event: PySide6.QtGui.QDropEvent) -> None:
        logger.debug("放下文件")
        # 判断拖入的文件是否是xml文件
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.fileName().endswith(".xml"):
                    self.file_path = url.toLocalFile()
                    # 连接标签文本更新槽函数
                    self.label_text.setText("文件路径：" + self.file_path)
                    # 解析xml文件
                    root = self.root_load = self.parsing_xml_files()
                    logger.debug("放下事件完成")
                    self.create_a_standard_item_model_settings_tree_control(root)

    def Load_xml_into_the_tree(self, xml_node, tree_node):
        for child_nodes in xml_node:
            # 获取第一个属性的描述
            the_first_property_description = ""
            a_list_of_properties = list(child_nodes.attrib.items())  # 将属性转换为列表
            if a_list_of_properties:
                the_first_property, value = a_list_of_properties[0]
                the_first_property_description = f" | {the_first_property}={value}"
                if len(a_list_of_properties) > 1:
                    the_first_property_description += "  ..."

            # 创建树中的节点
            subtree_nodes = QStandardItem(child_nodes.tag + the_first_property_description)
            # 设置字体颜色为亮灰色
            subtree_nodes.setForeground(QBrush(Qt.white))
            tree_node.appendRow(subtree_nodes)

            # 如果节点有内容，添加内容节点
            if child_nodes.text and child_nodes.text.strip():
                content_nodes = QStandardItem(child_nodes.text.strip())
                # 设置字体颜色为亮灰色
                content_nodes.setForeground(QBrush(Qt.white))
                subtree_nodes.appendRow(content_nodes)

            # 如果有属性，创建属性子树
            if child_nodes.attrib:
                # 属性子树节点 = QStandardItem(f'{子节点.tag}[@属性]')
                # 属性子树节点.setForeground(QBrush(Qt.white))
                # 子树节点.appendRow(属性子树节点)
                for attribute, value in child_nodes.attrib.items():
                    properties_node = QStandardItem(f'{child_nodes.tag}[@{attribute}]={value}')
                    properties_node.setForeground(QBrush(Qt.white))
                    subtree_nodes.appendRow(properties_node)

            # 递归调用
            self.Load_xml_into_the_tree(child_nodes, subtree_nodes)

    def create_a_standard_item_model_settings_tree_control(self, root):
        # 创建一个标准项模型
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['XML结构'])  # 设置表头
        # 添加root节点到模型
        root_node = self.tree_model.invisibleRootItem()
        self.Load_xml_into_the_tree(root, root_node)
        # 设置树控件的模型
        self.tree.setModel(self.tree_model)
        logger.info("解析xml文件成功")

    def set_xpath_set模板(self):
        xpath_path = self.Label_Text_Code_Editing_Area.text().split("：")[-1]
        template_set = f"""<config>
    <set xpath="{xpath_path}"></set>
</config>
        """
        if xpath_path:
            self.text_edit_box_code_edit_area.append(template_set)
        else:
            self.text_edit_box_code_edit_area.append("请先选择好xpath路径")

    def set_xpath_append模块(self):
        xpath_path = self.Label_Text_Code_Editing_Area.text().split("：")[-1]
        template_append = f"""<config>
    <append xpath="{xpath_path}"></append>
</config>
        """
        if xpath_path:
            self.text_edit_box_code_edit_area.append(template_append)
        else:
            self.text_edit_box_code_edit_area.append("请先选择好xpath路径")

    def set_xpath_remove模块(self):
        xpath_path = self.Label_Text_Code_Editing_Area.text().split("：")[-1]
        template_remove = f"""<config>
    <remove xpath="{xpath_path}"></remove>
</config>
        """
        if xpath_path:
            self.text_edit_box_code_edit_area.append(template_remove)
        else:
            self.text_edit_box_code_edit_area.append("请先选择好xpath路径")


if __name__ == "__main__":
    app = QApplication([])
    window = XPathSelector()
    window.show()
    app.exec()
