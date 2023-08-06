# -*- coding: utf-8 -*-


import tornado.web
from tornado.ioloop import IOLoop
from tornado.util import ObjectDict
from tornado.escape import url_escape
from tornado.web import _UIModuleNamespace
from tornado.concurrent import Future

import functools
import inspect
import re
import os

from tornado.web import HTTPError
from bree.escape import json_encode


def protocol(class_object):
    """
    convert protocol define to class
    """
    p = {}
    for k, v in class_object.__dict__.items():

        if k[0:2] != '__':
            p[k] = v

        pass

    return p


def model(method):
    """
    create tornado style model
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.io_loop = kwargs.get('io_loop', IOLoop.current())
        return method(self, *args, **kwargs)

    return wrapper


def build_settings(settings, boot_path, debug=None):
    """
    rebuild settings
    :param boot_path: this should be always set __file__
    :param settings_debug: @note this will replace sub-node,so don't set many dimensions settings
    :param settings: production settings
    :return:
    """

    root_path = os.path.dirname(boot_path)
    parent_path = os.path.dirname(root_path)

    if callable(settings):
        settings = settings()

    settings_debug = {}

    if callable(debug):
        settings_debug = debug()
    elif isinstance(debug, dict):
        settings_debug = debug
        pass

    settings.update(settings_debug)

    if 'static_path' not in settings:
        settings['static_path'] = os.path.join(parent_path, 'static')

    if 'static_url' not in settings:
        settings['static_url'] = '/static'

    if 'cdn' in settings:
        settings['static_url'] = settings['cdn'] + settings['static_url']

    if 'template_path' not in settings:
        settings['template_path'] = os.path.join(root_path, 'templates')

    settings['static_path'] = os.path.join(root_path, 'static')

    if settings_debug:
        settings['debug'] = True
        settings['js_debug'] = True
        settings['css_debug'] = True


    return settings


def async(entry, future):
    """
    easily create tornado async function,
    please note you must set future result at last async function

    """
    entry()
    return future


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        """
        a lot of code copy from tornado,because we must make sure self.initialize execute at last
        :param application:
        :param request:
        :param kwargs:
        :return:
        """

        self.application = application
        self.request = request
        self._headers_written = False
        self._finished = False
        self._auto_finish = True
        self._transforms = None  # will be set in _execute
        self._prepared_future = None
        self.path_args = None
        self.path_kwargs = None
        self.ui = ObjectDict((n, self._ui_method(m)) for n, m in
                             application.ui_methods.items())


        # ez-hack

        self.debug = self.application.settings.get('debug', None)
        self.js_debug = self.application.settings.get('js_debug', None)
        self.css_debug = self.application.settings.get('css_debug', None)

        self.auth_callback = self.application.settings.get('auth_callback', None)
        self.locale_callback = self.application.settings.get('locale_callback', None)
        self.api_messages = self.application.settings.get('api_messages', {})


        # ez-hack end

        # UIModules are available as both `modules` and `_tt_modules` in the
        # template namespace.  Historically only `modules` was available
        # but could be clobbered by user additions to the namespace.
        # The template {% module %} directive looks in `_tt_modules` to avoid
        # possible conflicts.
        self.ui["_tt_modules"] = _UIModuleNamespace(self,
                                                    application.ui_modules)
        self.ui["modules"] = self.ui["_tt_modules"]
        self.clear()
        self.request.connection.set_close_callback(self.on_connection_close)
        self.initialize(**kwargs)
        pass


    def get_current_user(self):
        '''
        use user custom auth function if set.
        :return:
        '''
        if self.auth_callback:
            return self.auth_callback(self)
        return None


    def get_user_locale(self):
        """Override to determine the locale from the authenticated user.

        If None is returned, we fall back to `get_browser_locale()`.

        This method should return a `tornado.locale.Locale` object,
        most likely obtained via a call like ``tornado.locale.get("en")``
        """

        if self.locale_callback:
            return self.locale_callback(self)
        return None


    def get_template_namespace(self):
        '''
        Add other namespace
        :return:
        '''

        namespace = super(RequestHandler, self).get_template_namespace()

        namespace.update({
            'js_debug': self.js_debug,
            'css_debug': self.css_debug
        })

        return namespace


    def api_write(self, ret, error_msg=None, messages=None, jsonp=None, **kwargs):
        """
        @todo we can add wrap to log api dump
        :param status: status code
        :param messages: messages
        :param kwargs: extra-data
        :return:None
        """

        messages = messages or self.api_messages

        if type(ret) is bool:
            ret = int(not ret)

        data = dict(ret=ret)

        if messages and error_msg:
            data['error_msg'] = self.locale.translate(messages.get(error_msg))
        elif error_msg:
            data['error_msg'] = error_msg
            pass

        data.update(kwargs)

        if jsonp:
            self.set_header('Content-Type', 'application/javascript')
            self.write(jsonp + '(' + json_encode(data) + ');')
        else:
            self.set_header('Content-Type', 'application/json')
            self.write(json_encode(data))

        pass


    def post_redirect(self, url, msg, breadcrumbs=[], recommend=[], *args, **kwargs):

        """
        don't use get to set argument
        :param url:
        :param data:
        :return:
        """

        try:
            breads_title, breads_url = zip(*breadcrumbs)
            self.set_cookie('rt_breads_title', url_escape('|'.join(breads_title)))
            self.set_cookie('rt_breads_url', url_escape('|'.join(breads_url)))
        except:
            pass

        try:
            rec_title, rec_url = zip(*recommend)
            self.set_cookie('rt_rec_title', url_escape('|'.join(rec_title)))
            self.set_cookie('rt_rec_url', url_escape('|'.join(rec_url)))
        except:
            pass

        for k, v in kwargs.items():
            if isinstance(v, list):
                self.set_cookie('rt_' + k, url_escape('|'.join(v)))
            else:
                self.set_cookie('rt_' + k, url_escape(v))
            pass

        self.set_cookie('rt_msg', url_escape(msg))
        self.redirect(url)
        pass


pass


def detect_browser(method):
    """

    :param method:
    :return:
    """


    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.browser_prefer = "mobile"

        regex = r"(nokia|iphone|android|motorola|^mot\-|softbank|foma|docomo|kddi|up\.browser|up\.link|" \
                "htc|dopod|blazer|netfront|helio|hosin|huawei|novarra|CoolPad|webos|techfaith|palmsource|" \
                "blackberry|alcatel|amoi|ktouch|nexian|samsung|^sam\-|s[cg]h|^lge|ericsson|philips|sagem|wellcom|bunjalloo|maui|" \
                "symbian|smartphone|midp|wap|phone|windows ce|iemobile|^spice|^bird|^zte\-|longcos|pantech|gionee|^sie\-|portalmmm|" \
                "jig\sbrowser|hiptop|^ucweb|^benq|haier|^lct|opera\s*mobi|opera\*mini|320×320|240×320|176×220" \
                ")"

        user_agent = self.request.headers.get('User-Agent')

        result = re.search(regex, user_agent, re.I)

        if not result:
            self.browser_prefer = "desktop"

        return method(self, *args, **kwargs)


    return wrapper


def detect_ie(method):
    """
    ie 678
    :return:
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user_agent = self.request.headers.get('User-Agent')

        if user_agent.find("MSIE 6") > -1:
            self.hacking_ie = 6
        elif user_agent.find("MSIE 7") > -1:
            self.hacking_ie = 7
        elif user_agent.find("MSIE 8") > -1:
            self.hacking_ie = 8

        return method(self, *args, **kwargs)

    return wrapper


class RenderMixin(object):
    @detect_ie
    @detect_browser
    def render(self, template_name, **kwargs):
        template_name = template_name.format(self.browser_prefer)
        return super(RequestHandler, self).render(template_name, **kwargs)

    pass
