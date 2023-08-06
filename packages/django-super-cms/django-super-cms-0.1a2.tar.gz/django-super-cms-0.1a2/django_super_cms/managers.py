# -*- coding:utf-8 -*-
# PROJECT_NAME : django-super-cms-sample
# FILE_NAME    : 
# AUTHOR       : younger shen
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, is_superuser, user_status, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)

        user = self.model(username=username,
                          email=email,
                          is_superuser=is_superuser,
                          user_status=user_status,
                          **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, 2, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, 0, **extra_fields)


class SoftDeleteManager(models.Manager):

    def __init__(self, soft=True, *args, **kwargs):
        self.soft = soft
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.soft:
            query = Q(deleted_at__isnull=True)
            return super(SoftDeleteManager, self).get_queryset().filter(query)
        else:
            return super(SoftDeleteManager, self).get_queryset()