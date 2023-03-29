import json

from tornado.util import ObjectDict

from qnado.handlers.base.base_handler import BaseHandler
from qnado.common.errors import ApiException
from qnado.common import log_util
from qnado.common.aio_http import aio_post
from qnado.baseapi import user_api
from qnado.handlers.task_handler import TaskHandler


logger = log_util.get_logger(__name__)


class WebTaskHandler(BaseHandler):
    pattern = f'/qnado/web/{user_api.class_name}'

    async def get(self):
        return self.render('web_utils.html', **{
            'web_utils_url': self.pattern,
            'task_query_url': TaskHandler.pattern,
            'title': f'{user_api.class_name} - Task Submit',
            'input_args': [ObjectDict({'name': k, 'dtype': v.field})
                            for k,v in user_api.input_args.items()],
        })

    @BaseHandler.ajax_base
    async def post(self):
        task_input_data = self.get_json()
        logger.info(f'TaskHandler:task_input_data: {task_input_data}')

        # 处理后的数据
        task_data = {}

        # 必填参数检查
        for arg, v in user_api.input_args.items():
            if arg not in task_input_data:
                raise ApiException(f'lack of argument: {arg}')
            # 数据类型转换
            try:
                if v.field.dtype in (list, dict):
                    task_data.update({arg: json.loads(task_input_data[arg])})
                else:
                    task_data.update({arg: v.field.dtype(task_input_data[arg])})
            except (ValueError, TypeError, SyntaxError):
                raise ApiException(f'Invalid dtype of argument: {arg}. It must be {v.field}')

        # 调用 api
        res = await aio_post(f'{self.request.protocol}://{self.request.host}{TaskHandler.pattern}', json.dumps(task_data))
        return json.loads(res.body).get('data')
