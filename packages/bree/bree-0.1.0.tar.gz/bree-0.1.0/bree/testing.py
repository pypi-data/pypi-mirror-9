# -*- coding: utf-8 -*-


import functools
import bree
import bree.web
import tornado.testing
from bree.web import build_settings


def active_ci(settings_pro, settings_ci, app_path, *args, **kwargs):
    """
    change bree settings to settings_ci
    :param settings_pro: settings_pro
    :param settings_ci: settings_ci must be callable
    :return:
    """

    def wrap(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            ci = settings_ci(self.io_loop)
            bree.settings = bree.web.build_settings(settings_pro, app_path, ci)
            return f(self, *args, **kwargs)

        return wrapper


    return wrap


