from datetime import datetime
import json
from tg import expose, validate
import tg
from tgext.datahelpers.utils import fail_with
from tgext.datahelpers.validators import SQLAEntityConverter
from calendarevents import model
from calendarevents.model import DBSession


@expose('calendarevents.templates.partials.event')
def event(event):
    return dict(calendar_event=event)


@validate(dict(cal=SQLAEntityConverter(model.Calendar)),
          error_handler=fail_with(404))
@expose('calendarevents.templates.partials.calendar')
def calendar(cal, event_sources=None, start_from=datetime.utcnow(), view='month', all_day_slot=False, slot_minutes=15,
             first_hour=8, column_format="d/M", time_format="HH:mm"):
    if event_sources is None:
        event_sources = {'event_sources': [{'events': cal.active_events_calendar_data}]}

    if view not in ('month', 'basicWeek', 'basicDay', 'agendaWeek', 'agendaDay'):
        view = 'month'

    for res in cal.events_type_info.resources:
        res.inject()

    return dict(cal=cal, values=tg.json_encode(event_sources), start_from=start_from, view=view,
                all_day_slot=all_day_slot,  slot_minutes=slot_minutes, first_hour=first_hour,
                column_format=column_format, time_format=time_format)
