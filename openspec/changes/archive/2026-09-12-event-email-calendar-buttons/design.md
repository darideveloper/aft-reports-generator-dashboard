## Context

`events/views.py:send_event_emails()` sends a branded client confirmation (`client_confirmation.html`) with an `access_url` CTA when `invitation_link + event_datetime` are set. The access page (`access.html`) already offers Google / Outlook / Apple calendar actions via `_build_google_calendar_url`, `_build_microsoft_calendar_url`, `_build_ics_content` + `EventCalendarIcsView` (`<slug>/ics/`). Email clients (Gmail, Outlook Word-engine, Apple Mail) strip `<style>`, flex, and SVG, so `access.html` markup cannot be reused verbatim. Locked choices from explore: `METHOD:PUBLISH`, graceful degradation (no VML), Apple = hosted link + attachment.

## Goals / Non-Goals

**Goals:**
- Reuse existing calendar builders with zero date-logic duplication; add absolute ICS URL via `_resolve_absolute_url`.
- Render an email-safe secondary `Agregar a tu calendario:` block + native `.ics` attachment gated on `event_datetime`.
- Keep spam path (no client email), admin email, access page, and ICS endpoint untouched.

**Non-Goals:**
- `METHOD:REQUEST` / Accept-Decline tracking, per-lead `ATTENDEE`, organizer configuration.
- VML bulletproof rounding, SVG icons, webfont or responsive `@media` work.
- Admin email calendar, reschedule-update emails, analytics.

## Decisions

- **Reuse builders, add absolute ICS URL over new code.** Google/Microsoft URLs are already absolute; only `reverse("events:event-ics")` needs `_resolve_absolute_url` (same helper as `logo_url`/`access_url`). Alternative (new serializer/service) rejected as over-engineering.
- **Single-row table, inline styles, text labels, compact sizing.** One `<tr>` with three button cells separated by 8px spacer cells (no flex/`gap`, no media queries): survives 320px + Outlook desktop. Buttons use `padding: 8px 12px` and `13px` bold text (smaller than the primary CTA). `bgcolor` attr + inline `background-color` + `border-radius:6px` gives rounded buttons where supported, squares in old Outlook with full click area. No-VML decision: acceptable since calendar is secondary (primary CTA keeps current style). Alternative full-VML rejected per user choice.
- **Decouple calendar visibility from `access_url`.** Calendar shows on `event_datetime` alone; access CTA still requires `invitation_link + event_datetime`. Rationale: a dated event without a Zoom link is still worth saving.
- **PUBLISH attachment + hosted link (both).** Attachment drives the native banner; hosted link survives corporate `.ics` stripping and stays fresh after reschedules. Filename `{slug}.ics`, stable `UID:{slug}@aft-dashboard` so re-sends update rather than duplicate.
- **Extend text part manually.** `strip_tags` drops hrefs, so append raw URLs to `client_text` when section exists; keeps non-HTML readers functional.

## Risks / Trade-offs

- [Risk] `ALLOWED_HOSTS[0]` wrong → absolute ICS/access URLs point at wrong domain → Mitigation: verify prod host ordering; test asserts `https://` prefix.
- [Risk] Dark-mode inversion washes button colors → Mitigation: solid brand colors, white bold text, contrast ≥4.5:1.
- [Risk] Attachment stripped by corporate filter → Mitigation: hosted link remains (Both decision).
- [Risk] Snapshot staleness (attachment frozen at send) → Mitigation: hosted link is live; documented as accepted tradeoff.
- [Risk] `.ics` `LOCATION` exposes the raw `invitation_link` inside the calendar file (the email body HTML deliberately hides it) → Mitigation: accepted per Both decision; file goes only to the registered lead; body HTML still never renders the raw URL.
- [Trade-off] No VML = square corners in Outlook 2007–2021 desktop; accepted for secondary actions.
