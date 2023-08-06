About calendarevents
--------------------

calendarevents is a Pluggable calendars and events application for TurboGears2.
It permits to create events which are associated to entities defined inside the
application which plugs it in.

Calendarevents provides support for multiple calendars and event types, by defining
new event types it is possible to define how the event relates to external entities
like a blog post that describes it.

When displaying events if available weather informations for the day and location
of the event will be provided.

Installing
----------

calendarevents can be installed both from pypi or from bitbucket::

    easy_install tgapp-calendarevents

should just work for most of the users

Plugging calendarevents
-----------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with calendarevents::

    plug(base_config, 'calendarevents', event_types=[...])

At least one event type must be defined inside the *event_types* argument.
Defining event types is explained inside the Event Types section.

You will be able to access the calendars at
*http://localhost:8080/calendarevents*.

Event Types
-----------

calendarevents needs the application to define at least one EventType to work.

Event types must be defined inheriting from the ``calendarevents.EventType`` class,
for example to define an event for a concert which relates to a blog article that
describes the concert itself::

    from tw2.core.js import js_function
    from tw2.core.resources import JSLink, CSSLink

    class Concert(EventType):
        name = 'Concert'
        resources = [
            JSLink(modname='calendarevents.public', filename='js/calendarevents.js'),
            CSSLink(modname='calendarevents.public', filename='css/fullcalendar.css')
        ]
        events = {'eventClick': js_function('calendarevents.eventClick'),
                  'dayClick': js_function('calendarevents.dayClick')}

        def get_linkable_entities(self, calendar):
            return [(a.uid, a.title) for a in model.DBSession.query(model.Article)]

        def get_linked_entity_info(self, event):
            return model.DBSession.query(model.Article).get(event.linked_entity_id).title

        def get_linked_entity_url(self, event):
            return tg.url('/blog/view/%s' % event.linked_entity_id)

    plug(base_config, 'calendarevents', event_types=[Concert()])

Event types can also specify some additional options to change the calendevents 
behavior. If the ``EventType`` specifies ``force_redirect = True`` as a class
property whenever the event page is opened the user gets redirected to the
linked entity url.
``EventType`` can also update the calendar informations be exposing a
``calendar_data(self, event) -> dict`` method that can return any
additional information for the event (for example it can mark the
event as allDay or not).

``resources`` are required only if you want to use js_hooks for fullcalendar events.
``resources`` should be a list of toscaWidget injected resources,

``events`` are the injected js methods for overriding js_hooks.

js_hooks
--------

If you want to use js_hooks you must inject resource in your event type, see prior section.
for now supported events for the js_hooks are ``eventClick`` and ``dayClick``.

The .js hook script can follow this example::

    (function(w) {
      w.calendarevents = {
        eventClick: function(base_url, event, view) {
          window.location.href = base_url+event.uid;
        },
        dayClick: function(base_url, date, allDay, view) {
        }
      };
    })(window);

note: if you inject js_hooks you replace the default behavior

Exposed Partials
----------------

calendarevents exposes a partial to render event boxes inside other pages:

* calendarevents.partials:event(event) - Renders an event box

Calendar Partial
----------------

``calendarevents.partials:calendar(cal, view='month', all_day_slot=False, start_from=datetime.utcnow())``

The calendar partial expose a partial with just a calendar, parameters accepted are:

* ``cal`` -> (required) the calendar object, for now the js events are managed only by the ``event_type`` assigned to
    that calendar
* ``event_sources`` -> a dictionary in the following format::

    {'event_sources': [{'events': availability_events_list,
                        'color': 'Blue',
                        'text_color': ''},
                       {'events': occupation_events_list,
                        'color': 'Red',
                        'text_color': ''}]}

  ``color`` and ``text_color`` are optional, ``events`` should be a list of ``event.calendar_data`` property, if you did
  not provide this, events are taken from ``cal`` object
* ``start_from`` -> (datetime) starting calendar date
* ``view`` -> (String)  (default value "month") type of the calendar view (``month``, ``basicWeek``, ``basicDay``,
  ``agendaWeek``, ``agendaDay``)
* ``all_day_slot`` -> (Bool) (default value: False) Event slot are displayed for all day or for the real time slot
* ``slot_minutes`` -> (Int) (default value: 15) Minutes slot duration
* ``first_hour`` -> (Int) (default value: 8) First hour displayed
* ``time_format`` -> (String) (default value: "HH:mm"), the display format for time
* ``column_format`` -> (String) (default value: "d/M"), the display format for column date

Utils
-----

inside ``calendarvents.lib.utils`` you can find a bunch of utils to view and manage events and calendar:

* **create_calendar(name, events_type)** - create a new calendar, events_type should be a string
* **get_calendar(calendar_id)** - retrieve the ``calendar`` for the given ``calendar_id``
* **create_event(cal, name, summary, datetime, location, linked_entity_type, linked_entity_id, end_time)** - create a
  new ``calendar_event``
* **get_event(event_id)** - retrieve the ``calendar_event`` for the given ``event_id``
* **get_calendar_events_from_datetime(calendar, start_time, active)** retrieve all the active ``calendar_event`` for
  the given calendar starting from the given ``start_time``
* **get_calendar_day_events(calendar, start_time, active)** retrieve all the active ``calendar_event`` for the given
  calendar and the given ``start_time``
* **get_calendar_events_in_range(calendar, start_time, end_time, active)** - retrieve all the active ``calendar_event``
  for the given calendar and the given range of time (``start_time`` - ``end_time``)
* **deactivate_event(event_id)** - deactivate a ``calendar_event``, by default standard get event utils retrieve only
  active events
* **activate_event(event_id)** - put the ``calendar_event`` in active state
