#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


__all__ = ['MetricsProvider', ]


HELP_TEXTS = {
    'snippet': u'The code snippet that will be included in your pages. Be very careful, may break pages if incorrect',
}


class MetricsProvider(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=100)
    snippet = models.TextField(u'Code snippet', help_text=HELP_TEXTS['snippet'])
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
