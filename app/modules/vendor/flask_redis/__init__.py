"""
Redis的Flask扩展
"""
import sys
import pickle
from flask import current_app

PY2 = sys.version_info[0] == 2

if PY2:
    integer_types = (int, long)
else:
    integer_types = (int, )

try:
    from redis import Redis
    from redis import from_url as redis_from_url
except ImportError:
    pass
else:
    def redis(app, config, kwargs):
        kwargs.update(dict(
            host=config.get("CACHE_REDIS_HOST", "localhost"),
            port=config.get("CACHE_REDIS_PORT", 6379),
        ))
        password = config.get("CACHE_REDIS_PASSWORD")
        if password:
            kwargs["password"] = password

        db_number = config.get("CACHE_REDIS_DB")
        if db_number:
            kwargs["db"] = db_number

        redis_url = config.get("CACHE_REDIS_URL")
        if redis_url:
            kwargs["host"] = redis_from_url(redis_url,
                                            db=kwargs.pop('db', None)
                                            )
        return Redis(**kwargs)


class FlaskRedis(object):

    def __init__(self, app=None, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")

        self.config = config
        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an install of dict or None")

        base_config = app.config.copy()
        if self.config:
            base_config.update(self.config)
        if config:
            base_config.update(config)
        config = base_config

        config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        config.setdefault('CACHE_THRESHOLD', 500)
        config.setdefault('CACHE_KEY_PREFIX', 'flask_cache_')
        config.setdefault('CACHE_OPTIONS', [])

        self._set_redis_cache(app, config)

    def _set_redis_cache(self, app, config):
        cache_obj = redis

        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions.setdefault('redis_cache', {})
        app.extensions['redis_cache'][self] = cache_obj(app, config, dict())
        self.config = config

    @property
    def cache(self):
        app = self.app or current_app
        return app.extensions['redis_cache'][self]

    @property
    def prefix(self):
        return self.config.get("CACHE_KEY_PREFIX", 'flask_cache_')

    @property
    def default_timeout(self):
        return self.config.get("CACHE_DEFAULT_TIMEOUT")

    def _normalize_timeout(self, timeout):
        if timeout is None:
            timeout = self.default_timeout
        if timeout == 0:
            timeout = -1
        return timeout

    def dump_object(self, value):
        t = type(value)
        if t in integer_types:
            return str(value).encode("ascii")
        return b'!' + pickle.dumps(value)

    def load_object(self, value):
        if value is None:
            return None

        if value.startswith(b"!"):
            try:
                return pickle.loads(value[1:])
            except pickle.PickleError:
                return None

        try:
            return int(value)
        except ValueError:
            return value

    def get(self, key):
        return self.load_object(self.cache.get(self.prefix + key))

    def set(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)

        if timeout == -1:
            result = self.cache.set(name=self.prefix + key, value=dump)
        else:
            result = self.cache.set(name=self.prefix + key, value=dump, timeout=timeout)

        return result

    def inc(self, key, delta=1):
        return self.cache.incr(name=self.prefix + key, amount=delta)

    def dec(self, key, delta=1):
        return self.cache.decr(name=self.prefix + key, amount=delta)

    def smembers(self, key):
        self.cache.smembers(name=self.prefix + key)

    def srandmember(self, key, number=None):
        return self.cache.srandmember(name=self.prefix + key, number=number)

    def sadd(self, key, *values):
        self.cache.sadd(self.prefix + key, *values)

    def delete(self, *keys):
        self.cache.delete(*keys)
