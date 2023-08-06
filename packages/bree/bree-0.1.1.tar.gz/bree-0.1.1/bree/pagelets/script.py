# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.web import UIModule

class Script(UIModule):
    def render(self, origin, compress=None, *args, **kwargs):
        debug = self.handler.js_debug

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

        for v in to_show:
            buff += '<script src="{}"></script>'.format(self.handler.static_url(v))
        pass

        return buff







