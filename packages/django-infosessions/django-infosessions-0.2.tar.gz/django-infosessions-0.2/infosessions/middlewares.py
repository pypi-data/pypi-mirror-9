# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from .models import SessionInfo

logger = logging.getLogger(__name__)


class SessionSyncMiddleware(object):
    @staticmethod
    def process_response(request, response):
        if hasattr(request, 'user') and request.user.is_authenticated() and not SessionInfo.exists(request):
            SessionInfo.record(request)
        return response