# -*- coding: utf-8 -*-
# Copyright (c) 2015 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import

from structlog._frames import _find_first_app_frame_and_name


def add_app_context(logger, method_name, event_dict):
    f, name = _find_first_app_frame_and_name(['logging', __name__])
    event_dict['file'] = f.f_code.co_filename
    event_dict['line'] = f.f_lineno
    event_dict['function'] = f.f_code.co_name
    return event_dict
