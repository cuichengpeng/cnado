# 配置文件

import os
import socket

from qnado.common.env_util import env
from qnado.common.utils import get_dir_path
from qnado.common import enums

DEBUG = False

QNADO_VERSION = '0.2.2'
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

SITE_ROOT = os.getcwd()
SITE_PORT = env.int('SITE_PORT', 5000)
SITE_NUMBER_OF_PROCESSES = 1

# DB_URL
DB_URL = env.str('DB_URL', 'mongodb://quantum:123456@192.168.20.61:27017')
DB_NAME = env.str('DB_NAME', 'db_qnado')

# REDIS
REDIS_HOST = env.str('REDIS_HOST', '192.168.20.61')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_PASSWORD = env.str('REDIS_PASSWORD', '123')
REDIS_DB = env.int('REDIS_DB', 8)

# 目录
TEMPLATE_PATH = os.path.join(PACKAGE_ROOT, 'templates')
MOUNT_DIR_PATH = env.str('MOUNT_DIR_PATH', get_dir_path(SITE_ROOT, 'mount'))
RESULT_DATA_PATH = get_dir_path(MOUNT_DIR_PATH, 'result_data')

# 日志
LOG_PATH = env.str('LOG_PATH', get_dir_path(SITE_ROOT, 'logs'))
LOG_NAME = 'python-api.log'
LOG_LEVEL = 'INFO'  # DEBUG|INFO|WARNING|ERROR|NONE
LOG_FILE_SIZE = 1024 * 1024 * 50
LOG_FILE_COUNT = 10
LOG_DATE_FORMAT = '%y%m%d %H:%M:%S'
LOG_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d pid=%(process)d tid=%(thread)d] %(message)s'  # 日志格式

#application
settings = dict(
    template_path=TEMPLATE_PATH,
    root_path=SITE_ROOT,
    xsrf_cookies=False,
    autoescape="xhtml_escape",
    debug=DEBUG,
    xheaders=True,
)

# celery config
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', 'redis://:123@192.168.20.61:6379/3')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', 'redis://:123@192.168.20.61:6379/6')
CELERYD_CONCURRENCY = env.int('CELERYD_CONCURRENCY', 4)
CELERY_WAIT_TIMEOUT = 5     # 超过这个时间则判定 celery 启动失败
CELERY_NAME_MODE = env.str('CELERY_NAME_MODE', enums.CELERY_NAME_MODE_HOSTNAME)

# OSS 文件路径模板
OSS_CONFIG = {
    'ACCESS_KEY': env.str('ACCESS_KEY', 'uuMckKEGa2pQwWDh'),
    'SECRET_KEY': env.str('SECRET_KEY', 'cx6qKx9I5e3AW9gZvhfU3UZ4Vg9tZ1r3'),
    'BUCKET': env.str('BUCKET', 'qnado-app'),
    'END_POINT': env.str('END_POINT', '192.168.20.70:9000'),
    'SECURE': env.bool('SECURE', False)
}

DEMO_API_FILE = 'simple_demo.py'
HOST_NAME = socket.gethostname()

# 配置 user_api 模块的路径
USER_MODULE_PATH = env.str('USER_MODULE_PATH', '')

# 配置实际需要使用到的 handler，对应的文件应放置再 qnado/handlers/ 目录下，使用模块名
HANDLER_PATH = 'qnado.handlers.{handler_module}'
ENABLED_HANDLER_LIST = [
    enums.SERVER_TASK_HANDLER,
    enums.SERVER_WEB_TASK_HANDLER
]

# 在此处注册异步任务
ASYNC_TASKS = {
    'main_task': {'module': 'qnado.tasks', 'func': 'main_task'},    # 会在 task_handler 中调用
}

# 配置 swagger-ui 的地址
SWAGGER_URL = '/qnado/api/doc'
