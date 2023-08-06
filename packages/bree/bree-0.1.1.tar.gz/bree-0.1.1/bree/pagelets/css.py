# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.web import UIModule


class CSS(UIModule):
    def render(self, origin, compress=None, *args, **kwargs):
        debug = self.handler.css_debug

        to_show = []

        buff = ''

        if debug or compress is None:
            if isinstance(origin, str):
                to_show = [origin]
            else:
                to_show = origin
        else:
            if isinstance(compress, str):
                to_show = [compress]
            else:
                to_show = compress

        for i in to_show:
            buff += '<link href="{}" media="screen" rel="stylesheet" type="text/css">'.format(self.handler.static_url(i))
        pass

        return buff







