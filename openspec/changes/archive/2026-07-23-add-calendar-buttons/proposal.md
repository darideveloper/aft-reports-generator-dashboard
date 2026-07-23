## Why

Event registrants currently see a countdown and invitation link on the access page, but have no way to save the event to their personal calendar. This forces them to manually copy dates or risk forgetting the event. Adding "Add to Calendar" buttons (Google, Outlook, Apple) improves the user experience and increases event attendance by letting users book the event with one click.

## What Changes

- Add three "Add to Calendar" buttons on the `events/<slug>/access/` page, each with its platform icon:
  - **Google Calendar** — link to `calendar.google.com/render?action=TEMPLATE`
  - **Microsoft Outlook** — link to `outlook.office.com/calendar/0/deeplink/compose`
  - **Apple Calendar** — download a generated `.ics` file
- The event's `invitation_link` (Zoom, Meet, etc.) is included as the location link in all three calendar formats so users can join directly from their calendar
- Add a new Django view `EventCalendarIcsView` that serves the `.ics` file at `events/<slug>/ics/`
- Add helper functions in `events/views.py` to build calendar URLs and `.ics` content, using `settings.TIME_ZONE` for timezone
- Calendar buttons only render when `event.event_datetime` is set
- All dates are converted to UTC for calendar formats; `ctz` parameter preserves the local timezone for display

## Capabilities

### New Capabilities
- `add-to-calendar`: Generate platform-specific calendar links (Google, Microsoft) and `.ics` file downloads from an `Event`'s datetime and duration, rendered as icon-labeled buttons on the access page.

### Modified Capabilities

None.

## Impact

- `events/views.py` — add `EventCalendarIcsView` class + 3 helper functions
- `events/urls.py` — add `ics/` route
- `events/templates/events/access.html` — add calendar buttons section with SVG icons
- `events/tests.py` — add tests for new view, helpers, and template rendering
- No new dependencies, no model changes, no migrations
