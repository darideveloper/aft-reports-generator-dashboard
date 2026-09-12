## 1. Backend email context + attachment

- [x] 1.1 Extend `send_event_emails()` in `events/views.py` to build `google_url`, `microsoft_url`, `ics_absolute_url` (via `_resolve_absolute_url(reverse("events:event-ics"))`) and `ics_content` when `event.event_datetime` is set, pass into client template context.
- [x] 1.2 Attach `{slug}.ics` (`text/calendar`, PUBLISH) via `client_msg.attach()` and append raw calendar URLs to the plain-text body when section exists; keep inside existing try/except so SMTP failure still returns 201.

## 2. Email template

- [x] 2.1 Add `Agregar a tu calendario:` block to `events/templates/events/emails/client_confirmation.html` after access CTA, gated on `{% if google_url %}`, using a single-row `<table role="presentation">` with three side-by-side buttons (8px spacers), compact sizing (`8px 12px` padding, `13px` text), all-inline styles and text-only labels (no flex/SVG/style reliance).
- [x] 2.2 Verify primary access CTA order/condition unchanged and raw `invitation_link` still never rendered.

## 3. Tests + verification

- [x] 3.1 Add tests in `events/tests.py`: section + 3 URLs present with datetime; absent without datetime; calendar-only when no invitation link; attachment name/mimetype/content (`UID`, `BEGIN:VCALENDAR`); text body contains raw URLs; spam sends nothing.
- [x] 3.2 Run `python manage.py test events` green and manually inspect rendered HTML at 320px + test inbox (Gmail, Outlook web, Apple Mail) for stacking, tap targets, and native Add banner.
