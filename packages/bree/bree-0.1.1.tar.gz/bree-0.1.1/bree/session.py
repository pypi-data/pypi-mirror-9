# -*- coding: utf-8 -*-


from uuid import uuid1


class RemoteIPExpection(Exception):
    """
    user change request ip
    """

    pass


class RedisSessionStore(object):
    def __init__(self, redis_connection, **options):
        self.options = {
            'key_prefix': 'sid',
            'expire': 7200,
        }
        self.options.update(options)
        self.redis_pool = redis_connection
        pass


    def prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    def chose_handler(self, sid):
        if isinstance(self.redis_pool, list):
            return self.redis_pool[ord(sid[0]) % len(self.redis_pool)]
        else:
            return self.redis_pool
        pass

    def get_session(self, sid, name):
        redis_connection = self.chose_handler(sid)
        data = redis_connection.hget(self.prefixed(sid), name)
        session = data.decode('utf-8') if data else None
        return session


    def set_session(self, sid, k, v):
        redis_connection = self.chose_handler(sid)
        redis_connection.hset(self.prefixed(sid), k, v)

        expiry = self.options['expire']
        if expiry:
            redis_connection.expire(self.prefixed(sid), expiry)


    def delete_session(self, sid):
        redis_connection = self.chose_handler(sid)
        redis_connection.delete(self.prefixed(sid))

    def delete_session_item(self, sid, *keys):
        redis_connection = self.chose_handler(sid)
        redis_connection.hdel(self.prefixed(sid), *keys)
        if expiry:
            redis_connection.expire(self.prefixed(sid), expiry)


class Session:
    def __init__(self, handlers):
        """
        persistence in session process is a bad idea.
        it should be in cache expire or use persistence store directly
        :param handlers:
        :return:
        """
        self.store = handlers
        pass

    def initialize(self, web):

        curr = web.get_cookie('sid')

        if curr:
            self._session_id = curr

            cache_ip = self.get('remote_ip')

            if cache_ip:
                if web.request.remote_ip != str(cache_ip):
                    raise RemoteIPExpection

            else:
                # user alive too long
                self.store.set_session(self._session_id, 'remote_ip', web.request.remote_ip)


        else:
            self._session_id = self.generate_sid()
            web.set_cookie('sid', self._session_id)
            self.store.set_session(self._session_id, 'remote_ip', web.request.remote_ip)

        self.web = web

        return self


    def generate_sid(self):
        return str(uuid1())


    def get(self, key, default=None, *args, **kwargs):
        curr = self.store.get_session(self._session_id, key)
        if not curr:
            if default:
                self.store.set_session(self._session_id, key, default)
            return default
        return curr

    def set(self, key, value):
        return self.store.set_session(self._session_id, key, value)

    def delete(self, *keys):
        return self.store.delete_session_item(self._session_id, *keys)

    def clear(self):
        self.store.delete_session(self._session_id)


    @property
    def session_id(self):
        return self._session_id




