#coding: utf-8
'''
Created on 10.06.2010

@author: akvarats
'''

from django.db import models
from django.contrib.auth.models import User

from metaroles import get_metarole


class UserRole(models.Model):
    '''
    Модель хранения роли пользователя в прикладной подсистеме
    '''
    # Наименование роли пользователя
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name=u'Наименование роли пользователя')

    # Ассоциированная с ролью метароль (определяет интерфейс пользователя).
    metarole = models.CharField(max_length=100, null=True, blank=True,
                                verbose_name=u'Метароль')

    def metarole_name(self):
        mr = get_metarole(self.metarole)
        return mr.name if mr else ''

    metarole_name.json_encode = True

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'm3_users_role'
        verbose_name = u'Роль пользователя'
        verbose_name_plural = u'Роли пользователя'


class RolePermission(models.Model):
    '''
    Разрешение, сопоставленное пользовательской роли.
    '''

    role = models.ForeignKey(UserRole, verbose_name=u'Роль')
    permission_code = models.CharField(max_length=200, db_index=True,
                                       verbose_name=u'Код права доступа')

    # Человеческое наименование разрешения с наименованиями модулей, разделенных
    # через запятые.
    verbose_permission_name = models.TextField(verbose_name=u'Описание права доступа')

    disabled = models.BooleanField(default=False, verbose_name=u'Активно')

    def __unicode__(self):
        return self.permission_code

    class Meta:
        db_table = 'm3_users_rolepermissions'
        verbose_name = u'Право доступа у роли'
        verbose_name_plural = u'Права доступа у ролей'


class AssignedRole(models.Model):
    '''
    Роль, назначенная на пользователя
    '''
    user = models.ForeignKey(User, related_name='assigned_roles',
                             verbose_name=u'Пользователь')
    role = models.ForeignKey(UserRole, related_name='assigned_users',
                             verbose_name=u'Роль')

    # TODO: Удалить, за очевидной ненужностью
    def user_login(self):
        return self.user.username if self.user else ''

    def user_first_name(self):
        return self.user.first_name if self.user else ''

    def user_last_name(self):
        return self.user.last_name if self.user else ''

    def user_email(self):
        return self.user.email if self.user else ''

    user_login.json_encode = True
    user_first_name.json_encode = True
    user_last_name.json_encode = True
    user_email.json_encode = True

    def __unicode__(self):
        return u'Роль "%s" у %s' % (self.role.name,
                                    self.user.username)

    class Meta:
        db_table = 'm3_users_assignedrole'
        verbose_name = u'Связка роли с пользователем'
        verbose_name_plural = u'Связки ролей с пользователями'
