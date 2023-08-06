# -*- coding: utf-8 -*-
import hashlib
import json
import time
from .base import BaseApi


msg_host = 'http://192.168.1.115:63015'

class MessageApi(BaseApi):
    def __init__(self, *args, **kwargs):
        self.client_id = kwargs.pop('client_id', None)
        super(MessageApi, self).__init__(*args, **kwargs)

    def get_secret(self, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/admin/get_secret', account=account, instance=instance)

    def refresh_secret(self, account=None, instance=None):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/admin/refresh_secret', 
                         account=account, instance=instance)

    def connect(self, account=None, instance=None, username=None, timestamp=None, signature=None):
        '''
        Connect to MessageCenter, get personal topic & client id
        '''
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        client_id = self.client_id or None
        resp = self._post(msg_host + '/api/v1/message/connect', 
                          account=account, instance=instance, 
                          client_id=client_id, username=username, 
                          timestamp=timestamp, signature=signature)
        self.client_id = resp.get('client_id', self.client_id)
        return resp

    def chat(self, to, body, from_user=None, account=None, instance=None, context={}, attachments=[], subject=''):
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        client_id = self.client_id
        return self._post(msg_host + '/api/v1/message/chat', account=account, 
                          instance=instance, client_id=client_id, 
                          msg_type=msg_type, to=to, body=body, 
                          context=context, attachments=attachments, 
                          subject=subject)

    def notify(self, to, body, from_user=None, context=None, attachments=None, subject=None, channel=None, action=None, account=None, instance=None):
        '''
        Send a notify message
        '''
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._post(msg_host + '/api/v1/message/notify', 
                         account=account, instance=instance, to=to, from_user=json.dumps(from_user), 
                         context=json.dumps(context), attachments=json.dumps(attachments), 
                         subject=subject, body=body, 
                         channel=channel, action=action)

    def query(self, account=None, instance=None, time_start=None, time_end=None, limit=50):
        '''
        Query history messages
        Args:
            instance: 消息区的实例号
            time_start 起始的消息 ID，默认为第一条未读消息 ID
            time_end 最末一条消息 ID，可选
            limit 消息数量限制，默认 50
        '''
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get(msg_host + '/api/v1/message/query', 
                         account=account, 
                         instance=instance, 
                         time_start=time_start, 
                         time_end=time_end, 
                         limit=limit)

    def query_count(self, account=None, instance=None, time_start=None, time_end=None):
        '''
        Query message count within specified time range
        Args:
            instance: 消息区的实例号
            time_start 起始的消息 ID，默认为第一条未读消息 ID
            time_end 最末一条消息 ID，可选
        '''
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get(msg_host + '/api/v1/message/query_count', 
                         account=account, 
                         instance=instance, 
                         time_start=None, 
                         time_end=time_end)

    def unread_stat(self, account=None, instance=None):
        '''
        Get statics of unread messages
        Args:
            instance: 消息区的实例号
        '''
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get(msg_host + '/api/v1/message/unread_stat', 
                         account=account, 
                         instance=instance)

