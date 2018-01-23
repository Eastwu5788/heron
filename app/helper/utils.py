

def array_column(array=list(), column=""):
    """
    获取对象数组中的某一个属性构成的数组
    :param array: 原始对象数组
    :param column: 属性名称
    :return: 属性值构成的数组
    """
    if not array or not column:
        return list()

    result_list = []

    for item in array:
        value = None

        # 是一个字典
        if isinstance(item, dict):
            value = item.get(column, None)
        # 是一个对象
        elif isinstance(item, object):
            if not hasattr(item, column):
                continue
            value = getattr(item, column)

        if value:
            result_list.append(value)

    return result_list


def array_column_key(array=list(), column=""):
    """
    返回以column的值为key的字典，当key值相同时，后一个会覆盖前一个
    """
    if not array or not column:
        return dict()

    result_dict = dict()

    for obj in array:
        value = None

        if isinstance(obj, dict):
            print("dict", obj)
            value = obj.get(column, None)

        elif isinstance(obj, object):
            if not hasattr(obj, column):
                continue
            value = getattr(obj, column)

        if not value:
            continue

        result_dict[value] = obj

    return result_dict
