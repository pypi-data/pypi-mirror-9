# -*- coding: utf-8 -*-
import json
from .base import BaseApi

class OrgApi(BaseApi):

    def list_org_structure(self, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/list_org_structure', account=account)

    def list_person_ougroups(self, person, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/list_person_ougroups', account=account, person=person)

    def get_objects_info(self, objects, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/get_objects_info', account=account, objects=objects)

    def get_ou_detail(self, ou_id, include_disabled=False, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/get_ou_detail', account=account, ou_id=ou_id)

    def search(self, account=None, ou='', q='', scope='onelevel', object_type='', include_disabled=True):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/search', account=account, ou=ou, q=q, scope=scope,\
                         object_type=object_type, include_disabled=json.dumps(include_disabled))

    def sync(self, objects_detail, send_mail, account=None):
        account = self.account_name if account is None else account
        return self._post('/api/v1/org/sync', account=account, objects_detail=json.dumps(objects_detail), send_mail=json.dumps(send_mail))

    def remove_objects(self, objects, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/remove_objects', account=account, objects=objects)
    
    def list_groups_members(self, groups, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/list_groups_members',  account=account, groups=groups)

    def add_group_users(self, group_id, users, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/add_group_users',  account=account, group_id=group_id, users=users)

    def remove_group_users(self, group_id, users, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/remove_group_users',  account=account, group_id=group_id, users=users)

    def list_relations(self, person, relation, account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/list_relations',  account=account, person=person, relation=relation)

    def remove_relation(self, person, superior='', colleague='', subordinate='', account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/remove_relation',  account=account, person=person, superior=superior, colleague=colleague, subordinate=subordinate)

    def add_relation(self, person, superior='', colleague='', subordinate='', account=None):
        account = self.account_name if account is None else account
        return self._get('/api/v1/org/add_relation',  account=account, person=person, superior=superior, colleague=colleague, subordinate=subordinate)

