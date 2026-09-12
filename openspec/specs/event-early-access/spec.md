# event-early-access Specification

## Purpose
Defines how the events app reveals the per-event invitation link ahead of the start time via a configurable early-access window (`access_early_minutes`), governing the server-side access gate redirect and the countdown page button visibility.

## Requirements
### Requirement: Configurable early-access window

The system SHALL reveal the event invitation link `access_early_minutes` before `event_datetime`, where `access_early_minutes` is a per-`Event` non-negative integer in minutes defaulting to `30`. The server gate at `/events/<slug>/access/` SHALL redirect (HTTP 302) to `invitation_link` when `now + access_early_minutes >= event_datetime` and `now < event_end_datetime`; otherwise it SHALL render the countdown page. The countdown page SHALL reveal the invitation button when remaining time is within the configured window.

#### Scenario: Redirect when within configured window (default 30)
- **WHEN** an event has the default `access_early_minutes = 30` with `event_datetime = now + 20 minutes` and `now < event_end_datetime`
- **THEN** `GET /events/<slug>/access/` returns HTTP 302 to the event's `invitation_link`

#### Scenario: Countdown when outside configured window (default 30)
- **WHEN** an event has the default `access_early_minutes = 30` with `event_datetime = now + 60 minutes`
- **THEN** `GET /events/<slug>/access/` renders `events/access.html` with status 200, shows title, datetime and countdown, and does not redirect

#### Scenario: Custom window redirects inside window (e.g. 90)
- **WHEN** an event has `access_early_minutes = 90` with `event_datetime = now + 60 minutes` and `now < event_end_datetime`
- **THEN** `GET /events/<slug>/access/` returns HTTP 302 to `invitation_link`

#### Scenario: Custom window exposes early_seconds on countdown page
- **WHEN** an event has `access_early_minutes = 90` with `event_datetime = now + 120 minutes`
- **THEN** `GET /events/<slug>/access/` renders `events/access.html` with `early_seconds = 5400` exposed to the client script

#### Scenario: Zero blocks early redirect
- **WHEN** an event has `access_early_minutes = 0` with `event_datetime = now + 5 minutes`
- **THEN** `GET /events/<slug>/access/` renders the countdown page (no redirect)

#### Scenario: Zero redirects once started
- **WHEN** an event has `access_early_minutes = 0` with `event_datetime = now - 5 minutes` and `now < event_end_datetime`
- **THEN** the server redirects to `invitation_link`

#### Scenario: Countdown button reveals within configured window
- **WHEN** the countdown page is rendered with `early_seconds = access_early_minutes * 60`
- **THEN** the invitation button becomes visible once remaining `totalSeconds <= early_seconds` and links to `invitation_link` with `target="_blank"` and `rel="noopener noreferrer"`

#### Scenario: Ended and 404 semantics unchanged
- **WHEN** `now >= event_end_datetime` (with `duration_minutes > 0`)
- **THEN** the server renders `events/ended.html` without revealing the link
- **WHEN** `invitation_link` is empty or `event_datetime` is NULL
- **THEN** the server returns HTTP 404 regardless of `access_early_minutes`

#### Scenario: Timezone-aware comparison
- **WHEN** a lead accesses the page at 09:40 America/Mexico_City for an event at 10:00 with default `access_early_minutes = 30`
- **THEN** the server detects `09:40 + 30min = 10:10 >= 10:00` and redirects to the invitation link
