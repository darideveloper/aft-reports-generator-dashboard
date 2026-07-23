## Context

Event invitation links (Zoom, Meet, etc.) are currently embedded directly in two surfaces:
- The client confirmation email (`client_confirmation.html`)
- The post-submit success state (`form.html` JS)

When attendees click these links before the event time, they reach a non-functional meeting page — the meeting hasn't started. This causes confusion and support requests.

The existing `Event` model has `invitation_link` and `invitation_label` fields but no notion of event date/time. The project uses `TIME_ZONE = "America/Mexico_City"` with `USE_TZ = True`, and all datetime logic goes through `django.utils.timezone`.

The `EventAdmin` uses explicit `fieldsets` — new model fields must be added there explicitly.

## Goals / Non-Goals

**Goals:**
- Add `event_datetime` and `duration_minutes` to the `Event` model, with validation.
- Create an intermediate access page at `/events/<slug>/access/` that validates the event time.
- Server-side redirect to the event link when within 1 hour of start.
- Server-rendered countdown page when ≥ 1 hour before start.
- "Event ended" message when the event has passed (start + duration).
- Replace all direct invitation link references in email and confirmation screen with absolute intermediate URLs.
- Add new fields to admin explicit `fieldsets`.
- Use Django views and templates — minimize client-side JS to just the countdown tick.

**Non-Goals:**
- Replacing the existing lead submission flow or form rendering.
- Adding calendar integration (`.ics` downloads, Google Calendar sync).
- Timezone selection per event — all events use the project timezone.
- Access control beyond time validation (no auth required to view the access page).

## Decisions

### Decision 1: Dedicated `EventAccessView` (TemplateView) vs. extending `EventFormView`
- **Chosen**: New `EventAccessView` as a Django `View` with manual `get()` method.
- **Rationale**: Clear separation of concerns. The form view renders a registration form; the access view handles event entry gating. They share nothing except the Event model lookup. A combined view would need conditional branching on a query parameter, making both paths harder to read and test.
- **Alternatives considered**: Adding `?access=1` to the existing `EventFormView` — rejected because it conflates two distinct responsibilities.

### Decision 2: Server-side redirect vs. JS redirect
- **Chosen**: Server-side `HttpResponseRedirect` when `now + 1h >= event_datetime`.
- **Rationale**: Non-bypassable. Even if JS is disabled, the user gets the right behavior. The 1-hour threshold is checked on every page load, so a user who arrives early and waits will need to refresh (the countdown page handles this client-side for convenience, but the server check is authoritative).
- **Alternatives considered**: JS-only redirect — rejected because it's bypassable and fails without JS.

### Decision 3: `duration_minutes` as `PositiveSmallIntegerField` vs. `DurationField`
- **Chosen**: `PositiveSmallIntegerField` defaulting to 0.
- **Rationale**: Simpler to set in admin (type "90" instead of a duration picker), simpler to display in templates ("90 minutos"), and sufficient precision. Django's `DurationField` stores a `timedelta` which is harder to render in templates without custom filters.
- **Duration=0 handling**: When `duration_minutes=0`, `event_end_datetime` returns `event_datetime` (equal to start). The "event ended" check (`now >= event_end_datetime`) would trigger immediately at start time. To prevent this, the access view treats `duration_minutes=0` as "no end defined" — the ended check is skipped and the link remains accessible after start time.
- **Alternatives considered**: `DurationField` — more precise but over-engineered; making `duration_minutes` nullable — same behavior as 0 but requires migration for existing nulls; requiring `duration_minutes > 0` via model validation when `event_datetime` is set.

### Decision 4: Countdown implementation
- **Chosen**: Server-rendered initial state showing the event info and the remaining time as text plus a lightweight JS countdown that ticks every second. The button is initially hidden and revealed when the countdown reaches 0. The countdown fetches no data — it computes from the initial time delta sent in the template context.
- **Rationale**: The page is useful without JS (shows event info + "Disponible en X horas"). The JS countdown is an enhancement. No API calls needed — the initial delta is embedded in the HTML.
- **Alternatives considered**: Full server-rendered with meta-refresh — works but no live countdown UX; full JS-based with API fetch — over-engineered.

### Decision 5: Access page URL structure
- **Chosen**: `/events/<slug>/access/` — namespaced under the existing `events/` path.
- **Rationale**: Follows RESTful convention (`/events/{slug}/access/` reads as "access this event"). The existing `events/` include already has `app_name = "events"`, so the new route integrates naturally as `events:event-access`.
- **Route ordering**: The access route is defined BEFORE the generic `<slug:slug>/` form route in `events/urls.py` to prevent shadowing, following Django URL resolution best practices.
- **Alternatives considered**: `/e/<slug>/` — shorter but inconsistent with existing URL patterns.

### Decision 6: Handling events without `event_datetime` or `invitation_link`
- **Chosen**: If `event_datetime` is null or `invitation_link` is null/empty, the access view raises `Http404`.
- **Rationale**: These events have no gated link to offer. The confirmation email/form should show no CTA (existing behavior for missing `invitation_link`). The access URL should not be rendered when there's nothing to gate.

### Decision 7: Email absolute URL construction
- **Chosen**: Build the absolute access URL in Python's `send_event_emails()` using `reverse('events:event-access', kwargs={'slug': event.slug})` and the same host/protocol resolution logic already used for `logo_url` (lines 37-44 of `views.py`). Pass the result as `access_url` in the template context.
- **Rationale**: Email templates have no request context, so `{% url %}` produces only relative paths. Absolute URLs are required for email links. This mirrors the existing `logo_url` pattern exactly.
- **Alternatives considered**: Passing the request into the email sending function — would require threading it through the API view, more invasive change; using `direct-to-s3` or external URL builders — unnecessary complexity.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Clock skew between server and client for countdown | Countdown uses server time embedded at render time. Client ticks from that delta — if client clock is off, the countdown duration is correct, only the visual "time remaining" display may differ from the user's clock. |
| Users bookmark the raw invite link | We can't prevent this — they received it before the change. The access gate only applies to links distributed through the new channels. Acceptable trade-off. |
| Duration=0 makes event end at start time | Access view explicitly treats `duration_minutes=0` as "no end defined" — the ended check is skipped entirely. The link stays accessible after start time for these events. |
| Migration adding nullable fields to existing events | Both new fields are nullable with defaults. Fully backward compatible. Model validation (`clean()`) only runs on new saves, not on existing rows. |

## Migration Plan

1. Create Django migration adding `event_datetime` (nullable DateTimeField) and `duration_minutes` (PositiveSmallIntegerField, default=0) to the Event model.
2. Add `event_end_datetime` property and `clean()` validation to the Event model.
3. Add new fields to `EventAdmin.fieldsets` in `events/admin.py`.
4. Implement `EventAccessView` and its templates.
5. Build absolute `access_url` in `send_event_emails()` and pass it to email template context.
6. Add URL route (before the form route in `events/urls.py`).
7. Update `client_confirmation.html` email template to use `{{ access_url }}`.
8. Update `form.html` post-submit CTA to use intermediate URL.
9. Add tests covering all timing states plus model validation.
10. Run existing test suite to confirm no regressions.
11. Deploy — rollback is a simple revert of the migration and code changes.
