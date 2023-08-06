# -*- mode: python; coding: utf-8 -*-

from django.core.exceptions import PermissionDenied


def login_required(fn):
    def deco(*args):
        current = args[-1]
        user = current.context['request'].user

        if user is None \
           or not user.is_authenticated() \
           or not user.is_active:
            raise PermissionDenied
        return fn(*args)
    return deco


def superuser_required(fn):
    def deco(*args):
        current = args[-1]
        user = current.context['request'].user

        if user is None \
           or not user.is_authenticated() \
           or not user.is_superuser \
           or not user.is_active:

            raise PermissionDenied
        return fn(*args)
    return deco
