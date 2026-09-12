## Why

Leads receive a confirmation email with an access CTA but no way to save the event date. Adding the same Google / Outlook / Apple calendar actions already present on the access page directly into the client email reduces no-shows and support requests.

## What Changes

- Client confirmation email gains an optional `Agregar a tu calendario:` section with three link buttons (Google, Outlook, Apple `.ics`) shown only when `Event.event_datetime` is set.
- Email buttons reuse existing `_build_google_calendar_url`, `_build_microsoft_calendar_url`, `_build_ics_content` with no new date logic; ICS download URL is made absolute via existing `_resolve_absolute_url`.
- Client email attaches `{slug}.ics` (`text/calendar`, `METHOD:PUBLISH`) so Gmail / Outlook / Apple Mail show a native Add-to-calendar banner. Note: the `.ics` `LOCATION` reuses `invitation_link`, so the raw meeting URL is visible inside the downloaded file (never in the email body HTML) — accepted tradeoff.
- Template uses table-based layout with all-inline styles (no flex, no SVG, no `<style>` reliance) so it renders in Gmail, Outlook desktop (Word engine, square-corner degradation accepted, no VML), and Apple Mail.
- Plain-text fallback appends raw calendar URLs when the section exists.
- No change to admin email, access page, form, API contract, or ICS endpoint behavior.

## Capabilities

### New Capabilities

- `email-calendar-invite`: calendar actions inside the client confirmation email (link buttons + ICS attachment + rendering rules).

### Modified Capabilities

- `event-forms`: client confirmation email body gains optional calendar section and attachment; visibility gated on `event_datetime`.
- `add-to-calendar`: existing builders/ICS content reused in email context; adds absolute ICS URL requirement for email use.

## Impact

- Affected: `events/views.py` (`send_event_emails`), `events/templates/events/emails/client_confirmation.html`, `events/tests.py`.
- No migrations, no new dependencies, no API changes.
- Minor increase in email size (~0.5KB ICS attachment); spam path unchanged (no client email).
