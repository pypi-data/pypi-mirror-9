# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def shard(key, connection_pool):
    """
    get fix node
    :param key:
    :param connection_pool:
    :return:
    """

    if not isinstance(connection_pool, list):
        return connection_pool

    node = ord(key[0]) % len(connection_pool)
    return connection_pool[node]