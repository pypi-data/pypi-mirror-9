#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError

from metrics.models import MetricsProvider


register = Library()


class MetricsNode(Node):
    def render(self, *args, **kwargs):
        providers = MetricsProvider.objects.filter(enabled=True)
        return '\n'.join(
            '<!-- start: %(name)s -->\n%(snippet)s\n<!-- end: %(name)s -->'
            % {'name': p.name, 'snippet': p.snippet}
            for p in providers
        )


@register.tag
def metrics(parser, token):
    '''
    This tag will render all the metrics providers'
    code snippets.
    '''
    args = token.split_contents()
    if len(args) > 1:
        raise TemplateSyntaxError(
            u"'%s' takes no argument (got '%s')"
            % (args[0], ' '.join(args[1:]))
        )
    return MetricsNode()
