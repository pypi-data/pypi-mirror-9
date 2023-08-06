# -*- encoding:utf-8 -*-
import memcache
from edo_client import OcClient, OrgClient
try:
    from ztq_core import set_key, get_key
except ImportError:
    def set_key(key, value, system=''): pass
    def get_key(key, system=''): return None

class CachedOcClient(OcClient):

    def __init__(self, server_url, app_id, secret, account=None, instance=None, maxsize=10000, expire=24*3600):
        OcClient.__init__(self, server_url, app_id, secret, account=account, instance=instance)
        self.cache = memcache.lru_cache(maxsize=maxsize, expire=expire)

    def get_user_token_info(self, token):
        """ 得到用户的token_info """
        try:
            token_info = self.cache.get(token)
        except KeyError:
            self.auth_with_token(token)
            token_info = self.oauth.get_token_info()
            self.cache.put(token, token_info)
        return token_info

    def get_user_roles(self, user, account=None):
        """ 得到用户的角色"""
        key = "roles:%s:%s"%(account, user)
        try:
            return self.cache.get(key)
        except KeyError:
            roles = self.account.get_user_roles(user=user, account=account)
            self.cache.put(key, roles)
            return roles

class CachedOrgClient(OrgClient, OcClient):
    """ 支持缓存的admin接口 """

    def __init__(self, server_url, app_id, secret, account=None, instance=None, maxsize=5000, expire=120):
        OrgClient.__init__(self, server_url, app_id, secret, account=account, instance=instance)
        self.cache = memcache.lru_cache(maxsize=maxsize, expire=expire)

    def _get_cache(self, cache_key, skip_memcached=False):
        # 从内存中取
        if not skip_memcached:
            try:
                return self.cache.get(cache_key)
            except:
                pass

        # 从redis上取
        result = get_key(cache_key, 'cache')
        if result is not None:
            self.cache.put(cache_key, result)
            return result

    def _getValueUseCache(self, cache_key, func, skip_cache=False, **params):
        """ 根据key从redis得到值，否则从rpc调用得到值并放入redis """

        # 从内存和redis上查找缓存 
        cache = self._get_cache(cache_key, skip_cache)
        if cache:
            return cache

        # 从服务器上取 
        result = func(**params)
        if result is None:
            return None

        # 放入redis
        set_key(cache_key, result, 'cache')
        self.cache.put(cache_key, result)

        return result

    def get_objects_info(self, account, pids, skip_cache=False):
        """ 批量得到人员和组的信息 """
        users = []
        values = []
        for pid in pids:
            object_type, name = pid.split(':')
            key = "pinfo:%s:%s.%s"%(account, object_type, name)

            # 从内存和redis上查找缓存 
            value = self._get_cache(key, skip_cache)
            if value is None:
                users.append(pid)
            else:
                values.append(value)

        if not users:
            return values

        infos = self.org.get_objects_info(account=account, objects=','.join(users))
        for info in infos:
            key = "pinfo:%s:%s.%s"%(account, info['object_type'], info['id'])
            self.cache.put(key, info)
            set_key(key, info, 'cache')
            values.append(info)
        return values

    def list_person_groups(self, account, user_id):
        key = "gusers:%s:%s"%(account, user_id)
        remote_groups= self._getValueUseCache(key, self.org.list_person_ougroups, person=user_id, account=account) or {}
        return remote_groups

    def get_ou_detail(self, account, ou_id, include_disabled=False, skip_cache=False):
        key = 'oudetail:%s:%s:%s' % (account, ou_id, str(include_disabled))
        return self._getValueUseCache(key, self.org.get_ou_detail, ou_id=ou_id, include_disabled=include_disabled, account=account, skip_cache=skip_cache)

    def list_groups_members(self, account, group_ids, skip_cache=False):
        """ 批量得到组的人员列表 """
        if isinstance(group_ids, basestring):
            group_ids = [group_ids]

        groups = []
        result = []
        for group_id in group_ids:
            key = "gmembers:%s:%s"%(account, group_id)

            value = self._get_cache(key) if not skip_cache else None
            if value is None:
                groups.append(group_id)
            else:
                result.extend([user_id for user_id in value])
        if not groups:
            return list(set(result))

        groups = self.org.list_groups_members(account=account, groups=','.join(groups))
        for group_key, group_value in groups.items():
            key = "gmembers:%s:%s"%(account, group_key)
            self.cache.put(key, group_value)
            set_key(key, group_value, 'cache')
            result.extend([user_id for user_id in group_value])

        return list(set(result))

    def list_org_structure(self, account, skip_cache=False):
        key = "orgstr:%s" % (account)
        org_structure = self._getValueUseCache(key, self.org.list_org_structure, account=account, skip_cache=skip_cache) or {}
        
        return org_structure

    def list_instances(self, account, application, skip_cache=False):
        key = "instanceinfo:%s" % (account)
        value = self._getValueUseCache(key, self.account.list_instances, account=account, application=application, skip_cache=skip_cache)
        return value

