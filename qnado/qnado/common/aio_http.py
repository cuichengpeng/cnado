import asyncio
import functools
import errno
from tornado.util import errno_from_exception
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

def retry_aio_http(times=3,duration=0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for t in range(times):
                try:
                    return await func(*args, **kwargs)
                except OSError as e:
                    if errno_from_exception(e) == errno.ENOTCONN:
                        # tornado http client 是个单例，当单例持有链接被关闭时，手动关闭单例
                        c = AsyncHTTPClient()
                        c.close()
                        if duration > 0:
                            await asyncio.sleep(duration)
                        if t + 1 == times:
                            raise e
                    else:
                        raise
        return wrapper
    return decorator


async def aio_get(url, headers=None, **kwargs):
    if headers is None:
        headers = {}
    response = await AsyncHTTPClient().fetch(HTTPRequest(
        url,
        headers=headers,
        **kwargs
    ))
    return response

@retry_aio_http(3,1)
async def aio_post(url, body="", headers=None, **kwargs):
    """
    async post请求
    :param url:
    :param body:
        两种形式：
        1. form_data：urlencode(dict)
        2. json data：json.dumps(dict)
    :param headers:
    :param kwargs:
    :return:
        response对象，取返回体方式：response.body
    """
    if headers is None:
        headers = {}
    response = await AsyncHTTPClient().fetch(HTTPRequest(
        url,
        method='POST',
        body=body,
        headers=headers,
        **kwargs
    ))
    return response


async def aio_patch(url, body="", headers=None, **kwargs):
    if headers is None:
        headers = {}
    response = await AsyncHTTPClient().fetch(HTTPRequest(
        url,
        method='PATCH',
        body=body,
        headers=headers,
        **kwargs
    ))
    return response


async def aio_put(url, body="", headers=None, **kwargs):
    if headers is None:
        headers = {}
    response = await AsyncHTTPClient().fetch(HTTPRequest(
        url,
        method='PUT',
        body=body,
        headers=headers,
        **kwargs
    ))
    return response