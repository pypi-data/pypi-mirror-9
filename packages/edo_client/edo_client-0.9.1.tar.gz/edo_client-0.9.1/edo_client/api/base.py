# -*- coding: utf-8 -*-
from edo_client.error import ApiError
from requests.exceptions import ConnectionError
from requests import Response

DEFAULT_START = 0
DEFAULT_COUNT = 20

def check_execption(func):
    def _check(*arg, **kws):
        # 网络错误, 连接不到服务器
        try:
            resp, data = func(*arg, **kws)
        except ConnectionError, e:
            raise ApiError(111, 111, 'network error: ' + str(e))
        # 地址错误
        if resp.status == 404:
            raise ApiError(404, 404, '404 Not Found')

        if resp.status >= 400:
            self = arg[0]
            # 如果得到的是一个Response对象，先将数据转化为json
            if isinstance(data, Response):
                data = data.json()
            if data['code'] == 401 and  self.refresh_hook:
                self.client.refresh_token(self.access_token.refresh_token)
                if self.refresh_hook:
                    self.refresh_hook(self.access_token.token, self.access_token.refresh_token)
                return _check(*arg, **kws)

            raise ApiError(resp.status, data['code'], data['message'])

        return data 

    return _check


class BaseApi(object):
    def __init__(self, client, access_token, refresh_hook, account=None, instance=None):
        self.client = client
        self.refresh_hook = refresh_hook
        self.access_token = access_token
        self.account_name = account
        self.instance_name = instance

    def __repr__(self):
        return '<EverydoAPI Base>'

    @check_execption
    def _get(self, url, raw=False, **opts):
        # 是否返回json格式的数据
        if raw:
            response = self.access_token.get(url, stream=True, parse=None, **opts)
            return response, response.resp
 
        else:
            response = self.access_token.get(url, **opts)
            return response, response.resp.json()

    @check_execption
    def _post(self, url, raw=False, **opts):
        # 是否返回json格式的数据
        if raw:
            response = self.access_token.post(url, stream=True, parse=None, **opts)
            return response, response.resp
        else:
            response = self.access_token.post(url, **opts)
            return response, response.resp.json()

    @check_execption
    def _put(self, url, raw=False, **opts):
        # 是否返回json格式的数据
        if raw:
            response = self.access_token.put(url, stream=True, parse=None, **opts)
            return response, response.resp
 
        else:
            response = self.access_token.put(url, **opts)
            return response, response.resp.json()

    @check_execption
    def _patch(self, url, raw=False, **opts):
        # 是否返回json格式的数据
        if raw:
            response = self.access_token.patch(url, stream=True, parse=None, **opts)
            return response, response.resp
        else:
            response = self.access_token.patch(url, **opts)
            return response, response.resp.json()

    @check_execption
    def _delete(self, url, raw=False, **opts):
        # 是否返回json格式的数据
        if raw:
            response = self.access_token.delete(url, stream=True, parse=None, **opts)
            return response, response.resp
        else:
            response = self.access_token.delete(url, **opts)
            return response, response.resp.json()

