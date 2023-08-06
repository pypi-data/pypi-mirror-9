from pkgutil import extend_path
from podhub.meh import Meh
import pylibmc

__path__ = extend_path(__path__, __name__)


app = Meh(name=__name__, config={
    'MEMCACHED_HOST': '127.0.0.1',
    'URL_PARSE_TIMEOUT': 86400,  # 1 day
}).app

mc = pylibmc.Client([app.config.get('MEMCACHED_HOST', '127.0.0.1')],
                    binary=True,
                    behaviors={'tcp_nodelay': True, 'ketama': True})

from . import views
