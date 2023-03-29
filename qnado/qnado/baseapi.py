import os
import sys

from abc import ABCMeta
from hashlib import md5
from importlib import import_module

from qnado import settings
from qnado.common import log_util
from qnado.common.errors import ApiException


logger = log_util.get_logger(__name__)


class UserAPILoader:
    def __init__(self, user_module_path=None) -> None:
        """
        按以下优先顺序导入 user_api
            1 参数指定
            2 从命令行读取
            3 settings 指定，可由 env 配置
        """
        # 检测命令行是否指定了用户模块
        user_module_in_cli = False
        if len(sys.argv) == 3 and sys.argv[1] in ['run', 'runserver', 'runcelery'] \
                              and sys.argv[2].endswith('.py'):
            user_module_in_cli = True

        if user_module_path:
            # 如果手动指定了 user_module_path，即代表手动调式模式，不从命令行获取
            self.user_module_path = user_module_path
            logger.warning('You define USER_MODULE_PATH in init args, so module both in your command and in settings will be ignore.')
        elif user_module_in_cli:
            dir_path = os.path.dirname(sys.argv[2])
            module_file = os.path.basename(sys.argv[2])
            if dir_path:
                sys.path.append(dir_path)
            self.user_module_path = os.path.splitext(module_file)[0]
        elif settings.USER_MODULE_PATH:
            self.user_module_path = settings.USER_MODULE_PATH
            logger.warning('You define USER_MODULE_PATH in settings, so module in your command will be ignore.')
        else:
            raise ApiException('USER API FILE must be define in command line or ".env" file. ')
        self.user_api = None

    def __load(self):
        logger.info('* Start to loading user module ...')
        sys.path.append(settings.SITE_ROOT)
        user_module = import_module(self.user_module_path)
        user_file = user_module.__file__
        task_queue_id = md5(open(user_file, 'rb').read()).hexdigest()
        logger.info(f'* Successfully loaded user module: {self.user_module_path}')

        user_api_class = None
        for v in user_module.__dict__.values():
            if isinstance(v, type) and v is not BaseAPI and issubclass(v, BaseAPI):
                user_api_class = v
        if not user_api_class:
            raise ApiException(f'* Not found subclass of BaseAPI in {self.user_module_path}')
        self.user_api = user_api_class(task_queue_id)

    def get_user_api(self):
        if not self.user_api:
            self.__load()
        return self.user_api


class ArgumentMetaclass(ABCMeta):
    def __new__(mcls, name: str, bases: tuple, namespace: dict, **kwargs):
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class Argument(metaclass=ArgumentMetaclass):
    INPUT = 'input'
    OUTPUT = 'output'
    def __init__(self, arg_type, field) -> None:
        self.arg_type = arg_type
        self.field = field


class APIMetaclass(ABCMeta):
    def __new__(mcls, name: str, bases: tuple, namespace: dict, **kwargs):
        if name != 'BaseAPI' and 'FUNCTION' not in namespace:
            raise ApiException(f'Not found "FUNCTION" attribute in {name}.')
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class BaseAPI(metaclass=APIMetaclass):
    def __init__(self, task_queue_id) -> None:
        self.raw_class_name = self.__class__.__name__
        self.class_name = self.raw_class_name.lower()
        self.db_table = 'qnado_task_' + self.class_name
        self.class_dict = self.__class__.__dict__
        self.task_function = self.__class__.FUNCTION
        self.task_function_name = self.task_function.__name__
        self.task_module = self.task_function.__module__
        self.task_queue_id = task_queue_id

        self.input_args = {}
        self.output_args = {}
        for k, v in self.class_dict.items():
            if isinstance(v, Argument) and v.arg_type == Argument.INPUT:
                self.input_args.update({k: v})
            elif isinstance(v, Argument) and v.arg_type == Argument.OUTPUT:
                self.output_args.update({k: v})

# 全局调用 user_api 均从此处导入
user_api = UserAPILoader().get_user_api()
