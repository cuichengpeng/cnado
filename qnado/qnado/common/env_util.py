# ----------- 用于载入本地配置文件【仅用于开发环境，生产环境应使用环境变量】

import os
import environ
from qnado.common.errors import ApiException


SETTINGS_DIR = os.getcwd()
DOT_ENV_FILE = os.environ.get('DOT_ENV_FILE', default='.env')

def env_load(DOT_ENV_FILE):
    """
    初始化ENV的实例， 载入本地的env 文件配置

    注意：本地文件只应在开发环境使用，生产环境上请使用环境变量。
    """
    env = environ.Env()

    if DOT_ENV_FILE:
        env_file = os.path.join(SETTINGS_DIR, DOT_ENV_FILE)
        if os.path.exists(env_file):
            env.read_env(env_file)
        else:
            ApiException(f'The .env file not found.')
    return env

env = env_load(DOT_ENV_FILE)
