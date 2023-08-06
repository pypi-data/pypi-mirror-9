from datetime import datetime as dt
from sqlalchemy import or_
from calendarevents import model


def create_calendar(name, events_type):
    new_calendar = model.Calendar(name=name, events_type=events_type)
    model.DBSession.add(new_calendar)
    return new_calendar


def get_calendar(calendar_id):
    return model.DBSession.query(model.Calendar).get(calendar_id)


def create_event(cal, name, summary, datetime, location, linked_entity_type, linked_entity_id, end_time=None):
    new_event = model.CalendarEvent(calendar_id=cal.uid, name=name,
                                    summary=summary, datetime=datetime,
                                    end_time=end_time,
                                    location=location,
                                    linked_entity_type=linked_entity_type,
                                    linked_entity_id=linked_entity_id,
                                    active=True)
    model.DBSession.add(new_event)
    return new_event


def get_event(event_id):
    return model.DBSession.query(model.CalendarEvent).get(event_id)


def get_calendar_events_from_datetime(calendar, start_time, active=True):
    return get_calendar_events_in_range(calendar, start_time, active=active)


def get_calendar_day_events(calendar, start_time, active=True):
    return get_calendar_events_in_range(calendar, start_time, start_time, active=active)


def get_calendar_events_in_range(calendar, start_time, end_time=None, active=True):
    """Retrieves events in range of datetimes.

    When ``start_time`` and ``end_time`` coincide it will get the events
    for that day.

    When ``end_time`` is ``None`` it will retrieve all the events
    starting from ``start_time``.

    """
    if start_time == end_time:
        start_time = dt.combine(start_time.date(), dt.min.time())
        end_time = dt.combine(start_time.date(), dt.max.time())

    q = model.DBSession.query(model.CalendarEvent).filter(
        model.CalendarEvent.active == active,
        model.CalendarEvent.calendar_id == calendar,
        or_(model.CalendarEvent.datetime >= start_time, model.CalendarEvent.end_time > start_time)
    )

    if end_time is not None:
        q = q.filter(model.CalendarEvent.datetime <= end_time)
    return q.order_by(model.CalendarEvent.datetime)


def deactivate_event(event_id):
    event = get_event(event_id)
    event.deactivate()


def activate_event(event_id):
    event = get_event(event_id)
    event.activate()
