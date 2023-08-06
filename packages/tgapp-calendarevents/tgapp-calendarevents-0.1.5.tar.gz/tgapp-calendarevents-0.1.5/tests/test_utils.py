import datetime
from calendarevents.lib import utils
from tests.base import configure_app, create_app


class TestCalendareventsUtilsTests(object):
    def test_create_calendar(self):
        calendar = utils.create_calendar('test_calendar1', 'event_type')
        assert calendar.name == 'test_calendar1'

    def test_get_calendar(self):
        self.test_create_calendar()
        calendar = utils.get_calendar(1)
        assert calendar.name == 'test_calendar1', calendar.name

    def test_create_event(self):
        self.test_create_calendar()
        calendar = utils.get_calendar(1)

        event = utils.create_event(calendar, 'event_test', 'event_summary', datetime.datetime(2020, 1, 1, 1, 3, 0),
                                   'torino', 'event_type', 1, end_time=None)
        assert event.name == 'event_test'

    def test_get_calendar_events_from_datetime(self):
        self.test_create_calendar()
        calendar = utils.get_calendar(1)
        start_time = datetime.datetime(2020, 1, 1, 1, 3, 0)
        self.test_create_event()
        events = utils.get_calendar_events_from_datetime(calendar.uid, start_time).all()
        assert len(events) > 0, len(events)