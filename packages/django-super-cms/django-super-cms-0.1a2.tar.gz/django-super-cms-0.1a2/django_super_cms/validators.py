# -*- coding:utf-8 -*-
# PROJECT_NAME : mysite
# FILE_NAME    : 
# AUTHOR       : younger shen

from django.contrib.auth import authenticate
from django_laravel_validator.validator import Validator
from django_super_cms.models import User
from .utils import captcha_validate
from .messages import CAPTCHA_INVALID
from .messages import USER_INVALID
from .messages import CREATE_USER_FAILED


class UserLoginValidator(Validator):
    username = 'required'
    password = 'required'
    captcha_0 = 'required'
    captcha_1 = 'required'

    def check(self):
        captcha_0 = self.get('captcha_0')
        captcha_1 = self.get('captcha_1')
        username = self.get('username')
        password = self.get('password')
        if not captcha_validate(captcha_0, captcha_1):
            self.add_error(dict(captcha=CAPTCHA_INVALID))
        else:
            user = authenticate(username=username, password=password)
            if not user:
                self.add_error(dict(user=USER_INVALID))
            else:
                setattr(self, 'user', user)


class UserRegistValidator(Validator):
    username = 'required'
    captcha_0 = 'required'
    captcha_1 = 'required'
    password = 'required|min:8'
    password_confirm = 'required|min:8|match:password'
    email = 'required|email|unique:django_super_cms.User,email'

    def check(self):
        captcha_0 = self.get('captcha_0')
        captcha_1 = self.get('captcha_1')

        if not captcha_validate(captcha_0, captcha_1):
            self.add_error(dict(captcha=CAPTCHA_INVALID))
        else:
            username = self.get('username')
            password = self.get('password')
            email = self.get('email')
            user = User.objects.create_user(username, email=email, password=password)
            if user:
                user = authenticate(username=username, password=password)
                setattr(self, 'user', user)
            else:
                self.add_error(dict(user=CREATE_USER_FAILED))