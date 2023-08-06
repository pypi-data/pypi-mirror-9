# -*- coding: utf-8 -*-
import hashlib
import json
from .base import BaseApi

class ViewerApi(BaseApi):

    def get_secret(self, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/viewer/get_secret', account=account, instance=instance)

    def set_access_policy(self, policy='private', account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/viewer/set_access_policy', account=account, instance=instance, policy=policy)

    def get_access_policy(self, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/viewer/get_access_policy', account=account, instance=instance)
    
    def refresh_secret(self, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/viewer/refresh_secret', account=account, instance=instance)

    def transform(self, location, timestamp='', signcode='', targets='', callbacks=None, params=None, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/transform', location=location, account=account, instance=instance,
                         timestamp=timestamp,
                         signcode=signcode,
                         targets=targets, callbacks=json.dumps(callbacks), params=json.dumps(params))

    def gen_view_signcode(self, location, account, instance, secret, ip='', timestamp='', username='', permission=''):
        text = location + account + instance + ip + timestamp + username + permission + secret
        sign_md5 = hashlib.md5()
        sign_md5.update(text)
        signcode = sign_md5.hexdigest()
        return signcode

    def test_signcode(self, location, account, instance, signcode, **kwargs):
        return self._get('/api/v1/viewer/test_signcode', location=location, account=account, instance=instance,
                signcode=signcode, **kwargs)


