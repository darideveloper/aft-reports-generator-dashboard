## 1. Calendar URL helpers

- [x] 1.1 Add `_build_google_calendar_url(event)` in `events/views.py` — generates Google Calendar URL with `action=TEMPLATE`, `text`, `dates` (UTC `YYYYMMDDTHHMMSSZ`), `ctz` from settings, `location` from `invitation_link` (if set), `trp=false`. Use `urllib.parse.urlencode` for parameter encoding.
- [x] 1.2 Add `_build_microsoft_calendar_url(event)` in `events/views.py` — generates Outlook.com URL with `subject`, `startdt`/`enddt` (ISO 8601), `location` from `invitation_link` (if set), `path=/calendar/action/compose`, `rru=addevent`. Use `urllib.parse.urlencode` for parameter encoding.
- [x] 1.3 Add `_build_ics_content(event)` in `events/views.py` — builds RFC 5545 `.ics` string with CRLF, `DTSTART`/`DTEND`/`SUMMARY`/`UID`/`DTSTAMP`, and `LOCATION` from `invitation_link` (if set). `UID` uses format `{slug}@aft-dashboard`. Escape `;`, `\`, `,`, newlines in text values (`SUMMARY`, `LOCATION`) per RFC 5545. When `duration_minutes` is 0, `DTEND` equals `DTSTART`. All dates in UTC.

## 2. ICS download view

- [x] 2.1 Add `EventCalendarIcsView` (Django `View`) in `events/views.py` — `get(slug)` fetches active Event, returns `HttpResponse(content_type='text/calendar')` with `Content-Disposition: attachment`
- [x] 2.2 Add `path("<slug:slug>/ics/", EventCalendarIcsView.as_view(), name="event-ics")` to `events/urls.py`

## 3. Inject calendar URLs into access page context

- [x] 3.1 In `EventAccessView.get_context_data()`, generate `google_calendar_url`, `microsoft_calendar_url`, and `ics_url` when `event.event_datetime` is set, add them to context

## 4. Template: Calendar buttons with SVG icons

- [x] 4.1 Add calendar buttons section to `events/templates/events/access.html` — wrap in `{% if event.event_datetime %}`, three `<a>` tags with inline SVG icons for Google Calendar (`target="_blank"`), Outlook (`target="_blank"`), and Apple Calendar (`download` attribute)
- [x] 4.2 Style buttons with CSS to appear as a horizontal row below the invitation CTA, matching the existing design system

## 5. Tests

- [x] 5.1 Test `_build_google_calendar_url()` produces correct params, UTC dates, and includes `location` when `invitation_link` is set; omits `location` when None
- [x] 5.2 Test `_build_microsoft_calendar_url()` produces correct params, UTC dates, and includes `location` when `invitation_link` is set; omits `location` when None
- [x] 5.3 Test `_build_ics_content()` produces valid `.ics` with DTSTART/DTEND/SUMMARY/UID/LOCATION when `invitation_link` is set; omits LOCATION when None; DTEND equals DTSTART when `duration_minutes=0`; escapes `;`, `\`, `,` in SUMMARY and LOCATION
- [x] 5.4 Test `EventCalendarIcsView` returns correct content type, disposition, and filename
- [x] 5.5 Test `EventCalendarIcsView` returns 404 for events without datetime or inactive
- [x] 5.6 Test access page renders three calendar buttons with correct attributes when datetime is set: Google/MS have `target="_blank"`, Apple has `download`
- [x] 5.7 Test access page renders no calendar buttons when datetime is None
