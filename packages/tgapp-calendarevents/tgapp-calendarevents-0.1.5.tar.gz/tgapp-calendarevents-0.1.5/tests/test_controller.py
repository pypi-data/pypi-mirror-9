from tg import request
from tests.base import configure_app, create_app


class TestCalendareventsControllerTests(object):
    @classmethod
    def setupClass(cls):
        cls.app_config = configure_app()

    def setup(self):
        self.app = create_app(self.app_config, True)

    def test_index(self):
        resp = self.app.get('/')
        assert 'HELLO' in resp.text

    def test_calendarevents(self):
        resp = self.app.get('/calendarevents').follow(status=200)
        assert 'Calendars' in resp.text, resp

    def test_new_calendar(self):
        resp = self.app.get('/calendarevents/calendar/new')
        assert "Insert new calendar's details" in resp, resp

    def test_save_calendar(self):
        resp = self.app.post('/calendarevents/calendar/save',
                             params={'name': 'test_calendar1',
                                     'events_type': 'event_type'}).follow()
        assert 'Calendar successfully added' in resp, resp

    def test_view_calendar(self):
        self.test_save_calendar()
        resp = self.app.get('/calendarevents/calendar/1')
        assert 'test_calendar1' in resp, resp

    def test_view_calendar_wrong_view(self):
        self.test_save_calendar()
        resp = self.app.get('/calendarevents/calendar/1', params={'view': 'sbrollax'})
        assert 'test_calendar1' in resp, resp

    def test_view_calendar_events(self):
        self.test_save_calendar()
        resp = self.app.get('/calendarevents/calendar/events/1')
        assert 'test_calendar1' in resp, resp

    def test_new_event(self):
        self.test_save_calendar()
        resp = self.app.get('/calendarevents/event/new/1')
        assert "Insert new event's details" in resp, resp

    def test_create_event(self):
        self.test_save_calendar()
        self.app.get('/calendarevents').follow(status=200)
        resp = self.app.post('/calendarevents/event/create',
                             params={'cal': 1,
                                     'name': 'test_event1',
                                     'summary': 'summary_test',
                                     'datetime': '2020-03-01 01:01',
                                     'location': 'torino',
                                     'linked_entity': 1}).follow()
        assert "Event successfully added" in resp, resp

    def test_edit_event(self):
        self.test_create_event()
        resp = self.app.get('/calendarevents/event/edit/1')
        assert "value=\"1\"" in resp, resp

    def test_view_event(self):
        self.test_create_event()
        resp = self.app.get('/calendarevents/event/1')
        assert 'test_event1' in resp, resp

    def test_save_event(self):
        self.test_create_event()
        self.app.get('/calendarevents/event/edit/1')
        resp = self.app.post('/calendarevents/event/save',
                             params={'cal': 1,
                                     'event': 1,
                                     'name': 'test_event2',
                                     'summary': 'summary_test2',
                                     'datetime': '2020-04-01 01:01',
                                     'location': 'torino',
                                     'linked_entity': 1}).follow()
        assert 'Event successfully modified' in resp, resp

    def test_save_event_nonexisting_event(self):
        self.test_create_event()
        self.app.get('/calendarevents/event/edit/1')
        resp = self.app.post('/calendarevents/event/save',
                             params={'cal': 1,
                                     'event': 30,
                                     'name': 'test_event2',
                                     'summary': 'summary_test2',
                                     'datetime': '2020-04-01 01:01',
                                     'location': 'torino',
                                     'linked_entity': 1}, status=404)
        assert 'The resource could not be found' in resp, resp

