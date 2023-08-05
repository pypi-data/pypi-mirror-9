# -*- coding: utf-8 -*-
from edo_client.api import OcAPI, WoAPI, ViewerAPI, OrgAPI, OperatorAPI, MessageAPI
from error import ApiError
import md5
from pyoauth2 import Client as OAuthClient
from pyoauth2 import AccessToken
import os

vendor = os.environ.get('EDO_VENDOR', 'test')

class EDOOAuthClient(OAuthClient):

    def get_token(self, **opts):
        """ 易度比标准得到更多的token信息

            token_info = {'app_id':'workoneline',  'pid':'zope.manager', 'permissions':'permissions', 'is_rpc':True}
        """
        self.response = self.request(self.opts['token_method'], self.token_url(), **opts)
        opts.update(self.response.parsed)
        token_info = opts.get('token_info', {})
        if token_info:
            token_info['access_token'] = opts['access_token']
            token_info['refresh_token'] = opts['refresh_token']
        return AccessToken.from_hash(self, **opts), token_info

class BaseClient(WoAPI):
    """ token管理"""

    def __init__(self, api_host, client_id, client_secret, auth_host='', redirect='', refresh_hook=None, account=None, instance=None):
        self.api_host = api_host
        self.auth_host = auth_host
        if self.auth_host:
            self.authorize_url = self.auth_host + '/@@authorize'
        else:
            self.authorize_url = ''

        self.client = EDOOAuthClient(client_id, client_secret,
                       site = api_host, 
                       authorize_url = self.authorize_url,
                       token_url = self.api_host + '/api/v1/oauth2/access_token')

        self.refresh_hook = refresh_hook
        self.redirect_uri = redirect
        self.refresh_hook = refresh_hook
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
         
        # 预先设置的account信息，方便接口调用
        self.account_name = account
        self.instance_name = instance

    @property
    def token_code(self):
        return getattr(self.access_token, 'token', None)

    @property
    def refresh_token_code(self):
        return getattr(self.access_token, 'refresh_token', None)

    def refresh_token(self, refresh_token):
        access_token = AccessToken(self.client, token='', refresh_token=refresh_token)
        self.access_token = access_token.refresh()
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    def get_authorize_url(self, account=''):
        if self.authorize_url:
            return self.client.auth_code.authorize_url(redirect_uri=self.redirect_uri)
        else:
            self.access_token = AccessToken(self.client, token='', refresh_token='')
            auth_host = self.oauth.get_auth_host(account or self.account_name)['url']
            self.access_token = None
            self.authorize_url = auth_host + '/@@authorize'
            self.client.opts['authorize_url'] = self.authorize_url
            return self.client.auth_code.authorize_url(redirect_uri=self.redirect_uri)


    def auth_with_code(self, code, account='', return_token_info=True):
        if not account:
            account = self.account_name
        self.access_token, token_info = self.client.auth_code.get_token(code, account=account, return_token_info=return_token_info)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')
        return token_info

    def auth_with_password(self, username, password, account='', **opt):
        if not account:
            account = self.account_name
        self.access_token, token_info = self.client.password.get_token(username=username,
                                 password=password, account=account, **opt)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    def auth_with_borrow_token(self, access_token, **opt):
        self.access_token, token_info = self.client.borrow.get_token(access_token=access_token, **opt)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    def auth_with_token(self, access_token, refresh_token=''):
        if isinstance(access_token, AccessToken):
            token = access_token
            access_token = token.token
            refresh_token = token.refresh_token
        self.access_token = AccessToken(self.client, token=access_token, refresh_token=refresh_token)

    def auth_with_rpc(self):
        token = md5.new(self.client_id + self.client_secret).hexdigest()
        self.auth_with_token(token)

class OcClient(BaseClient, OcAPI):
    """ 提供多种token获取途径"""

class OrgClient(BaseClient, OrgAPI):
    pass

class WoClient(BaseClient, OperatorAPI, WoAPI):
    pass

class MessageClient(BaseClient, OperatorAPI, MessageAPI):
    pass

class ViewerClient(BaseClient, OperatorAPI, ViewerAPI):
    pass

if __name__ == '__main__':
    pass

