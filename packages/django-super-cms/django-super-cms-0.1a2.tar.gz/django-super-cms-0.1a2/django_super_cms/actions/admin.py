# -*- coding:utf-8 -*-
# PROJECT_NAME : mysite
# FILE_NAME    : 
# AUTHOR       : younger shen
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django_flash_message.storage import storage
from ..validators import UserLoginValidator
from ..validators import UserRegistValidator


@require_POST
def admin_login_action(request):
    validator = UserLoginValidator(request.POST)
    if validator.fails():
        user = getattr(validator, 'user')
        login(request, user)
    else:
        errors = validator.errors()
        storage.add_message(request, 'login_errors', errors)
    return redirect(reverse('dsc_admin_login_view'))


@require_POST
def admin_regist_action(request):
    validator = UserRegistValidator(request.POST)
    if validator.fails():
        user = getattr(validator, 'user')
        login(request, user)
    else:
        errors = validator.errors()
        storage.add_message(request, 'regist_errors', errors)

    return redirect(reverse('dsc_admin_regist_view'))