import yaml

# from tornado_swagger.model import register_swagger_model
# from tornado_swagger.parameter import register_swagger_parameter

from qnado.baseapi import user_api


def gen_task_handler_doc():
    task_detail_properties = {
        '_id': {'type': 'string'},
        'create_time': {'type': 'string'},
        'status': {'type': 'integer', 'default': 2},
        'task_id': {'type': 'string'},
        'update_time': {'type': 'string'},
        'duration': {'type': 'float', 'default': 0.1},
        'err_msg': {'type': 'string'},
    }

    # 添加 output_args
    for k,v in user_api.output_args.items():
        task_detail_properties.update({k: {'type': v.field.swagger_dtype}})
        if v.field.dtype == list:
            task_detail_properties[k].update({'default': []})

    post_parameters = {}
    for k,v in user_api.input_args.items():
        post_parameters.update({k: {'type': v.field.swagger_dtype}})
        if v.field.dtype == list:
            post_parameters[k].update({'default': []})

    doc =  {
        'GET': '---' + yaml.dump({
            'tags': ['Task'],
            'summary': 'Get task detail',
            'description': 'Get task detail by task_id.',
            'produces': ['application/json'],
            'parameters':[{
                'name': 'task_id',
                'in': 'query',
                'required': True,
                'type': 'string',
                'description': 'task id',
            }],
            'responses': {
                '200': {
                    'description': 'return task detail',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'errcode': {'type': 'integer', 'default': 0},
                            'data': {
                                'type': 'object',
                                'properties': task_detail_properties
                            }
                        }
                    }
                }
            }
        }),
        'POST': '---' + yaml.dump({
            'tags': ['Task'],
            'summary': 'Submit a new Task',
            'description': 'Submit a new Task and get task_id.',
            'produces': ['application/json'],
            'parameters':[{
                'name': 'Task',
                'in': 'body',
                'description': '',
                'schema': {
                    'type': 'object',
                    'required': list(post_parameters.keys()),
                    'properties': post_parameters
                }
            }],
            'responses': {
                '200': {
                    'description': 'return task_id',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'task_id': {'type': 'string'}
                        }
                    }
                }
            }
        })
    }
    return doc
