from sqlalchemy import Table, ForeignKey, Column, Boolean
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from calendarevents.model import DeclarativeBase
from calendarevents.lib.event_type import lookup_event_type
from calendarevents.lib.weather import get_weather_for_date

from tg.decorators import cached_property


class Calendar(DeclarativeBase):
    __tablename__ = 'calendarevents_calendar'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    events_type = Column(Unicode(64), index=True)

    @property
    def events_type_info(self):
        return lookup_event_type(self.events_type)

    @property
    def linkable_entities(self):
        event_type = self.events_type_info
        if not event_type:
            return []
        return event_type.get_linkable_entities(self)

    def events_in_range(self, start_date, end_date, active=True):
        from calendarevents.lib.utils import get_calendar_events_in_range
        return get_calendar_events_in_range(self.uid, start_date, end_date, active=active)

    @property
    def active_events(self):
        return [e for e in self.events if e.active]

    @property
    def active_events_calendar_data(self):
        return [e.calendar_data for e in self.events if e.active]

class CalendarEvent(DeclarativeBase):
    __tablename__ = 'calendarevents_event'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    summary = Column(Unicode(1024))
    datetime = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, index=True)
    location = Column(Unicode(255), nullable=False)
    active = Column(Boolean, index=True, default=True)

    calendar_id = Column(Integer, ForeignKey(Calendar.uid), nullable=False, index=True)
    calendar = relation(Calendar, backref=backref('events', order_by='CalendarEvent.datetime.desc()',
                                                  cascade='all, delete-orphan'))

    linked_entity_id = Column(Integer, nullable=False, index=True)
    linked_entity_type = Column(Unicode(255), nullable=False, index=True)

    @property
    def calendar_data(self):
        data = {'uid': self.uid, 'title': self.name, 'start': self.datetime,
                'linked_entity_info': self.linked_entity_info}

        if self.end_time:
            data['end'] = self.end_time
            data['allDay'] = False

        event_type = self.event_type
        if event_type is not None and hasattr(event_type, 'calendar_data'):
            data.update(event_type.calendar_data(self))

        return data

    @property
    def event_type(self):
        return lookup_event_type(self.linked_entity_type)

    @property
    def linked_entity_url(self):
        return self.event_type.get_linked_entity_url(self)

    @property
    def linked_entity_info(self):
        return self.event_type.get_linked_entity_info(self)

    @cached_property
    def weather(self):
        return get_weather_for_date(self.location, self.datetime)

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True