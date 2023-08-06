#coding:utf-8

from django.contrib.auth.models import User
from django.contrib.auth import get_backends

from m3_users.models import RolePermission


class ActionsBackend(object):
    # Поддержка прав доступа на уровне объекта (пока отключена, потом можно будет включить)
    supports_object_permissions = False
    # Поддержка прав доступа анонимного пользователя
    supports_anonymous_user = True

    def authenticate(self, username=None, password=None):
        '''
        Мы не будет проверять пользователя - на это есть другие бэкенды
        '''
        return None 

    def get_group_permissions(self, user_obj):
        """
        Возвращается набор строк с правами по всем группам, в которые входит пользователь
        В нашем случае это роли и права в ролях
        """
        if not hasattr(user_obj, '_role_perm_cache'):
            perms = RolePermission.objects.filter(role__assigned_users__user = user_obj).values_list('permission_code').order_by('permission_code')
            user_obj._role_perm_cache = set()
            for code in perms:
                user_obj._role_perm_cache.update(code)
        return user_obj._role_perm_cache

    def get_all_permissions(self, user_obj, obj=None):
        """
        Возвращается набор строк с правами по всем группам, в которые входит пользователь и права непосредственно пользователя
        В нашем случае это все роли, т.к. у пользователя нет прав :) 
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        return self.get_group_permissions(user_obj)

    def has_perm(self, user_obj, perm, obj=None):
        """
        Проверка наличия права у пользователя
        """
        return perm in self.get_all_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        """
        Возвращается Истина, если есть какие-либо права в указанном приложении/модуле
        """
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
    def get_perm_details(self, user_obj, perm):
        '''
        Возвращает детали прав доступа по коду
        '''
        return None

def get_permission_details(user_obj, perm):
    for backend in get_backends():
        if hasattr(backend, 'get_perm_details'):
            details = backend.get_perm_details(user_obj, perm)
            return details
    return None