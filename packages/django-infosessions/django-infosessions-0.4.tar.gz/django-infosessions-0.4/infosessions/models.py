# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib

from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text

from .settings import INFO_PREFIX, INFO_TIMEOUT, PREFIX
from .session import SessionStore, DataBaseStore
from .constants import MAX_KEY_LENGTH, MAX_PREFIX_LENGTH, GLOBAL_PREFIX, INFO_KEY, DEFAULT_PREFIX, INFO_EXIST_VALUE


class SessionInfo(models.Model):
    """
    Session-related information
    """
    user = models.ForeignKey(get_user_model(), related_name='sessions', db_index=True, verbose_name=_('User'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    key = models.CharField(max_length=MAX_KEY_LENGTH, db_index=True, verbose_name=_('Key'))
    prefix = models.CharField(max_length=MAX_PREFIX_LENGTH, db_index=True, default=DEFAULT_PREFIX)
    active = models.BooleanField(default=True)

    # additional request data
    user_ip = models.IPAddressField(default='127.0.0.1')
    user_agent = models.TextField(null=True, default=None, blank=True)

    # auto-generated data on .save()
    user_agent_md5 = models.CharField(max_length=32, default=None, null=True, blank=True)

    @classmethod
    def get_key(cls, session_key):
        return ':'.join([INFO_PREFIX, GLOBAL_PREFIX, INFO_KEY, session_key])

    @classmethod
    def key_exists(cls, session_key):
        """
        If session info exists with that session_key, returns True
        """
        key = cls.get_key(session_key)
        conn = get_redis_connection()
        return conn.exists(key)

    @staticmethod
    def exists(request):
        return SessionInfo.key_exists(request.session.session_key)

    @classmethod
    def gen(cls, request):
        """
        Generate Session model from request
        """
        session = SessionInfo(user=request.user, key=request.session.session_key)

        # additional request data processing
        session.user_ip = request.META.get('REMOTE_ADDR')
        session.user_agent = force_text(request.META.get('HTTP_USER_AGENT'), errors='replace')

        return session

    @classmethod
    def record(cls, request, prefix=PREFIX):
        """
        Record session info from request
        """
        session_key = request.session.session_key
        try:
            session = cls.gen(request)
            session.prefix = prefix
            session.save()
        except IntegrityError:
            # session info is already in database
            pass
        conn = get_redis_connection()
        conn.setex(cls.get_key(session_key), INFO_TIMEOUT, INFO_EXIST_VALUE)

    def erase(self):
        self.active = False
        SessionStore(self.key, self.prefix).delete()
        self.save()

    def session_exists(self):
        return SessionStore(self.key, self.prefix).exists()
    session_exists.boolean = True

    def session_exists_db(self):
        return DataBaseStore().exists(self.key)
    session_exists_db.boolean = True

    def session_data(self):
        s = SessionStore(self.key, self.prefix)
        if s.exists(self.key):
            return s.load()
        if self.session_exists_db():
            return DataBaseStore(self.key).load()
        return _('Does not exist')

    def __unicode__(self):
        return '{user}'.format(user=self.user)

    def save(self, *args, **kwargs):
        if self.user_agent:
            self.user_agent_md5 = hashlib.md5(self.user_agent).hexdigest()
        super(SessionInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        unique_together = (('prefix', 'key'),)