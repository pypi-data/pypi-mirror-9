# -*- coding: utf-8 -*-
# Copyright (c) 2015 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import

import logging
import os
import json
import socket

from graypy.handler import SYSLOG_LEVELS
from structlog.processors import JSONRenderer
from structlog.stdlib import _NAME_TO_LEVEL


STANDARD_GELF_KEYS = (
    'version',
    'host',
    'short_message',
    'full_message',
    'timestamp',
    'level',
)


def _get_gelf_compatible_key(key):
    if key in STANDARD_GELF_KEYS or key.startswith('_'):
        return key
    return '_{}'.format(key)


class GELFEncoder(JSONRenderer):
    def __init__(self, fqdn=True, localname=None,
                 gelf_keys=STANDARD_GELF_KEYS, **dumps_kw):
        if fqdn:
            host = socket.getfqdn()
        elif localname is not None:
            host = localname
        else:
            host = socket.gethostname()
        self.host = host
        self.gelf_keys = frozenset(gelf_keys)
        super(GELFEncoder, self).__init__(**dumps_kw)

    def _translate_non_gelf_keys(self, event_dict):
        return {
            _get_gelf_compatible_key(key): value
            for key, value in event_dict.items()
        }

    def __call__(self, logger, method_name, event_dict):
        event_dict = event_dict.copy()
        levelno = _NAME_TO_LEVEL[method_name]

        gelf_dict = {
            'version': '1.1',
            'host': self.host,
            'level': SYSLOG_LEVELS.get(levelno, levelno),
        }

        message = gelf_dict['short_message'] = event_dict.pop('event', '')

        if 'exception' in event_dict:
            exc = event_dict.pop('exception')
            gelf_dict['full_message'] = '\n'.join([message, exc])

        gelf_dict['_pid'] = os.getpid()
        gelf_dict['_logger'] = logger.name
        gelf_dict['_level_name'] = logging.getLevelName(levelno)

        gelf_dict.update(self._translate_non_gelf_keys(event_dict))

        return super(GELFEncoder, self).__call__(
            logger, method_name, gelf_dict)
