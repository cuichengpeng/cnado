import logging
import os
import socket

from qnado import settings
from concurrent_log_handler import ConcurrentRotatingFileHandler


LOGGING_MAPPING = {}

DEFAULT_FILE_SIZE = settings.LOG_FILE_SIZE  # 日志文件大小
DEFAULT_FILE_COUNT = settings.LOG_FILE_COUNT  # 日志文件数量
DEFAULT_DATE_FORMAT = settings.LOG_DATE_FORMAT  # 日志中日期格式
DEFAULT_FORMAT = settings.LOG_FORMAT  # 日志格式


class LazyLogger(object):
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        self._logger = None

    @property
    def debug(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.debug

    @property
    def info(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.info

    @property
    def warning(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.warning

    @property
    def warn(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.warn

    @property
    def error(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.error

    @property
    def exception(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.exception

    @property
    def critical(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.critical

    fatal = critical

    @property
    def log(self):
        logger = self._logger
        if not logger:
            logger = _get_logging(*self.__args, **self.__kwargs)
            self._logger = logger
        return logger.log


def _get_logging(name=None, file_name=None) -> logging.Logger:
    global LOGGING_MAPPING
    name = str(name) if name else 'default'
    file_name = str(file_name) if file_name else settings.LOG_NAME
    log_key = ('%s_%s' % (name, file_name)).replace('.', '_')
    if log_key not in LOGGING_MAPPING.keys():
        _generate_logger(name, file_name)
    return LOGGING_MAPPING.get(log_key)


def _generate_logger(name=None, file_name=None):
    global LOGGING_MAPPING
    log_name = file_name if file_name else settings.LOG_NAME
    log_name = logfile_name_add_hostname(log_name)
    log_file = os.path.join(settings.LOG_PATH, log_name)
    channel_handler = ConcurrentRotatingFileHandler(log_file, maxBytes=DEFAULT_FILE_SIZE, backupCount=DEFAULT_FILE_COUNT)
    channel_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT))

    logger = logging.getLogger(name if name else 'default')
    logger.addHandler(channel_handler)

    # 设置日志等级
    logger.setLevel(settings.LOG_LEVEL)

    LOGGING_MAPPING[('%s_%s' % (name, file_name)).replace('.', '_')] = logger


def logfile_name_add_hostname(log_name):
    hostname = socket.gethostname()  # 主机名
    if hostname:
        log_name = hostname + "-" + log_name
    return log_name


def get_logging(name=None, file_name=None):
    return LazyLogger(name=name, file_name=file_name)

# 先启动默认的 root logger，输出到控制台
logger_root = logging.getLogger()
root_handler = logging.StreamHandler()
root_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT))
logger_root.addHandler(root_handler)

# 日志的使用从此处导入
get_logger = get_logging