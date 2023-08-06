# -*- coding: utf-8 -*-
"""The tgapp-calendarevents package"""

import tg
from calendarevents.lib.event_type import EventType
import partials


def plugme(app_config, options):
    app_config['_calendarevents'] = options
    return dict(appid='calendarevents', global_helpers=False)

