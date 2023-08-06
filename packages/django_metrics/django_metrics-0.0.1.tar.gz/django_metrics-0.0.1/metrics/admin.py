#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from metrics.models import MetricsProvider


@admin.register(MetricsProvider)
class MetricsProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled', 'snippet_extract']

    def snippet_extract(self, obj):
        if len(obj.snippet) > 50:
            return obj.snippet[:50] + '...'
        else:
            return obj.snippet
    snippet_extract.short_description = 'Code snippet'
