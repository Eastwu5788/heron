"""
heron 项目配置文件
"""
from config.develop.develop_config import DevelopConfig
from config.product.product_config import ProductConfig

from app.middleware.auth_middleware import AuthMiddleWare
from app.middleware.secret_middleware import SecretMiddleWare

# App 秘钥
SECRET_KEY = 'p*ggd=o#y8ws1fspup!jnw9m0mo=4+fs1a!l!eu%h&b=jfx$x#'

MIDDLEWARE = [
    SecretMiddleWare,
    AuthMiddleWare,
]

# 请求是否进行安全检查
REQUEST_SECRET_CHECK = True

# 请求白名单
WHITE_LIST = [
   "/build/initialize/index",
]

# load config file with 'dev' or 'pro'
config = {
    'dev': DevelopConfig,
    'pro': ProductConfig,
}
