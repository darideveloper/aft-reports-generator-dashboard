## Context

The events app has an access page at `events/<slug>/access/` that shows a countdown to the event and an invitation link button (visible within 1 hour of start). The `Event` model stores `event_datetime` (timezone-aware, `USE_TZ=True`) and `duration_minutes`. The project timezone is `America/Mexico_City`.

Currently there is no mechanism for users to add the event to their personal calendar — they would have to manually copy the date/time.

## Goals / Non-Goals

**Goals:**
- Render three "Add to Calendar" buttons on the access page when `event.event_datetime` is set
- Google Calendar button opens a pre-filled event creation URL
- Microsoft Outlook button opens a pre-filled event creation URL
- Apple Calendar button downloads a valid `.ics` file
- Each button includes its platform's SVG icon
- Calendar entries include the event's `invitation_link` (Zoom, Meet, etc.) as the location, so users can join directly from their calendar
- All dates use UTC for interchange; the `ctz` parameter tells Google the event's local timezone
- Only modify the events app (no cross-app changes)

**Non-Goals:**
- No model changes or migrations
- No new Python dependencies (standard library + Django only)
- No changes to the registration form (`events/form.html`) or email templates
- No calendar subscription feeds (`webcal://`) — just single-event add
- No Yahoo or other calendar providers

## Decisions

### 1. Server-side URL generation vs client-side JavaScript
**Decision**: Server-side Python in `views.py` helper functions.

Python has `datetime` + `zoneinfo`/`pytz` for reliable timezone math. Constructing URLs in the view context is testable via Django's test client. Client-side JS would require duplicating timezone logic and `.ics` generation in the browser, which is more fragile.

### 2. `.ics` served via dedicated view vs inline data URI
**Decision**: Dedicated Django view `EventCalendarIcsView` at `events/<slug>/ics/`.

Data URIs for `.ics` files work poorly on iOS Safari (where Apple Calendar integrations matter most). A real endpoint returns proper `Content-Type: text/calendar` and `Content-Disposition: attachment` headers, ensuring the OS correctly associates the file with Calendar.app.

### 3. `.ics` generation: icalendar library vs manual string
**Decision**: Manual string construction.

The standard library `email` and `calendar` packages plus basic string formatting cover the ~15 lines needed. Adding `icalendar` as a project dependency for a single event with no recurrence, alarms, or attendees is unnecessary weight (YAGNI).

### 4. Button icons: SVG inline vs image files
**Decision**: Inline SVG in the template.

No extra HTTP requests, works offline, no asset pipeline changes. Each platform's icon is ~1-2KB of SVG. The icons are simple, well-known logos (Google Calendar colored G, Outlook envelope, Apple Calendar).

### 5. Button placement on the page
**Decision**: Below the invitation link CTA, in a row. They supplement the main "join event" action rather than competing with it.

### 6. Timezone handling
**Decision**: Convert `event.event_datetime` to UTC for all three calendar formats. For Google Calendar, additionally pass `ctz=America/Mexico_City` so the event displays in the user's local time. This matches the project's `TIME_ZONE` setting.

### 7. Including invitation_link as calendar location
**Decision**: Include `event.invitation_link` (Zoom, Meet, etc.) as the `location` parameter in Google Calendar and Microsoft Outlook URLs, and as the `LOCATION` property in `.ics` files.

The `invitation_link` is the core join mechanism — without it in the calendar entry, users would add the event to their calendar but still need to return to the access page to find the join link. If `invitation_link` is not set, the location is simply omitted from all formats.

## Risks / Trade-offs

- **Risk**: `.ics` content with CRLF line endings might render incorrectly on some clients. **Mitigation**: Use `\r\n` per RFC 5545.
- **Risk**: `.ics` text values (`SUMMARY`, `LOCATION`) containing characters `;`, `\`, `,`, or newlines would produce invalid iCalendar. **Mitigation**: Escape with backslash (`\;`, `\\`, `\,`, `\n`) per RFC 5545 §3.3.11 before inserting into the `.ics` template.
- **Risk**: Microsoft URL format may differ for outlook.com vs Office 365 vs desktop Outlook. **Mitigation**: Use the Office 365 deeplink format, which redirects appropriately for the user's account type.
- **Risk**: Very long event titles could break URL length limits. **Mitigation**: Google/MS URLs stay well under the ~2000 char limit for typical use. No URL shortening needed.
- **Risk**: Icons increase page size. **Mitigation**: Minified inline SVGs add ~4KB total across 3 icons — negligible.
- **Trade-off**: Apple Calendar requires a download step (the `.ics` file) rather than a direct link. This is inherent to the platform (Apple has no web-based calendar creation URL).
