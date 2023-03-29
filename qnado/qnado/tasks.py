import datetime

from celery import Celery
from kombu import Queue
from importlib import import_module

from qnado import settings
from qnado.common import enums
from qnado.common.db_util import db
from qnado.common import log_util
from qnado.common.errors import ApiException
from qnado.common.utils import get_trace_info
from qnado.baseapi import user_api


logger = log_util.get_logger(__name__)


def celery_setup():
    if settings.CELERY_NAME_MODE == enums.CELERY_NAME_MODE_USERFILE_MD5:
        queue_name = f'qnado_task_queue::{user_api.task_queue_id}'
        routing_key = f'qnado_task_queue::{user_api.task_queue_id}'
    else:
        queue_name = f'qnado_task_queue:{settings.HOST_NAME}:{user_api.task_queue_id}'
        routing_key = f'qnado_task_queue:{settings.HOST_NAME}:{user_api.task_queue_id}'
    celery_app = Celery()
    celery_app.conf.update({
        'broker_url': settings.CELERY_BROKER_URL,
        'result_backend': settings.CELERY_RESULT_BACKEND,
        'worker_concurrency': settings.CELERYD_CONCURRENCY,
        'timezone': 'Asia/Shanghai',
        'task_queues': [Queue(name=queue_name, routing_key=routing_key)],
        'task_routes': {f'qnado.tasks.async_task_launcher': {
                        'queue': queue_name,'routing_key': routing_key}}
    })
    return celery_app
app = celery_setup()


# 异步执行器
@app.task
def async_task_launcher(async_task, kwargs):
    mod = import_module(async_task['module'])
    task = getattr(mod, async_task['func'])
    logger.info(f'[Async task launcher] {task.__name__} in {mod.__name__}: Started.')
    task(**kwargs)
    logger.info(f'[Async task launcher] {task.__name__} in {mod.__name__}: Finished.')


def main_task(**kwargs):
    """ user_api 中的主任务 """
    task_id = kwargs.pop('task_id')
    task_data = db.find_one(user_api.db_table, {'task_id': task_id})
    if not task_data:
        # 任务不存在则不启动任务
        logger.error(f'Task[{task_id}] 数据不存在。')
        return

    kwargs.pop('status')    # 剔除 status
    # 更新任务状态 --> 执行中
    db.update(
        user_api.db_table,
        {'task_id': task_id},
        {'status': enums.TASK_RUNNING, 'update_time': datetime.datetime.now()}
    )

    # 任务调用
    try:
        logger.info(f'Task[{task_id}] 开始执行')
        res = user_api.task_function(**kwargs)
        logger.info(f'Task[{task_id}] 算法部分已执行完毕.')

        # 检查输出数据
        for arg_name, arg_ins in user_api.output_args.items():
            if arg_name not in res:
                raise ApiException(f'Not found arg[{arg_name}] in result data of task.')
            field = arg_ins.field
            if type(res[arg_name]) != field.dtype:
                raise ApiException(f'Invalid dtype of output field: {arg_name}. It must be {field}')
    except ApiException as e:
        db.update(user_api.db_table, {'task_id': task_id}, {
                'status': enums.TASK_FAILED,
                'err_msg': str(e),
                'update_time': datetime.datetime.now()})
        return
    except Exception as e:
        logger.exception(e)
        trace_str = get_trace_info(e)
        db.update(user_api.db_table, {'task_id': task_id}, {
                'status': enums.TASK_FAILED,
                'err_msg': trace_str,
                'update_time': datetime.datetime.now()})
        return

    # 添加结束时间和任务耗时
    now_dt = datetime.datetime.now()
    res.update({
        'update_time': now_dt,
        'duration': (now_dt - task_data['create_time']).total_seconds(),
        'status': enums.TASK_SUCCESS,
        'err_msg': None
    })
    # 写入数据库
    db.update(
        user_api.db_table,
        {'task_id': task_id},
        res
    )
    logger.info(f'Task[{task_id}] 已完成.')


def run_celery():
    app.start(argv=['celery', 'worker', '-l', 'INFO',
                    '-f', 'logs/%h-celery.log',
                    '--without-heartbeat', '--without-gossip', '--without-mingle'])
