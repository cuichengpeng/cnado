import os
from qnado.common.oss_util import oss
from qnado.settings import QNADO_VERSION


def upload2oss():
    whl = os.path.join('dist', f'qnado-{QNADO_VERSION}-py3-none-any.whl')
    if not os.path.exists(whl):
        print(f'* File not found: {whl}')
    whl_url = oss.put_object_from_file(f'qnado/{whl}', whl)
    print(f'Successfully uploaded: {whl_url}')


if __name__ == '__main__':
    upload2oss()
