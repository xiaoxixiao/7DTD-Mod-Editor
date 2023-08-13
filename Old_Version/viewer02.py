def xml_to_tree(parent, xml_element):
    """
    将给定的XML元素及其子元素转换为树节点，添加到给定的父节点中。

    :param parent: QStandardItem，父树节点，新的树节点将作为其子节点
    :param xml_element: Element，当前要转换的XML元素

    1. 从XML元素的标签创建新的树节点，并将其添加到父节点。
    2. 创建一个字典来存储节点的类型、标签和属性，然后将字典存储为节点的自定义数据。
    3. 遍历XML元素的属性，并为每个属性创建新的树节点，作为新节点的子节点。每个属性节点都存储一个包含类型、名称和值的字典。
    4. 递归地调用此函数来处理XML元素的子元素。

    通过此函数，整个XML结构将被转换为一个树状图，其中每个XML元素和属性都由树节点表示。
    """
    # Logging the call to xml_to_tree
    logger.debug(f"Called xml_to_tree with parent: {parent}, xml_element tag: {xml_element.tag}")

    # 使用标签创建新的树节点
    item_text = localization_func(xml_element.tag)  # 本地化标签
    item = QStandardItem(item_text)                 # 创建新的树节点

    # Logging the creation of a new tree node
    logger.debug(f"Created new tree node with text: {item_text}")

    # 创建一个字典来存储节点的相关信息
    node_data = {
        "type": "element",
        "tag": xml_element.tag,
        "attributes": xml_element.attrib
    }                                           # 创建一个字典来存储节点的相关信息

    # Logging the node data
    logger.debug(f"Node data: {node_data}")

    # 将字典作为节点的数据存储
    item.setData(node_data, QtCore.Qt.UserRole + 1)     # 将字典作为节点的数据存储
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