# -*- coding: utf-8 -*-
from .base import BaseApi
import json
import os

class OperatorApi(BaseApi):

    def create_instance(self, account_name, instance_name, instance_title, admin_uid, init_options):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                'instance_title':instance_title,
                'admin_uid':admin_uid,
                'init_options':json.dumps(init_options)
                }
        return self._get('/api/v1/operator/create_instance', **params)

    def update_options(self, account_name, instance_name,\
                               operation_options, removed_options, do_check):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                'operation_options':json.dumps(operation_options),
                'removed_options':json.dumps(removed_options),
                'do_check':json.dumps(do_check)
                }
        return self._get('/api/v1/operator/update_options', **params)

    def list_options(self, account_name, instance_name):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                }
        return self._get('/api/v1/operator/list_options', **params)

    def check_quotas(self, account_name, instance_name, quotas):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                'quotas':json.dumps(quotas),
                }
        return self._get('/api/v1/operator/check_quotas', **params)

    def update_title(self, account_name, instance_name, title):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                'title': title,
                }
        return self._get('/api/v1/operator/update_title', **params)


    def destroy_instance(self, account_name, instance_name):
        params = {'instance_name':instance_name,
                'account_name':account_name,
                }
        return self._get('/api/v1/operator/destroy_instance', **params)

    def refresh_org_cache(self, keys, account=None, instance=None):
        account = self.account_name if account is None else account
        instance = self.instance_name if instance is None else instance 

        return self._get('/api/v1/operator/refresh_org_cache', account=account, instance=instance, keys=str(keys))

