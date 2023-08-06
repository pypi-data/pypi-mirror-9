# -*- coding:utf-8 -*-
# PROJECT_NAME : mysite
# FILE_NAME    : 
# AUTHOR       : younger shen
from functools import wraps
import cjson
from captcha.models import CaptchaStore
from captcha.models import get_safe_now
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponseNotAllowed
from django.conf import settings
from django.shortcuts import redirect


def captcha_validate(key, value):
    try:
        captcha = CaptchaStore.objects.get(response=value, hashkey=key, expiration__gt=get_safe_now())
    except CaptchaStore.DoesNotExist:
        return False
    else:
        captcha.delete()
        return True


def require_ajax(view_func):
    @wraps(view_func)
    def inner(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed(request.method)
        else:
            return view_func(request, *args, **kwargs)
    return inner

require_AJAX = require_ajax


def queryset_to_json(qs, fields=None, use_natural_foreign_key=False, use_natural_primary_keys=False):
    data = serializers.serialize('json', qs, fields=fields, use_natural_foreign_keys=use_natural_foreign_key, use_natural_primary_keys=use_natural_primary_keys)
    return cjson.decode(data)


def captcha_generator():
    key = CaptchaStore.generate_key()
    refresh_url = reverse('captcha-refresh')
    image_url = reverse('captcha-image', kwargs={'key': key})
    return dict(captcha_key=key, captcha_refresh_url=refresh_url, captcha_image_url=image_url)


def already_login_redirect(viewe_func, redirect_url=settings.LOGIN_REDIRECT_URL):
    def decorator(view_func):
        def wrapper_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(redirect_url)
            else:
                return view_func(request, *args, **kwargs)
        return wrapper_view
    return decorator(viewe_func)