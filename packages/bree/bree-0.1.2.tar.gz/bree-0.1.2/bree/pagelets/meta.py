# -*- coding: utf-8 -*-

from tornado.web import UIModule


class Meta(UIModule):
    def render(self, title='', desc='', keywords='', copyleft='', author='', icon='/static/favicon.ico', *args, **kwargs):
        buff = '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
        buff += '<title>{}</title>'.format(title)
        buff += '<meta name="description" content="{}">'.format(desc)
        buff += '<meta name="keywords" content="{}">'.format(keywords)
        buff += '<meta name="author" content="{}">'.format(author)
        buff += '<meta name="copyright" content="{}">'.format(copyleft)
        buff += '<link rel="icon" href="{}">'.format(icon)
        return buff


