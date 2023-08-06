import tg
from tw2.core.js import js_function
from tw2.core.resources import JSLink, CSSLink


class EventType(object):
    name = 'Unknown'
    resources = [
        JSLink(modname='calendarevents.public', filename='js/calendarevents.js'),
        CSSLink(modname='calendarevents.public', filename='css/fullcalendar.css')
    ]
    events = {'eventClick': js_function('calendarevents.eventClick'),
              'dayClick': js_function('calendarevents.dayClick')}

    def get_linkable_entities(self, calendar):
        raise NotImplementedError

    def get_linked_entity_url(self, event):
        return NotImplementedError

    def get_linked_entity_info(self, event):
        return NotImplementedError


def lookup_event_type(name):
    event_types = tg.config['_calendarevents']['event_types']
    for et in event_types:
        if et.name == name:
            return et
    return None
