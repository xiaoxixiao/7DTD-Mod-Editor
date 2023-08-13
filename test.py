import xml.etree.ElementTree as ET
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_xml(input_data):
    try:
        root = ET.fromstring(input_data)
        return root
    except ET.ParseError:
        try:
            tree = ET.parse(input_data)
            root = tree.getroot()
            return root
        except ET.ParseError as e:
            logger.error(f'解析XML时出错: {e}')
            return None

    result = {}

    def traverse_tree(node, level):
        if level not in result:
            result[level] = {'节点': [], '属性': []}

        # 存储节点名称
        result[level]['节点'].append(node.tag)

        # 将属性存储为字典
        attributes_dict = {attr: value for attr, value in node.attrib.items()}
        result[level]['属性'].append(attributes_dict)

        for child in node:
            traverse_tree(child, level + 1)

    traverse_tree(root, 0)
    logger.info('XML解析成功')
    return result


def find_paths_to_level(root, target_level, selected_node, selected_attribute_value):
    paths_with_attributes = []

    def traverse_tree(node, current_level, current_path, current_attributes):
        # 如果到达目标层级，将当前路径和属性添加到结果中
        if current_level == target_level:
            current_attributes.append({attr_key: attr_value for attr_key, attr_value in node.attrib.items()})
            path_str = '/'.join(current_path)
            attr_key, attr_value = selected_attribute_value.split('=')
            if selected_node in path_str and any(attr.get(attr_key) == attr_value for attr in current_attributes):
                paths_with_attributes.append((path_str, current_attributes.copy()))
            current_attributes.pop()

        # 递归遍历子节点
        for child in node:
            current_path.append(child.tag)
            current_attributes.append({attr_key: attr_value for attr_key, attr_value in child.attrib.items()})
            traverse_tree(child, current_level + 1, current_path, current_attributes)
            current_path.pop()
            current_attributes.pop()

    traverse_tree(root, 0, [root.tag], [])
    return paths_with_attributes


if __name__ == "__main__":

    xml_path = r"D:\.game\steam\steamapps\common\7 Days To Die\Data\Config\items.xml"

    root = parse_xml(xml_path)
    selection = {
        '所选层': 2,
        '所选节点': 'property',
        '所选属性值': 'name=Tags'
    }

    paths_to_level = find_paths_to_level(root, selection['所选层'], selection['所选节点'], selection['所选属性值'])
    for path, attributes in paths_to_level:
        print(f"路径: {path}")
        print(f"属性: {attributes}")
