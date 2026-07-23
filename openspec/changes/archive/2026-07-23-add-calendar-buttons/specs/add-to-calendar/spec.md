## ADDED Requirements

### Requirement: Google Calendar link generation
The system SHALL generate a pre-filled Google Calendar event creation URL from an Event's title, datetime, duration, and `invitation_link`. The URL SHALL use UTC dates with the `ctz` parameter set to `settings.TIME_ZONE`.

#### Scenario: Google Calendar URL contains correct params
- **WHEN** an Event has `title="Conferencia"`, `event_datetime=2024-03-15T16:00:00-06:00`, `duration_minutes=120`, and `invitation_link="https://zoom.us/j/123"`
- **THEN** the generated URL SHALL contain `action=TEMPLATE`, `text=Conferencia`, `location` set to the invitation link, `ctz=America/Mexico_City`, and dates in `YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ` format

#### Scenario: Google Calendar URL omits location when no invitation_link
- **WHEN** an Event has `invitation_link=None`
- **THEN** the generated Google Calendar URL SHALL NOT contain a `location` parameter

### Requirement: Microsoft Outlook link generation
The system SHALL generate a pre-filled Outlook.com/Office 365 event creation URL from an Event's title, datetime, duration, and `invitation_link`.

#### Scenario: Outlook URL contains correct params
- **WHEN** an Event has `title="Conferencia"`, `event_datetime=2024-03-15T16:00:00-06:00`, `duration_minutes=120`, and `invitation_link="https://zoom.us/j/123"`
- **THEN** the generated URL SHALL contain `subject=Conferencia`, `location` set to the invitation link, `startdt` and `enddt` in ISO 8601 format, and `path=/calendar/action/compose`

#### Scenario: Outlook URL omits location when no invitation_link
- **WHEN** an Event has `invitation_link=None`
- **THEN** the generated Outlook URL SHALL NOT contain a `location` parameter

### Requirement: Apple Calendar .ics download
The system SHALL provide a downloadable `.ics` file (RFC 5545) for an Event when accessed at `events/<slug>/ics/`. The `.ics` SHALL include the event's `invitation_link` as the `LOCATION` property when set. Text values (`SUMMARY`, `LOCATION`) SHALL escape the characters `\`, `;`, `,`, and literal newlines with a backslash per RFC 5545. The `UID` SHALL use the format `{event.slug}@aft-dashboard`. When `duration_minutes` is `0` or `None`, `DTEND` SHALL equal `DTSTART`.

#### Scenario: .ics endpoint returns valid file with location
- **WHEN** a GET request is made to `events/<slug>/ics/` for a valid active Event with `event_datetime`, `duration_minutes`, and `invitation_link` set
- **THEN** the response SHALL have `Content-Type: text/calendar`, `Content-Disposition: attachment; filename="<slug>.ics"`, and body containing `BEGIN:VCALENDAR`, `DTSTART`, `DTEND`, `SUMMARY`, `UID` (format `{slug}@aft-dashboard`), `LOCATION` with the invitation link, and `END:VCALENDAR`

#### Scenario: .ics escapes special characters in text values
- **WHEN** an Event has `title="Evento; Especial, Edición 2024"` containing the characters `;`, `\,` and `,`
- **THEN** the `.ics` `SUMMARY` property SHALL escape `;` as `\;`, `\` as `\\`, and `,` as `\,`

#### Scenario: .ics uses DTEND=DTSTART when duration_minutes is zero
- **WHEN** an Event has `duration_minutes=0`
- **THEN** the `.ics` `DTEND` SHALL equal `DTSTART`

#### Scenario: .ics file omits location when no invitation_link
- **WHEN** a GET request is made to `events/<slug>/ics/` for an Event with `invitation_link=None`
- **THEN** the `.ics` body SHALL NOT contain a `LOCATION` property

#### Scenario: .ics endpoint returns 404 for event without datetime
- **WHEN** a GET request is made to `events/<slug>/ics/` for an Event with `event_datetime=None`
- **THEN** the response SHALL be 404

#### Scenario: .ics endpoint returns 404 for inactive event
- **WHEN** a GET request is made to `events/<slug>/ics/` for an Event with `is_active=False`
- **THEN** the response SHALL be 404

### Requirement: Calendar buttons render with platform icons
The access page SHALL render three buttons (Google Calendar, Outlook, Apple Calendar) when the Event has an `event_datetime`. Each button SHALL include its platform's SVG icon. The Google and Outlook buttons SHALL use `target="_blank"` to open in a new tab. The Apple Calendar button SHALL use the `download` attribute to trigger a file download.

#### Scenario: Three buttons visible on access page with correct behavior
- **WHEN** the access page is rendered for an Event with `event_datetime` set
- **THEN** the page SHALL contain three anchor elements: Google Calendar (with `target="_blank"`), Outlook (with `target="_blank"`), and Apple Calendar (with `download` attribute), each with an SVG icon

#### Scenario: No buttons when event_datetime is None
- **WHEN** the access page is rendered for an Event with `event_datetime=None`
- **THEN** the page SHALL NOT contain the calendar buttons

### Requirement: Timezone correctness
All calendar URLs and `.ics` files SHALL use UTC dates. The `ctz` parameter on the Google Calendar URL SHALL equal `settings.TIME_ZONE`.

#### Scenario: UTC dates in generated URLs
- **WHEN** an Event has `event_datetime` in `America/Mexico_City` timezone
- **THEN** the Google and Outlook URLs and `.ics` SHALL contain the corresponding UTC date (e.g., `16:00 CST` → `22:00Z`)
