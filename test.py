import xml.etree.ElementTree as ET
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_xml(input_data):
    """
    解析给定的XML文件路径或XML字符串，并遍历每一层的节点和属性。

    参数:
        input_data (str): 要解析的XML文件路径或XML字符串。

    返回:
        dict: 字典，其键是整数，表示层数（从0开始），值是包含以下键的字典：
              - '节点': 包含该层所有节点名称的列表。
              - '属性': 包含该层所有节点属性的列表。每个元素是由属性名称和属性值组成的键值对列表。
    """

    def traverse_tree(node, level):
        if level not in result:
            result[level] = {'节点': [], '属性': []}

        # 存储节点名称和属性
        result[level]['节点'].append(node.tag)
        result[level]['属性'].append(list(node.attrib.items()))

        # 遍历子节点
        for child in node:
            traverse_tree(child, level + 1)

    try:
        # 尝试解析XML字符串
        root = ET.fromstring(input_data)
    except ET.ParseError:
        try:
            # 如果解析字符串失败，则尝试作为文件路径解析
            tree = ET.parse(input_data)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.error(f'解析XML时出错: {e}')
            return None

    result = {}

    # 递归函数，用于遍历XML

    traverse_tree(root, 0)
    logger.info('XML解析成功')
    return result


if __name__ == "__main__":
    xml_string = '''<root>
        <child1 attribute1="value1" attribute2="value2">text1</child1>
        <child2 attribute3="value3">text2</child2>
        <child3>
            <grandchild attribute4="value4">text3</grandchild>
        </child3>
    </root>'''

    parsed_xml = parse_xml(xml_string)
    if parsed_xml:
        for level, data in parsed_xml.items():
            print(f"层数: {level}, 节点: {data['节点']}, 属性: {data['属性']}")
    else:
        print('解析XML时出错')
