# -*- coding: utf-8 -*-


# some feature not find a good place


import bree

import bree.web


def build_settings(settings, boot_path, debug=None):
    """
    a wrapper for web.build_settings
    :param boot_path: this should be always set __file__
    :param settings_debug: @note this will replace sub-node,so don't set many dimensions settings
    :param settings: production settings
    :return:
    """
    bree.settings = bree.web.build_settings(settings,boot_path,debug)

    return bree.settings


