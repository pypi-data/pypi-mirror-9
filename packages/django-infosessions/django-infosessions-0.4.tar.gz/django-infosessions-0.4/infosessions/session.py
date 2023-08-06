# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from redis.exceptions import RedisError

from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.backends.db import Session as DataBaseSession, SessionStore as DataBaseStore
from django_redis import get_redis_connection
from django.utils import timezone


from .settings import PREFIX, USE_FALLBACK
from .constants import DATA_KEY, GLOBAL_PREFIX

logger = logging.getLogger(__name__)


class SessionStore(SessionBase):
    """
    Implements Redis session store.
    Forked from: https://github.com/martinrusev/django-redis-sessions
    """

    @classmethod
    def clear_expired(cls):
        # clear_expired is no-op and is done by redis
        if USE_FALLBACK:
            logger.info('clearing expired DB sessions')
            DataBaseStore.clear_expired()
        return True

    def __init__(self, session_key=None, prefix=PREFIX):
        super(SessionStore, self).__init__(session_key)
        self.server = get_redis_connection()
        self.prefix = prefix

    def load_db(self):
        try:
            s = DataBaseSession.objects.get(
                session_key=self.session_key,
                expire_date__gt=timezone.now()
            )
            logger.info('fallback successful')
            # noinspection PyAttributeOutsideInit
            self._session_cache = self.decode(s.session_data)
            self.save()
            return self._session_cache
        except (DataBaseSession.DoesNotExist, SuspiciousOperation) as e:
            logger.info('fallback failed: %s' % e)
            self.create()
            return {}

    def load_redis(self):
        logger.info('loading session from redis: %s' % self.session_key)
        try:
            session_data = self.server.get(
                self.redis_key(self.session_key)
            )
            return self.decode(force_unicode(session_data))
        except RedisError as e:
            logger.error('error while loading session %s: %s' % (self.session_key, e))
            self.create()
            return {}

    def load(self):
        if USE_FALLBACK and not self.exists(self.session_key):
            return self.load_db()
        return self.load_redis()

    def exists(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        return self.server.exists(self.get_redis_key(session_key, self.prefix))

    def create(self):
        logger.info('creating session')
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        logger.info('saving session')
        if must_create and self.exists(self._get_or_create_session_key()):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        self.server.setex(
            self.get_redis_key(self._get_or_create_session_key(), self.prefix),
            self.get_expiry_age(),
            data
        )

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.delete_session(session_key, conn=self.server, prefix=self.prefix)
            from .models import SessionInfo
            SessionInfo.objects.filter(key=session_key, prefix=self.prefix).update(active=False)
        except Exception as e:
            logger.warning(e)

    @classmethod
    def delete_session(cls, session_key, conn=None, prefix=PREFIX):
        logger.info('deleting session %s' % session_key)
        if USE_FALLBACK:
            DataBaseStore(session_key).delete()
        if conn is None:
            conn = get_redis_connection()
        return conn.delete(cls.get_redis_key(session_key, prefix))

    @staticmethod
    def get_redis_key(session_key, prefix=PREFIX):
        """Return the real key name in redis storage
        @return string
        """
        return ':'.join([prefix, GLOBAL_PREFIX, DATA_KEY, session_key])

    def redis_key(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        return self.get_redis_key(session_key, self.prefix)
