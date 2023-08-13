import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import xml.etree.ElementTree as ET

class ModEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("七日杀 Mod 编辑器")

        # 创建一个PanedWindow，这样我们可以在左侧放置列表框，在右侧放置文本编辑器
        self.paned_window = tk.PanedWindow(root)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 创建一个菜单栏
        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        # 在菜单栏中添加一个“文件”菜单
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="文件", menu=self.file_menu)

        # 在“文件”菜单中添加一个“导入”菜单项
        self.file_menu.add_command(label="导入", command=self.open_file)

        # 创建一个列表框用于显示所有的物品名称，宽度暂时设置为1
        self.item_listbox = tk.Listbox(self.paned_window, width=1)
        self.paned_window.add(self.item_listbox)

        # 绑定列表框的选择事件，当用户在列表框中选择一个物品时调用self.show_item_xml方法
        self.item_listbox.bind("<<ListboxSelect>>", self.show_item_xml)

        # 创建一个搜索框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(root, textvariable=self.search_var)
        self.search_entry.pack()

        # 绑定搜索框的变化事件，当搜索框的内容改变时调用self.search_items方法
        self.search_var.trace_add("write", self.search_items)

        # 创建一个文本编辑器，放置在PanedWindow的右侧
        self.text_editor = scrolledtext.ScrolledText(self.paned_window)
        self.paned_window.add(self.text_editor)

        # 定义一个列表来存储所有的物品名称
        self.items = []

        # 定义一个字典来存储每个物品的XML
        self.item_xmls = {}

    def open_file(self):
        # 打开一个文件选择对话框，让用户选择要打开的文件
        filename = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])

        # 如果用户选择了一个文件
        if filename:
            # 解析选中的XML文件
            tree = ET.parse(filename)
            root = tree.getroot()

            # 清空物品名称列表和物品XML字典
            self.items.clear()
            self.item_xmls.clear()

            # 将XML文件中的所有物品名称添加到物品名称列表中，并将物品的XML添加到物品XML字典中
            for item in root.findall(".//item"):
                name = item.get('name')
                if name:
                    self.items.append(name)
                    self.item_xmls[name] = ET.tostring(item, encoding='unicode')

            # 更新列表框
            self.update_listbox()

    def search_items(self, *args):
        # 获取搜索框中的文本
        search_text = self.search_var.get()

        # 清空列表框
        self.item_listbox.delete(0, tk.END)

        # 添加所有包含搜索文本的物品名称到列表框中
        for item in self.items:
            if search_text.lower() in item.lower():
                self.item_listbox.insert(tk.END, item)

    def show_item_xml(self, event):
        # 获取选中的物品名称
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            item_name = event.widget.get(index)

            # 获取物品的XML
            item_xml = self.item_xmls.get(item_name, "")

            # 显示物品的XML在文本编辑器中
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, item_xml)

    def update_listbox(self):
        # 清空列表框
        self.item_listbox.delete(0, tk.END)

        # 添加所有物品名称到列表框中
        for item in self.items:
            self.item_listbox.insert(tk.END, item)

        # 计算最长的物品名称，并更新列表框的宽度
        max_width = max(len(item) for item in self.items)
        self.item_listbox.config(width=max_width)

root = tk.Tk()
app = ModEditor(root)
root.mainloop()
