import json
import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta


class JsonEncoder(json.JSONEncoder):

    def default(self, obj):

        # 处理SQLAlchemy模型
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None

        # 处理datetime
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")

        # 其它默认处理
        return json.JSONEncoder.default(self, obj)