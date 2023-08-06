#coding:utf-8
'''
Created on 11.06.2010

@author: akvarats
'''
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

from models import UserRole, AssignedRole


def get_roles_query(filter = ''):
    '''
    Возвращает запрос на получение списка ролей
    '''
    if filter:
        query = UserRole.objects.filter(name__icontains = filter)
    else:
        query = UserRole.objects.all()
    
    return query.order_by('name') 

def get_users_query(filter=''):
    '''
    Возвращает запрос на получение списка пользователей
    '''
    if 'django.contrib.auth' in settings.INSTALLED_APPS:
        if filter:
            query = User.objects.filter(
                Q(username__icontains = filter) | 
                Q(first_name__icontains = filter) | 
                Q(last_name__icontains = filter) | 
                Q(email__icontains = filter)
            )
        else:
            query = User.objects.all()
        return query.order_by('first_name', 'last_name', 'username')
    
def get_assigned_users_query(role, filter=None):
    filter_ = Q()
    if filter:
        #поиск по полям логин, имя, фамилия, email
        for field in ['username', 'first_name', 'last_name', 'email']:
            filter_ |= Q(**{'user__'+field+'__icontains': filter})
    query = AssignedRole.objects.filter(Q(role = role) & filter_).select_related('user').select_related('role')
    return query

def get_unassigned_users(role, filter):
    '''
    Хелпер возвращает список пользователей (возможно, отфильтрованных 
    по наименованию), которые еще не включены в роль
    '''
    
    # получаем список всех пользователей
    all_users = list(get_users_query(filter))
    
    # получаем список пользователей, которые назначены на роль
    assigned_users = list(get_assigned_users_query(role))
    
    excluded_users_dict = {}
    for assigned_user in assigned_users:
        excluded_users_dict[assigned_user.user.id] = assigned_user.user 
    
    result = []
    for user in all_users:
        if not excluded_users_dict.has_key(user.id):
            result.append(user)
            
    return result

def get_assigned_metaroles_query(user):
    '''
    Возвращает список метаролей у пользователя
    '''
    lst = [ metarole['role__metarole'] for metarole in AssignedRole.objects.filter(user=user). \
        select_related('role'). values('role__metarole').distinct() \
        if metarole['role__metarole']]
    # если небыло списка ролей, то возьмем метароли из профиля
    if not lst:
        prof = user.get_profile()
        if hasattr(prof, 'get_metaroles'):
            lst = prof.get_metaroles()
    return lst
