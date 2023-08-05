# -*- coding: utf-8 -*-
"""
Define your custom middlewares in this file.
"""
import base64
from urllib.parse import unquote
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group

__author__ = "flanker"


class ProxyRemoteUserMiddleware(RemoteUserMiddleware):
    header = settings.REMOTE_USER_HEADER


GROUPS = {}


class DefaultGroupRemoteUserBackend(RemoteUserBackend):

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        if GROUPS.get(settings.DEFAULT_GROUP) is None:
            GROUPS[settings.DEFAULT_GROUP] = Group.objects.get_or_create(name=str(settings.DEFAULT_GROUP))[0]
        user.groups.add(GROUPS[settings.DEFAULT_GROUP])
        user.save()
        return user


class IEMiddleware(object):
    """Add a HTTP header for Internet Explorer Compatibility.
    Ensure that IE uses the last version of its display engine.
    """
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_template_response(self, request, response):
        response['X-UA-Compatible'] = 'IE=edge,chrome=1'
        return response


class FakeAuthenticationMiddleware(object):

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        username = settings.FAKE_AUTHENTICATION_USERNAME
        if not settings.DEBUG or not username:
            return
        user = auth.authenticate(remote_user=username)
        if user:
            request.user = user
            auth.login(request, user)


class BasicAuthMiddleware(object):

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth_data) = authentication.split(' ', 1)
            if 'basic' == authmeth.lower():
                auth_data = base64.b64decode(auth_data.strip()).decode('utf-8')
                username, password = auth_data.split(':', 1)
                user = auth.authenticate(username=username, password=password)
                if user:
                    request.user = user
                    auth.login(request, user)


class GetAuthMiddleware(object):

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        username = request.GET.get('username', '')
        password = request.GET.get('password', '')
        username = unquote(username)
        password = unquote(password)
        user = auth.authenticate(username=username, password=password)
        if user:
            request.user = user
            auth.login(request, user)
