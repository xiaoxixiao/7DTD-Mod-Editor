## 文件结构
- mod_editor.py：主程序文件，包含了 ModEditor 类和程序的入口点。

## 主要类和函数
### ModEditor 类
- ModEditor 类继承自 QMainWindow，是程序的主类，包含了程序的所有逻辑。

#### 属性
- item_listbox：一个 QListWidget，用于显示所有的物品名称。
- text_editor：一个 QTextEdit，用于显示和编辑物品的 XML。
- search_entry：一个 QLineEdit，用于输入搜索文本。
- indent_label、indent_input、indent_button：用于设置文本编辑器的缩进宽度。
- show_button、hide_button：用于显示和隐藏设置部分。
- items：一个 list，存储所有的物品名称。
- item_xmls：一个 dict，存储每个物品的 XML。
- indent_widget：一个部件，包含了设置缩进宽度的相关组件。
- file_path：一个字符串，存储当前加载的文件路径。在加载新文件之前会被清空。

#### 方法
- __init__：初始化方法，设置窗口标题，创建所有的组件和布局，绑定事件。
- show_settings：显示设置部分。
- hide_settings：隐藏设置部分。
- set_tab_width：设置文本编辑器的缩进宽度。
- dragEnterEvent、dropEvent：重载这两个方法，使程序支持文件拖放。
- load_file(filename)：创建一个新的方法来加载文件。它会解析选中的 XML 文件，并将所有物品名称添加到物品名称列表中，将物品的 XML 添加到物品 XML 字典中。如果在解析时出现错误，会显示一个错误对话框。
- open_file()：此方法会在用户点击“导入”菜单项时被调用。它会打开一个文件选择对话框，让用户选择要打开的文件，并调用 load_file 来加载所选文件。
- search_items()：此方法会在搜索框的内容改变时被调用。它会获取搜索框中的文本，并添加所有包含搜索文本的物品名称到列表框中。
- show_item_xml()：此方法会在用户在列表框中选择一个物品时被调用。它会获取选中的物品名称，获取物品的 XML，然后在文本编辑器和树状图中显示物品的 XML。
- update_listbox()：此方法用来更新列表框中的内容。它会清空列表框，并添加所有物品名称到列表框中。
- select_tree_item：当用户点击选择按钮时，此方法会被调用，它会获取当前选择的树节点，并弹出一个对话框显示节点的完整路径。
- get_full_node_path：此方法获取节点的完整路径，参数 index 是要查询的节点的索引。
- tree_item_clicked：此方法记录用户点击树状图中的一个节点，并通过日志记录选中的节点。

### xml_to_tree 函数
这个函数接受两个参数：一个 QStandardItem 和一个 xml.etree.ElementTree.Element。它会将 XML 元素转换为树节点，然后添加到 QStandardItem 中。

## 使用的库
- PyQt5：用于创建 GUI。
- xml.etree.ElementTree：用于解析 XML。

## 软件依赖
- Python 3
- PyQt5
- xml.etree.ElementTree

## 程序执行部分
- 创建应用实例。
- 创建 ModEditor 对象并显示。
- 进入应用的主循环。
