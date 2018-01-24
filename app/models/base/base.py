
class BaseModel(object):

    def to_dict(self, filter_params=False):
        """
        将模型转换成字典
        """
        result = {}

        for c in self.__table__.columns:

            # 过滤一些字段
            if filter_params and self.__fillable__ and c.name not in self.__fillable__:
                continue

            # 设置键值对
            result[c.name] = getattr(self, c.name, None)

        return result

    def format_model(self, attr_list=list()):
        result = dict()

        for attr in attr_list:
            if not attr:
                continue

            if not hasattr(self, attr):
                result[attr] = None
                continue

            result[attr] = getattr(self, attr, None)

        return result

