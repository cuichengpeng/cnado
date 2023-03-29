import tornado.web
import json
import datetime
import functools

from tornado.web import RequestHandler
from qnado.common import log_util
from qnado.common import enums
from qnado.common.errors import ApiException
from bson import ObjectId


access_logger = log_util.get_logging('access', file_name='access.log')
app_logger = log_util.get_logging('app')


class BaseHandler(RequestHandler):
    def prepare(self, *args, **kwargs):
        access_logger.info('{}:[{}]{} start'.format(self.request.remote_ip, self.request.method, self.request.uri))

    def on_finish(self):
        access_logger.info('{}:[{}]{} finished'.format(self.request.remote_ip, self.request.method, self.request.uri))

    def _get_argument_as_dict(self):
        if not hasattr(self, "__dict_args"):
            self.__dict_args = json.loads(self.request.body)
        return self.__dict_args

    def get_argument_file(self, argument, default=None, strip=True):
        if self.request.files:
            file = self.request.files[argument][0]
            return file
        else:
            return default

    def get_json(self):
        if hasattr(self, '_json'):
            return self._json
        try:
            _json = json.loads(self.request.body)
        except Exception:
            _json = {}
        self._json = _json
        return _json

    def write_json(self, data=None, errcode=0, errmsg=None, status=None):
        ''''''
        self.set_header('Content-Type', 'text/json')
        if isinstance(status, int):
            self.set_status(status)
        dic = {'errcode': errcode, 'data': data or []}
        if errmsg:
            dic['errmsg'] = errmsg
        self.write(json.dumps(dic, cls=MyJsonEncoder))

    @classmethod
    def ajax_base(cls, method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            try:
                result = await method(self, *args, **kwargs)
                self.write_json(data=result, errcode=enums.AJAX_SUCCESS, errmsg=None, status=None)
            except ApiException as e:
                app_logger.error(e)
                self.write_json(data=None, errcode=enums.AJAX_FAIL_NORMAL,
                                errmsg=str(e), status=None)
            except Exception as e:
                app_logger.exception(e)
                self.write_json(data=None, errcode=enums.AJAX_FAIL_NORMAL,
                                errmsg=enums.ERRCODE_DICT[enums.AJAX_FAIL_NORMAL], status=None)
            self.finish()

        return wrapper


class MyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class PageNotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("error.html", msg="page not found")
    
    def post(self):
        self.render("error.html", msg="page not found")
    
    def initialize(self, status_code):
        self.set_status(status_code)
