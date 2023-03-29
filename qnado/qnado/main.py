import os
import sys
import time
import signal
import psutil

from multiprocessing import Process

from qnado.settings import PACKAGE_ROOT, DEMO_API_FILE, CELERYD_CONCURRENCY, CELERY_WAIT_TIMEOUT
from qnado.common.log_util import get_logger

logger = get_logger(__name__)


def term_sig_handler(sig_num, frame):
    server_p = frame.f_locals.get('server_p')
    celery_p = frame.f_locals.get('celery_p')

    # terminate sub process
    if celery_p:
        celery_p.terminate()
        celery_p.join()
    if server_p:
        server_p.terminate()
        server_p.join()
    sys.exit(0)


def run_user_module(server_sw=True, celery_sw=True):
    from qnado.server import run_server
    from qnado.tasks import run_celery

    if not server_sw and not celery_sw:
        logger.error("It's not allowed to set server_sw and celery_sw both False.")
        sys.exit(-1)

    if celery_sw:
        # 启动 celery
        celery_p = Process(target=run_celery)
        celery_p.start()

        # 等待 celery 启动完成
        celery_t0 = time.time()
        while True:
            celery_process = psutil.Process(celery_p.pid)
            if len(celery_process.children()) == CELERYD_CONCURRENCY:
                logger.info('* Successfully launched Celery workers.')
                break
            if time.time() - celery_t0 > CELERY_WAIT_TIMEOUT:
                logger.error('Timeout to launch Celery workers.')
                sys.exit(-1)
            time.sleep(0.1)

    if server_sw:
        # 启动服务
        server_p = Process(target=run_server)
        server_p.start()

    # set signal handler
    signal.signal(signal.SIGINT, term_sig_handler)
    signal.signal(signal.SIGTERM, term_sig_handler)

    # Main Loop
    while True:
        # do something in main loop
        time.sleep(5)
        # print('* main heartbeat.')


class Commander:
    # cmd 描述内容，用于 help 输出
    cmd_list = {
        'help': {
            'usage': 'qnado help',
            'description': 'Show help content.',
            'example': ''
        },
        'run': {
            'usage': 'qnado run <api_file>',
            'description': 'Launch a server and task workers for specific api_file.',
            'example': 'qnado run user_api_example.py'
        },
        'runserver': {
            'usage': 'qnado runserver <api_file>',
            'description': 'Launch a server for specific api_file.',
            'example': 'qnado run user_api_example.py'
        },
        'runcelery': {
            'usage': 'qnado runcelery <api_file>',
            'description': 'Launch task workers for specific api_file.',
            'example': 'qnado run user_api_example.py'
        },
        'demo': {
            'usage': 'qnado demo',
            'description': 'Launch a server of demo project.',
            'example': ''
        },
        'create': {
            'usage': 'qnado create <prj_name>',
            'description': 'Create a new api_file.',
            'example': 'qnado create FindMol'
        },
    }

    def __init__(self) -> None:
        pass

    def main(self):
        if len(sys.argv) == 1:
            print('* You should use some command. For example: qnado run test.py')
            return 0

        # 获取命令行参数
        cmd = sys.argv[1]
        if not hasattr(self, cmd):
            print('* Invalid command. You can type "qnado help" to get more information.')
            return -1
        getattr(self, cmd)()

    def help(self):
        for cmd, content in self.cmd_list.items():
            print(cmd)
            for label in ['usage', 'description', 'example']:
                text = content.get(label)
                if text:
                    print(f'\t* {label}: {text}')

    def run(self):
        if len(sys.argv) != 3:
            print('* Invalid usage of "run". Usage example: qnado run test.py')
            sys.exit(-1)
        if not sys.argv[2].endswith('.py'):
            print('* Invalid usage of "run". User module must end with ".py".')
            sys.exit(-1)
        run_user_module()

    def runserver(self):
        if len(sys.argv) != 3:
            print('* Invalid usage of "runserver". Usage example: qnado runserver test.py')
            sys.exit(-1)
        if not sys.argv[2].endswith('.py'):
            print('* Invalid usage of "runserver". User module must end with ".py".')
            sys.exit(-1)
        run_user_module(celery_sw=False)

    def runcelery(self):
        if len(sys.argv) != 3:
            print('* Invalid usage of "runcelery". Usage example: qnado runcelery test.py')
            sys.exit(-1)
        if not sys.argv[2].endswith('.py'):
            print('* Invalid usage of "runcelery". User module must end with ".py".')
            sys.exit(-1)
        run_user_module(server_sw=False)

    def create(self):
        if len(sys.argv) != 3:
            print('* Invalid usage of "create". Usage example: qnado create UserTask')
            return -1
        prj_name = sys.argv[2]
        new_api_file = prj_name.lower()+'.py'

        if os.path.exists(new_api_file):
            print(f'* Target api file already exists: {new_api_file}')
            return -1
        with open(new_api_file, 'w', encoding='utf8') as f:
            demo_code = open(os.path.join(PACKAGE_ROOT, 'demo', DEMO_API_FILE), encoding='utf8').read()
            f.write(demo_code.replace('SimpleDemo', prj_name))
        print(f'* New api file created: {new_api_file}')
        print(f'* You can run "qnado run {new_api_file}" to launch this api server.')
        return 0

    def demo(self):
        if len(sys.argv) != 2:
            print('* Invalid usage of "demo". Usage: qnado demo')
            sys.exit(-1)
        # 注入指令，启动 demo
        sys.argv[1] = 'run'
        sys.argv.append(os.path.join(PACKAGE_ROOT, 'demo/simple_demo.py'))
        run_user_module()


# 命令行工具的入口
main = Commander().main
