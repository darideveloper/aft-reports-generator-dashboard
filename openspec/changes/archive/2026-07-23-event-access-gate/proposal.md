## Why

Event invitation links (Zoom, Meet, etc.) are exposed directly in the confirmation email and post-submit confirmation screen. Attendees who click these links too early (hours or days before the event) land on a non-functional meeting page — the meeting hasn't started yet. This creates confusion, support requests, and a poor user experience. We need a gating mechanism that validates the event time before revealing the meeting link.

## What Changes

- **Event model**: Add `event_datetime` (DateTimeField) and `duration_minutes` (PositiveSmallIntegerField) to define when the event starts and how long it lasts. Add model validation requiring `duration_minutes > 0` when `event_datetime` is set.
- **New intermediate access page**: Replace direct invitation links in the email and confirmation screen with a URL to a new Django-rendered view at `/events/<slug>/access/` that validates the event time.
- **Access page behavior**:
  - Before event (≥1 hour away): Show event info + server-rendered countdown. No JS-dependent redirect — the countdown ticks and reveals a "Acceder al evento" button when ready.
  - Near event (<1 hour away): Server-side redirect straight to the invitation link.
  - After event ends (start + duration passed): Show "Evento finalizado" message.
  - Missing `event_datetime` or `invitation_link`: 404/fallback (no CTA shown).
  - `duration_minutes=0`: treated as "no end defined" — countdown/redirect work normally but the "ended" check never triggers (avoids immediate end at start time).
- **Confirmation email**: Uses an absolute access URL built in Python (`reverse()` + host), passed as `access_url` in the template context — mirrors the existing `logo_url` pattern. The raw `invitation_link` is never exposed in the email body.
- **Post-submit CTA in form**: The success state button now points to the access page instead of the raw meeting URL.
- **Admin fieldset**: `event_datetime` and `duration_minutes` added explicitly to the first fieldset in `EventAdmin` (the admin uses explicit `fieldsets`, so auto-discovery won't work).
- **All datetime logic** uses `django.utils.timezone` with project timezone (`America/Mexico_City`).

## Capabilities

### New Capabilities
- `event-access-gate`: Server-side access validation for event invitation links. Handles date/time checks, countdown rendering, "event ended" state, and redirection based on time proximity to the event.

### Modified Capabilities
- `event-forms`: The Event model gains `event_datetime` and `duration_minutes` fields with model validation. The invitation-link CTA behavior changes in both the client confirmation email and the post-submit form state — the link target changes from the raw meeting URL to the intermediate access page. New admin form fields added to explicit fieldset and updated visibility rules.

## Impact

- **`events/models.py`**: Add `event_datetime` and `duration_minutes` fields, plus `event_end_datetime` property, plus `clean()` validation.
- **`events/views.py`**: New `EventAccessView` (Django `View`). Update `send_event_emails()` to build and pass `access_url` in template context.
- **`events/urls.py`**: New route `/<slug:slug>/access/` placed before the generic form route to avoid shadowing.
- **`events/admin.py`**: Add new fields to explicit `fieldsets`.
- **`events/templates/events/`**: New `access.html` and `ended.html` templates.
- **`events/emails/client_confirmation.html`**: CTA href changed to `{{ access_url }}` (absolute URL from Python context).
- **`events/templates/events/form.html`**: Post-submit JS CTA href changed to the intermediate URL.
- **`openspec/specs/event-forms/spec.md`**: Updated to reflect new model fields, admin fieldset, and gated CTA behavior.
- **Migration**: New migration for the Event model.
- **Tests**: New tests for EventAccessView covering all timing states plus model validation.
