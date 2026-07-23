## ADDED Requirements

### Requirement: Event Access Gate Page
The system SHALL expose a public Django-rendered page at `/events/<slug>/access/` that validates the event date/time and decides whether to redirect to the invitation link, show a countdown, or show an "event ended" message.

#### Scenario: Access page redirects to invitation link when within 1 hour
- **WHEN** a lead clicks the access URL for an event where `now + 1 hour >= event_datetime` and `now < event_datetime + duration_minutes`
- **THEN** the server returns an HTTP 302 redirect to the event's `invitation_link`

#### Scenario: Access page shows countdown when more than 1 hour before event
- **WHEN** a lead clicks the access URL for an event where `now + 1 hour < event_datetime`
- **THEN** the server renders an HTML page showing event title, event datetime, time remaining, and a countdown timer
- **AND** no invitation link or CTA button is visible on the page

#### Scenario: Access page shows "Evento finalizado" when event has ended
- **WHEN** a lead clicks the access URL for an event where `now >= event_datetime + duration_minutes`
- **THEN** the server renders an HTML page showing "Este evento ya ha finalizado" or equivalent message
- **AND** the invitation link is not revealed

#### Scenario: Access page returns 404 when invitation_link is missing
- **WHEN** a lead clicks the access URL for an event where `invitation_link` is NULL or empty
- **THEN** the server returns HTTP 404

#### Scenario: Access page returns 404 when event_datetime is missing
- **WHEN** a lead clicks the access URL for an event where `event_datetime` is NULL
- **THEN** the server returns HTTP 404

### Requirement: Countdown Timer Reveals Button on Completion
The access page SHALL include a client-side countdown that updates every second and reveals a clickable "Acceder al evento" button when the countdown reaches zero. The button SHALL link to the event's `invitation_link` with `target="_blank"` and `rel="noopener noreferrer"`.

#### Scenario: Countdown reaches zero and button appears
- **WHEN** the client-side countdown on the access page reaches 0 seconds remaining
- **THEN** the "Acceder al evento" button becomes visible and clickable
- **AND** the button's `href` equals the event's `invitation_link`
- **AND** the button has `target="_blank"` and `rel="noopener noreferrer"`

#### Scenario: Countdown renders correctly without JavaScript
- **WHEN** a lead accesses the countdown page with JavaScript disabled
- **THEN** the page displays the event title, event datetime, and the time remaining as server-rendered text
- **AND** no invitation link or CTA button is shown
- **AND** no script errors occur

### Requirement: All Datetime Comparisons Use Project Timezone
The system SHALL use `django.utils.timezone.now()` for all datetime comparisons, which respects the `TIME_ZONE = "America/Mexico_City"` setting. The `event_datetime` field SHALL be stored as a timezone-aware datetime in the database.

#### Scenario: Access check uses timezone-aware comparison
- **WHEN** a lead accesses the event access page at 2026-07-25 09:00:00 America/Mexico_City
- **AND** the event has `event_datetime = 2026-07-25 10:00:00 America/Mexico_City`
- **THEN** the server detects `now + 1 hour >= event_datetime` is true (09:00 + 1h = 10:00 >= 10:00)
- **AND** redirects to the invitation link

#### Scenario: Access check works across DST transitions
- **WHEN** the project timezone is America/Mexico_City and a DST transition occurs
- **THEN** all datetime comparisons use timezone-aware datetimes and correctly compute the time difference
