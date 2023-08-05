# -*- coding: utf-8 -*-
from .base import BaseApi
import time
import md5

class RechargeApi(BaseApi):
    """内部充值接口"""

    def new_code(self, amount, deadline, creator, description, secret, account_name=''):
        timestamp = int(time.time()) + 100
        text = '%s%s%s%s%s%s' % (amount, deadline, creator, description, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/recharge/new_code', amount=amount, deadline=deadline, creator=creator, description=description, timestamp=timestamp, signcode=signcode, account_name=account_name)

    def remove_code(self, code, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s%s" % (code, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/recharge/remove_code', code=code, signcode=signcode)

    def list_codes(self, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s" % (timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/recharge/list_codes',timestamp=timestamp, signcode=signcode)

    def get_code(self, code, secret):
        timestamp = int(time.time()) + 100
        text = "%s%s%s" % (code, timestamp, secret)
        signcode = md5.new(text).hexdigest()
        return self._get('/api/v1/recharge/get_code', timestamp=timestamp, code=code, signcode=signcode)
