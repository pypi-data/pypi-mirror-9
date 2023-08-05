# -*- coding: utf-8 -*-
from .base import BaseApi

class OAuthApi(BaseApi):

    def get_token_info(self):
        """ 当前用户的账户信息 """
        return self._get('/api/v1/oauth2/get_token_info')

    def get_auth_host(self, account):
        """ 当前用户的账户信息 """
        return self._get('/api/v1/oauth2/get_auth_host', account=account)
