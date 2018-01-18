import datetime
from app import db
from app.models.base.base import BaseModel


class AppVersionModel(db.Model, BaseModel):
    __bind_key__ = "a_core"
    __tablename__ = "app_version"

    # 调用to_dict()时，只处理次数组中的字段
    __fillable__ = ["device_type", "version", "url"]

    id = db.Column(db.Integer, primary_key=True)

    device_type = db.Column(db.String(20), default="")
    version = db.Column(db.String(15), default="")
    version2long = db.Column(db.Integer, default=0)
    hash = db.Column(db.String(32), default="")
    url = db.Column(db.String(100), default="")

    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @staticmethod
    def query_last_app_version_by_device_type(device_type=""):
        # 查询条件
        query = AppVersionModel.query.filter_by(device_type=device_type, status=1)
        # 排序
        query = query.order_by(db.desc(AppVersionModel.version2long))
        # 查询
        return query.first()
