import platform
import tornado.ioloop
import tornado.web

from tornado_swagger.setup import setup_swagger
from tornado.httpserver import HTTPServer
from tornado.netutil import bind_sockets
from tornado.ioloop import IOLoop
from importlib import import_module

from qnado import settings
from qnado.handlers.base.base_handler import PageNotFoundHandler, BaseHandler
from qnado.common.errors import ApiException
from qnado.common.log_util import get_logger
from qnado.common import enums
from qnado.baseapi import user_api

logger = get_logger(__name__)


def get_url_mapping():
    url_mapping = []
    readable_router = {}
    for handler in settings.ENABLED_HANDLER_LIST:
        module = import_module(settings.HANDLER_PATH.format(handler_module=handler))
        for item in module.__dict__.values():
            if isinstance(item, type) and issubclass(item, BaseHandler) \
                                      and item.__module__ == module.__name__:
                url_mapping.append(tornado.web.url(item.pattern, item))
                readable_router.update({enums.SERVER_HANDLERS[handler]: item.pattern})
    return url_mapping, readable_router


class Application(tornado.web.Application):
    def __init__(self):
        url_mapping, readable_router = get_url_mapping()
        self.readable_router = readable_router
        setup_swagger(url_mapping,
                      swagger_url=settings.SWAGGER_URL,
                      api_base_url='/',
                      description=user_api.__doc__,
                      api_version=settings.QNADO_VERSION,
                      title='Qnado TASK API')
        super().__init__(url_mapping, **settings.settings)


def run_server():
    application = Application()
    tornado.web.ErrorHandler = PageNotFoundHandler
    server = HTTPServer(application, xheaders=True)
    if platform.system() == 'Windows':
        raise ApiException('Qnado does not support Windows.')
    else:
        sockets = bind_sockets(settings.SITE_PORT)
        server.add_sockets(sockets)
        server.start(settings.SITE_NUMBER_OF_PROCESSES)

    logger.info('Tornado server started on port %s.' % settings.SITE_PORT)

    # 输出当前的路由表
    for k,v in application.readable_router.items():
        logger.info(f'URL of {k}: http://127.0.0.1:{settings.SITE_PORT}{v}')

    # 输出 swagger-ui 的地址
    logger.info(f'URL of swagger-ui: http://127.0.0.1:{settings.SITE_PORT}{settings.SWAGGER_URL}')

    IOLoop.current().start()
