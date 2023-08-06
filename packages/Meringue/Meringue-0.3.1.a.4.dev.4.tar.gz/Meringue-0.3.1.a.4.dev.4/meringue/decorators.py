# -*- coding: utf-8 -*-

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def anonymous_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url=None):
    """
        Докоратор пропускает только неавторизованных пользователей, в ином случае редиректит
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
