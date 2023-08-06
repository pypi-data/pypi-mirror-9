# -*- coding: utf-8 -*-
from .base import BaseApi
import time
import md5

class AdminApi(BaseApi):
    """内部充值接口"""

    def new_code(self, score, deadline, creator, description, secret, account_name=''):
        timestamp = int(time.time()) + 100
        format = "%Y-%m-%d %H:%M:%S" 
        deadline = deadline.strftime(format)
        text = '%s%s%s%s%s%s' % (score, deadline, creator, description, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/admin/new_code', score=score, deadline=deadline, creator=creator, description=description, timestamp=timestamp, signcode=signcode, account_name=account_name)

    def remove_code(self, code, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s%s" % (code, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/admin/remove_code', code=code, timestamp=timestamp, signcode=signcode)

    def list_codes(self, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s" % (timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/admin/list_codes',timestamp=timestamp, signcode=signcode)

    def get_code(self, code, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s%s" % (code, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/admin/get_code', timestamp=timestamp, code=code, signcode=signcode)

    def use_code(self, code, secret, account=None):
        if not account:
            account = self.account_name
        timestamp = int(time.time()) + 100
        text = "%s%s%s" % (code, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/admin/use_code', timestamp=timestamp, code=code, signcode=signcode, account=account)

    def upgrade(self, account_name):
        return self._get('/api/v1/admin/upgrade', account_name=account_name)

