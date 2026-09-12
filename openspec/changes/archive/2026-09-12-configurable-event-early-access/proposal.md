## Why

The early-access window for event invitation links (when users may see/click the Zoom/Meet URL before start) is hardcoded to 1 hour in both backend and frontend. Organizers need per-event control (e.g. 30 min default, shorter/longer for specific events) without code deploys.

## What Changes

- Add per-`Event` configurable field `access_early_minutes` (`PositiveIntegerField`, default `30`, Spanish admin labels) controlling how many minutes before `event_datetime` the invitation link becomes visible.
- Replace hardcoded server-side gate `now + 1h >= event_datetime` in `EventAccessView.get()` with `now + timedelta(minutes=event.access_early_minutes) >= event_datetime`.
- Replace hardcoded client-side threshold `totalSeconds <= 3600` in `events/access.html` with server-provided `early_seconds`.
- Expose the new field in `EventAdmin` alongside `event_datetime` / `duration_minutes`.
- Backfill existing rows via migration default (`30`). **BREAKING**: existing events previously opening 60 min early will now open 30 min early unless an admin edits them.

## Capabilities

### New Capabilities
- `event-early-access`: per-event configurable early-access window governing when the invitation link is revealed (server redirect + countdown + button visibility), including default, zero, and boundary semantics.

### Modified Capabilities
- `event-forms`: `Event` creation/configuration requirement gains the `access_early_minutes` field (Spanish labels, admin fieldset, default 30).

## Impact

- Affected code: `events/models.py`, `events/views.py` (`EventAccessView`), `events/templates/events/access.html`, `events/admin.py`, new migration, `events/tests.py`.
- No API contract change (`/api/events/<slug>/submit/`, `/events/<slug>/access/`, ICS/calendar URLs unchanged).
- Emails unchanged (confirmation email still links to access gate, gate enforces the window).
- Risk: behavior change for existing events (60 → 30 min); needs admin communication.
