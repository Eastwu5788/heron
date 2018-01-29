"""
Redis的Flask扩展
"""
from flask import current_app

try:
    from werkzeug.contrib.cache import RedisCache
    from redis import from_url as redis_from_url
except ImportError:
    pass
else:
    def redis(app, config, args, kwargs):
        kwargs.update(dict(
            host=config.get("CACHE_REDIS_HOST", "localhost"),
            port=config.get("CACHE_REDIS_PORT", 6379),
        ))
        password = config.get("CACHE_REDIS_PASSWORD")
        if password:
            kwargs["password"] = password

        key_prefix = config.get("CACHE_KEY_PREFIX")
        if key_prefix:
            kwargs["key_prefix"] = key_prefix

        db_number = config.get("CACHE_REDIS_DB")
        if db_number:
            kwargs["db"] = db_number

        redis_url = config.get("CACHE_REDIS_URL")
        if redis_url:
            kwargs["host"] = redis_from_url(redis_url,
                                            db=kwargs.pop('db', None)
                                            )
        return RedisCache(*args, **kwargs)


class Redis(object):

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
        config.setdefault('CACHE_MEMCACHED_SERVERS', None)
        config.setdefault('CACHE_DIR', None)
        config.setdefault('CACHE_OPTIONS', None)
        config.setdefault('CACHE_ARGS', [])
        config.setdefault('CACHE_TYPE', 'null')
        config.setdefault('CACHE_NO_NULL_WARNING', False)

        self._set_redis_cache(app, config)

    def _set_redis_cache(self, app, config):
        cache_obj = redis

        cache_args = config["CACHE_ARGS"][:]
        cache_options = {"default_timeout": config["CACHE_DEFAULT_TIMEOUT"]}

        if config["CACHE_OPTIONS"]:
            cache_options.update(config["CACHE_OPTIONS"])

        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions.setdefault('redis_cache', {})
        app.extensions['redis_cache'][self] = cache_obj(app, config, cache_args, cache_options)

    @property
    def cache(self):
        app = self.app or current_app
        return app.extensions['redis_cache'][self]

    def get(self, *args, **kwargs):
        return self.cache.get(*args, **kwargs)

    def set(self, *args, **kwargs):
        self.cache.set(*args, **kwargs)

    def inc(self, *args, **kwargs):
        self.cache.inc(*args, **kwargs)

    def dec(self, *args, **kwargs):
        self.cache.dec(*args, **kwargs)
