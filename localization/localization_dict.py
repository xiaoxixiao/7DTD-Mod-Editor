localization_dict = {
    "item": "物品",
    "name": "名称",
    "description": "描述",
}


def localization_func(tag):
    return localization_dict.get(tag, tag)


def inverse_localization_func(localized_tag):
    inverse_dict = {v: k for k, v in localization_dict.items()}
    return inverse_dict.get(localized_tag, localized_tag)
