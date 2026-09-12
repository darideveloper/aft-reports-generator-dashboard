## Context

`EventAccessView` (`events/views.py:201-241`) currently hardcodes the early-access window in two places: server-side `now + timedelta(hours=1) >= event_datetime` → 302 to `invitation_link`, and client-side `totalSeconds <= 3600` in `events/templates/events/access.html:84` → reveal button. `Event` (`events/models.py:21-66`) has no field for this; `EventAdmin` (`events/admin.py:25-36`) has no control. Prior spec `2026-07-23-event-access-gate` fixed the window at 1h. Stakeholders: event organizers (need per-event timing), leads (countdown UX), admins.

Constraints: Django 4.2, Spanish admin labels, `AutoField` PK convention, timezone-aware comparisons via `timezone.now()` (`TIME_ZONE = America/Mexico_City`), no new dependencies, keep email/ICS/calendar behavior unchanged.

## Goals / Non-Goals

**Goals:**
- Per-event configurable early-access window in minutes, default 30, editable in Django admin.
- Single source of truth on `Event`; server gate and countdown button both derive from it.
- Preserve ended/404 semantics and timezone handling.

**Non-Goals:**
- No per-lead/per-company windows, no scheduling UI beyond an integer field.
- No change to confirmation email body, ICS/Google/Outlook URLs, submit API, or `duration_minutes` validation.
- No global setting/env override in this change.

## Decisions

- **Field: `access_early_minutes = PositiveIntegerField(default=30)` on `Event`.**
  Why: minutes are the natural unit (organizers say "open 30/15/90 min early"); integer keeps admin + validation trivial, YAGNI over DurationField. `PositiveIntegerField` blocks negatives at DB/form level; `0` means "only from start". Alternative considered: global `settings.EVENT_EARLY_MINUTES` — rejected (organizers need per-event variance); `DurationField` — rejected (heavier widget, harder admin UX for same expressiveness).
- **Server gate: `now + timedelta(minutes=event.access_early_minutes or 0) >= event_datetime`.**
  Why: minimal diff to existing gate, keeps `or 0` null-safety, preserves boundary-inclusive semantics (`>=`). Alternative: property `event.early_open_datetime` — nice but adds indirection for one use site; inline keeps the diff reviewable.
- **Template: pass `early_seconds` from `get_context_data`, use it in JS instead of `3600`.**
  Why: server stays authoritative; JS stays a UX mirror (page refresh still re-gates). Keeps no-JS fallback intact (button hidden, countdown text server-rendered).
- **Migration default `30` backfills existing rows.**
  Why: simplest Django migration (`default=30` on field). Trade-off accepted: existing events silently move 60→30 min (documented as BREAKING in proposal; admins can re-edit).
- **Admin placement: same fieldset as `event_datetime`/`duration_minutes`.**
  Why: the three fields form one temporal group; Spanish `verbose_name="Anticipación de acceso (minutos)"` + help text follows project localization convention.

## Risks / Trade-offs

- [Risk] Existing events open later than before (60→30) without organizers noticing → Mitigation: call out in release notes; admin can bulk-edit. Decision confirmed: blanket 30 backfill, no 60-preservation migration.
- [Risk] JS/client clock drift shows button early/late → Mitigation: server redirect remains authoritative; JS only toggles visibility, refresh re-validates.
- [Risk] `0` confused with "always open" → Mitigation: help text states `0 = solo desde el inicio`; ended-state still hides link after `event_end_datetime`.
- [Trade-off] No upper-bound validation (e.g. 1440) — YAGNI; absurd values just open early, harmless.

## Migration Plan

1. Add field + migration (`makemigrations events`).
2. Deploy; existing rows default to 30.
3. Verify: access gate tests, manual check `/events/<slug>/access/` at boundary, admin edit round-trip.
4. Rollback: revert code + migration; gate returns to hardcoded 1h (no data loss — column dropped).

## Open Questions

None. Resolved per stakeholder confirmation: pre-existing rows backfill to blanket `30` (no 60-preservation migration); no max cap (unbounded); `0` means "only from start".
