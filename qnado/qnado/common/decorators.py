import time
import inspect
import functools

from qnado.common import log_util


logger = log_util.get_logger(__name__)


def retry(retry_times=3, fixed_sleep=1, retry_on_exception=Exception):
    """
    重试装饰器
    @params retry_times: 重试次数
    @params fixed_sleep: 每次重试固定休息时间
    @params retry_on_exception: 发生指定异常的情况下重试
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            for i in range(retry_times):
                try:
                    return func(*args, **kwargs)
                except retry_on_exception:
                    logger.warning(f"{func.__name__}: 将在{fixed_sleep}秒后开始第{i+1}/{retry_times}次重试")
                    time.sleep(fixed_sleep)
            return func(*args, **kwargs)
        return wrapped

    return decorator


def add_docstring(docstring_dict):
    def wrapper(cls):
        for method in cls.SUPPORTED_METHODS:
            func = getattr(cls, method.lower(), None)
            if func:
                inspect.unwrap(func).__doc__ = docstring_dict.get(method, None)
        return cls
    return wrapper
