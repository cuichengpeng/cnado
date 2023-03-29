import datetime
import uuid

from qnado.handlers.base.base_handler import BaseHandler
from qnado.common.errors import ApiException
from qnado.common.db_util import db
from qnado.common import log_util
from qnado.common import enums
from qnado.baseapi import user_api
from qnado.tasks import async_task_launcher
from qnado.settings import ASYNC_TASKS
from qnado.common.decorators import add_docstring
from qnado.common.swagger_docstring import gen_task_handler_doc


logger = log_util.get_logger(__name__)


@add_docstring(gen_task_handler_doc())
class TaskHandler(BaseHandler):
    pattern = f'/qnado/api/{user_api.class_name}'

    @BaseHandler.ajax_base
    async def get(self):
        task_id  = self.get_argument('task_id', '')
        if not task_id:
            raise ApiException("Not found 'task_id' in arguments.")
        if len(task_id) != 32:
            raise ApiException('Invalid format of task_id.')

        # 查询结果数据
        data = db.find_one(user_api.db_table, {'task_id': task_id})
        if not data:
            raise ApiException(f'Task[{task_id}] does not exists.')
        return data

    @BaseHandler.ajax_base
    async def post(self):
        task_input_data = self.get_json()
        logger.info(f'TaskHandler:task_input_data: {task_input_data}')

        # 必填参数检查
        for arg, v in user_api.input_args.items():
            if arg not in task_input_data:
                raise ApiException(f'lack of argument: {arg}')
            if type(task_input_data[arg]) != v.field.dtype:
                raise ApiException(f'Invalid dtype of argument: {arg}. It must be {v.field}')

        # 执行前保存任务参数
        params = {k: task_input_data[k] for k in user_api.input_args.keys()}
        # 添加创建时间，分配 task_id
        task_id = uuid.uuid4().hex
        params.update({
            'create_time': datetime.datetime.now(),
            'status': enums.TASK_SUBMITTED,
            'task_id': task_id})
        db.insert(user_api.db_table, params)   # 数据库自增 id

        # 启动异步任务
        params.pop('create_time', None)
        async_task_launcher.delay(ASYNC_TASKS['main_task'], params)
        return {'task_id': task_id}
