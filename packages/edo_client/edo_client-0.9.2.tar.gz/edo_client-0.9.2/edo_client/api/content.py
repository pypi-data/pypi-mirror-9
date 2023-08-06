# -*- coding: utf-8 -*-
from .base import BaseApi
import json
import urlparse

class ContentApi(BaseApi):

    def properties(self, path='', uid='', fields=[], account=None, instance=None):
        """ 取得文件或者文件夹的元数据"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/properties', fields=','.join(fields), account=account, instance=instance, uid=uid, path=path)

    def items(self, path='', uid='', fields=[], start=0, limit=1000, account=None, instance=None):
        """ 获取文件夹下所有文件和文件夹的元数据"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/items', fields=','.join(fields), account=account, instance=instance, uid=uid, path=path, start=start, limit=limit)

    def search(self, path='', uid='', queries=[], fields=[], start=0, limit=1000, account=None, instance=None):
        """ 获取文件夹下所有文件和文件夹的元数据"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
 
        return self._get('/api/v1/content/search', queries=json.dumps(queries), fields=','.join(fields), account=account, instance=instance, uid=uid, path=path, start=start, limit=limit)

    def list_tag_groups(self, path='', uid='', account=None, instance=None):
        """ 获取标签组设置信息"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/list_tag_groups', account=account, instance=instance, uid=uid, path=path)

    def acl_grant_role(self, path='', uid='', role='', pids=[], account=None, instance=None):
        """ 角色授权"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/acl_grant_role', role=role, pids=','.join(pids), account=account, instance=instance, uid=uid, path=path)

    def acl_deny_role(self, path='', uid='', role='', pids=[], account=None, instance=None):
        """ 禁用用户角色"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/acl_deny_role', role=role, pids=','.join(pids), account=account, instance=instance, uid=uid, path=path)

    def acl_unset_role(self, path='', uid='', role='', pids=[], account=None, instance=None):
        """ 取消用户角色"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/acl_unset_role', role=role, pids=','.join(pids), account=account, instance=instance, uid=uid, path=path)

    def delete(self, path='', uid='', account=None, instance=None):
        """ 删除文件或文件夹"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/delete', account=account, instance=instance, uid=uid, path=path)

    def move(self, path='', uid='', to_uid='', to_path='', name='', account=None, instance=None):
        """ 移动文件或文件夹"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/move', account=account, instance=instance, uid=uid, path=path ,to_uid=to_uid, to_path=to_path, name=name)

    def create_folder(self, path='', uid='', name='', account=None, instance=None):
        """ 创建文件夹"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/create_folder', account=account, instance=instance, uid=uid, path=path, name=name)

    def upload(self, path='', uid='', file=None, filename='', account=None, instance=None):
        """上传文件"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._post('/api/v1/content/upload', account=account, instance=instance, path=path, uid=uid, files={'file':(filename, file)})

    def upload_rev(self, path='', uid='', file=None, parent_rev='', account=None, instance=None):
        """上传文件"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._post('/api/v1/content/upload_rev', account=account, instance=instance, path=path, uid=uid, parent_rev=parent_rev, files={'file':file})

    def download(self, path='', uid='', mime='', account=None, instance=None):
        """下载文件"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/download', raw=True, account=account, instance=instance, path=path, uid=uid, mime=mime)

    def view_url(self, path='', uid='', account=None, instance=None):
        """下载文件"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/content/view_url', account=account, instance=instance, path=path, uid=uid)

    def assistent_info(self, account=None, instance=None):
        """下载文件"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        resp = self._get('/api/v1/content/assistent_info',  raw=True, account=account, instance=instance)
        info = resp.json()
        for i in info.values():
            i['url'] = urlparse.urljoin(resp.url, './%s' % i['filename'])

        return info

    def notify(self, account=None, instance=None, path='', uid='', from_pid='', action='', body='', title='', to_pids=[], exclude_me=True, excldue_pids=[], attachments=[], methods=[]):
        """通知接口"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/notify', account=account, instance=instance, path=path, from_pid=from_pid, uid=uid, action=action, body=body, title=title, to_pids=','.join(to_pids), exclude_me=json.dumps(exclude_me), excldue_pids=','.join(excldue_pids), attachments=','.join(attachments), methods=','.join(methods))

    def update_properties(self, path='', uid='', fields={}, account=None, instance=None):
        """更新metadata"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/content/update_properties', account=account, instance=instance, path=path, uid=uid, fields=json.dumps(fields))

    def new_mdset(self, path='', uid='', mdset='', account=None, instance=None):
        """更新metadata"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/content/new_mdset', account=account, instance=instance, path=path, uid=uid, mdset=mdset)


    def remove_mdset(self, path='', uid='', mdset='', account=None, instance=None):
        """更新metadata"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/content/remove_mdset', account=account, instance=instance, path=path, uid=uid, mdset=mdset)


    def set_state(self, path='', uid='', state='', account=None, instance=None):
        """更新metadata"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name
        return self._get('/api/v1/content/set_state', account=account, instance=instance, path=path, uid=uid, state=state)


    def revision_ids(self, path='', uid='', include_temp=True, account=None, instance=None):
        """ 取得文件的历史版本清单"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/revision_ids', include_temp=json.dumps(include_temp), account=account, instance=instance, uid=uid, path=path)


    def revision_info(self, path='', uid='', revision='', account=None, instance=None):
        """ 取得文件版本信息"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/revision_info', revision=revision, account=account, instance=instance, uid=uid, path=path)


    def revision_tag(self, path='', uid='', revision='', major_version='', minor_version='', comment='', account=None, instance=None):
        """文件定版"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/revision_tag', revision=revision, major_version=major_version, minor_version=minor_version, comment=comment, account=account, instance=instance, uid=uid, path=path)


    def revision_remove(self, path='', uid='', revision='', account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/revision_remove', revision=revision, account=account, instance=instance, uid=uid, path=path)

    def submit_mdset(self, path='', uid='', mdset='', data={}, account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/submit_mdset', mdset=mdset, data=json.dumps(data), account=account, instance=instance, uid=uid, path=path)


    def submit_md(self, path='', uid='', data={}, account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/submit_md', data=json.dumps(data), account=account, instance=instance, uid=uid, path=path)

    def add_dataitem(self, path='', uid='', data={}, account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/add_dataitem', data=json.dumps(data), account=account, instance=instance, uid=uid, path=path)

    def action_workitem(self, path='', uid='', data={}, workitem_name='', action_name='', account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/action_workitem', workitem_name=workitem_name, action_name=action_name, data=json.dumps(data), account=account, instance=instance, uid=uid, path=path)

    def get_workitem(self, path='', uid='', workitem_name='', account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/get_workitem', workitem_name=workitem_name, account=account, instance=instance, uid=uid, path=path)

    def search_workitems(self, path='', uid='', pid='', stati='', account=None, instance=None):
        """删除版本"""
        if not account: account = self.account_name
        if not instance: instance = self.instance_name

        return self._get('/api/v1/content/search_workitems', pid=pid, stati=stati, account=account, instance=instance, uid=uid, path=path)
