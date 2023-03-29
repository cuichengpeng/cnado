import setuptools

from qnado.settings import QNADO_VERSION


setuptools.setup(
    name='qnado',
    packages=setuptools.find_packages(),
    version=QNADO_VERSION,
    description='qnado',
    author='xiaodong.ma',
    author_email='maxiaodong@turingq.com',
    python_requires='>=3.6',
    include_package_data=True,
    package_data={'': ['*.html']},
    install_requires=[req.strip() for req in open('requirements.txt') if req],
    entry_points={
        'console_scripts': [
            'qnado = qnado.main:main'
        ]
    }
)