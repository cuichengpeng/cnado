from qnado.web.base_api import BaseAPI, Argument
from qnado.fields import (
    IntegerField, FloatField, StringField, BoolField, ListField, DictField)


def xalgo_calc(a_int, b_float, c_str, d_bool, e_list, f_dict):
    import time
    time.sleep(2)
    return {
        'res_a_int':    a_int + 100,
        'res_b_float':  b_float + 100.0,
        'res_c_str':    c_str + '_tail',
        'res_d_bool':   not d_bool,
        'res_e_list':   e_list + ['abc'],
        'res_f_dict':   {k:v for k,v in list(f_dict.items()) + [('k1', 10)]},
    }


class APIExample(BaseAPI):
    # 任务配置
    #   - FUNCTION 为固定标识符
    #   - xalgo_calc 是具体的任务函数（应是一个可调用对象）
    FUNCTION = xalgo_calc

    # 输入参数
    a_int = Argument(Argument.INPUT, IntegerField)
    b_float = Argument(Argument.INPUT, FloatField)
    c_str = Argument(Argument.INPUT, StringField)
    d_bool = Argument(Argument.INPUT, BoolField)
    e_list = Argument(Argument.INPUT, ListField)
    f_dict = Argument(Argument.INPUT, DictField)

    # 结果参数
    res_a_int = Argument(Argument.OUTPUT, IntegerField)
    res_b_float = Argument(Argument.OUTPUT, FloatField)
    res_c_str = Argument(Argument.OUTPUT, StringField)
    res_d_bool = Argument(Argument.OUTPUT, BoolField)
    res_e_list = Argument(Argument.OUTPUT, ListField)
    res_f_dict = Argument(Argument.OUTPUT, DictField)

    # API 接口参数 示例 （POST body）
    # {
    #     "a_int": 100,
    #     "b_float": 8.8,
    #     "c_str": "hello",
    #     "d_bool": true,
    #     "e_list": [1, 2, 3],
    #     "f_dict": {"a1": 9}
    # }
