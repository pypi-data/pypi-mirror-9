(function(w) {
  w.calendarevents = {
    eventClick: function(base_url, event, view) {
      window.location.href = base_url+event.uid;
    },
    dayClick: function(base_url, date, allDay, view) {
    }
  };
})(window);
