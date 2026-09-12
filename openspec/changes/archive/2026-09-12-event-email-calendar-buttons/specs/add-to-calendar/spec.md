## ADDED Requirements

### Requirement: Calendar builders reused for email with absolute ICS URL
The system SHALL reuse `_build_google_calendar_url`, `_build_microsoft_calendar_url`, and `_build_ics_content` for email rendering without duplicating date logic. The email SHALL use an absolute ICS download URL built with `reverse("events:event-ics")` + `_resolve_absolute_url`. Existing access-page buttons and ICS endpoint behavior SHALL remain unchanged.

#### Scenario: Email context reuses builder output
- **WHEN** `send_event_emails()` runs for an event with `event_datetime` set
- **THEN** the template context `google_url` equals `_build_google_calendar_url(event)`, `microsoft_url` equals `_build_microsoft_calendar_url(event)`, and `ics_absolute_url` is an absolute URL (`http://` when `DEBUG=True`, otherwise `https://`) containing `/ics/`

#### Scenario: Access page and ICS endpoint unchanged
- **WHEN** the access page or `<slug>/ics/` endpoint is requested after this change
- **THEN** responses match pre-change behavior (relative `ics_url` on access page still valid, endpoint headers and body unchanged)
