# -*- coding: utf-8 -*-
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.auth.models import User, Group

from updoc.models import RssRoot, RssItem, RewrittenUrl, ProxyfiedHost


__author__ = "flanker"


from django.contrib.admin import site, ModelAdmin, TabularInline


class UserAdmin(ModelAdmin):
    fields = ('username', 'first_name', 'last_name', 'email',
              ('is_staff', 'is_superuser'))


class ItemInline(TabularInline):
    model = RssItem


class RssAdmin(ModelAdmin):
    inlines = [ItemInline, ]


site.unregister(User)
site.unregister(Group)
site.register(User, UserAdmin)
site.register(RssRoot, RssAdmin)
site.register(RewrittenUrl)
site.register(ProxyfiedHost)