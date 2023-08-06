#coding:utf-8
"""
Created on 10.06.2010

@author: akvarats
"""

from django.conf import urls

from m3 import authenticated_user_required
from m3.actions import ActionController

from roles import RolesActions, Roles_DictPack
from users import UsersActions
from metaroles import UserMetarole, Metaroles_DictPack

# Константы:
GENERIC_USER = 'generic-user'
ADMIN = 'admin'
SUPER_ADMIN = 'super-admin'

# контроллер
users_controller = ActionController(url='/m3-users', name=u'Пользователи М3')


def register_actions():
    users_controller.packs.extend([
        RolesActions(),
        UsersActions(),
        Roles_DictPack(),
        
        Metaroles_DictPack(), # метароли пользователей
    ])

def register_urlpatterns():
    """
    Регистрация конфигурации урлов для приложения m3.contrib.users
    """
    return urls.patterns('',
        (r'^m3-users', 'm3_users.app_meta.users_view'),
    )

#===============================================================================
# Регистрация метаролей для приложения
#===============================================================================        
def register_metaroles(manager):
    """
    Функция возвращает список метаролей, которые регистрируются
    по умолчанию на уровне Платформы М3.
    
    @param manager: объект, отвечающий за управление метаролями.
    """
    
    # метароль обычного пользователя системы
    manager.GENERIC_USER_METAROLE = UserMetarole(GENERIC_USER, u'Обобщенный пользователь')
    
    # метароль администратора системы
    manager.ADMIN_METAROLE = UserMetarole(ADMIN, u'Администратор')
    manager.ADMIN_METAROLE.included_metaroles.extend([manager.GENERIC_USER_METAROLE])
    
    # метароль супер-администратора системы
    manager.SUPER_ADMIN_METAROLE = UserMetarole(SUPER_ADMIN, u'Супер-администратор')
    manager.SUPER_ADMIN_METAROLE.included_metaroles.extend([manager.GENERIC_USER_METAROLE, manager.ADMIN_METAROLE])
    
    return [manager.GENERIC_USER_METAROLE, manager.ADMIN_METAROLE, manager.SUPER_ADMIN_METAROLE]

#===============================================================================
# Представления
#===============================================================================
@authenticated_user_required
def users_view(request):
    return users_controller.process_request(request)
