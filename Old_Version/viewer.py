def show_item_xml(self):
    """
    显示物品的XML内容：当用户在列表框中选择一个物品时，本方法用于显示所选物品的XML内容。

    1. 记录开始显示选中物品的XML内容。
    2. 获取选中的物品名称，以便我们可以查找相应的XML。
    3. 从字典中获取物品的XML。如果没有找到，将记录一条警告并返回。
    4. 在文本编辑器中显示物品的XML，使用户可以查看和编辑。
    5. 将物品的XML显示在树状图中，以可视化方式呈现XML结构。
    """

    logger.info("开始显示选中的物品的XML内容")

    # 获取选中的物品名称
    item_name = self.item_listbox.currentItem().text().strip()
    logger.debug("选中的物品名称为: %s", item_name)

    # 从字典中获取物品的XML
    item_xml = self.item_xmls.get(item_name, "")

    # 如果没有找到XML，记录警告并返回
    if not item_xml:
        logger.warning("未找到 %s 的 XML 内容", item_name)
        return

    # 在文本编辑器中显示物品的XML，使用户可以查看和编辑
    self.text_editor.setText(item_xml)
    logger.debug("物品的XML已加载到文本编辑器中")

    # 将物品的XML显示在树状图中，以可视化方式呈现XML结构
    self.tree_model.clear()
    root = ET.fromstring(item_xml)
    xml_to_tree(self.tree_model.invisibleRootItem(), root)
    logger.info("%s 的 XML 已加载到树状图中", item_name)



