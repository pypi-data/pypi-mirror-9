# -*- coding: utf-8 -*-
# Copyright (c) 2015 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import

import zlib

from graypy.handler import GELFHandler as BaseGELFHandler


class _CompressHandler(object):
    def makePickle(self, record):
        return zlib.compress(record.msg.encode('utf-8'))


class GELFHandler(_CompressHandler, BaseGELFHandler):
    pass
