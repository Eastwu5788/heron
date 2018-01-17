from flask import g
from .base_middleware import BaseMiddleWare


class DBMiddleWare(BaseMiddleWare):

    @staticmethod
    def before_request():
        # g.db = connect_db()
        pass

    @staticmethod
    def teardown_request(exception):
        # db = getattr(g, 'db', None)
        # if db is not None:
        #    db.close()
        pass
