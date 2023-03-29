from qnado.baseapi import BaseAPI, Argument
from qnado.core.fields import (
    IntegerField, FloatField, StringField, BoolField, ListField, DictField)


class SimpleDemo(BaseAPI):
    """
    说明：这是一个 Qnado 的示例，用于演示各项功能的使用方式。
    """
    @staticmethod
    def FUNCTION(a, b):     # 这里改为实际任务的输入参数

        sum = a + b         # 在这里编写任务代码，或者直接调用对应任务

        return {
            'sum': sum      # 这里以键值对的形式输出结果数据
        }

    # 在下方定义输入参数的数据类型
    a = Argument(Argument.INPUT, IntegerField)
    b = Argument(Argument.INPUT, IntegerField)

    # 在下方定义结果参数的数据类型
    sum = Argument(Argument.OUTPUT, IntegerField)
