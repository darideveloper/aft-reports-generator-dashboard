## 1. Model & Migration

- [x] 1.1 Add `event_datetime` (nullable DateTimeField) and `duration_minutes` (PositiveSmallIntegerField, default=0) to the Event model in `events/models.py`
- [x] 1.2 Add `event_end_datetime` property that computes `event_datetime + timedelta(minutes=duration_minutes)`. Returns `event_datetime` when duration=0 (the view treats 0 as "undefined" to avoid immediate-end)
- [x] 1.3 Add `clean()` method to Event model: raises `ValidationError` on `duration_minutes` when `event_datetime` is set and `duration_minutes == 0`
- [x] 1.4 Create and run the migration for the new fields

## 2. Admin

- [x] 2.1 Add `event_datetime` and `duration_minutes` to the first fieldset in `EventAdmin.fieldsets` in `events/admin.py` (after `invitation_label`)

## 3. Access View & Templates

- [x] 3.1 Create `EventAccessView` in `events/views.py` as a plain Django View with a `get()` method that:
      - Looks up the event by slug (404 if not found/inactive)
      - Returns 404 if `event_datetime` or `invitation_link` is missing
      - If `duration_minutes > 0` and `now >= event_end_datetime`: renders `events/ended.html`
      - Else if `now + 1h >= event_datetime`: redirects to `event.invitation_link`
      - Otherwise: renders `events/access.html` with time-remaining context
- [x] 3.2 Create `events/templates/events/access.html` with:
      - Event title and datetime display
      - Server-rendered "Tiempo restante: X horas Y minutos" fallback text
      - JS countdown that ticks every second and reveals a clickable "Acceder al evento" button when it reaches 0
      - Button links to `event.invitation_link` with `target="_blank"` and `rel="noopener noreferrer"`
- [x] 3.3 Create `events/templates/events/ended.html` with "Este evento ya ha finalizado" message
- [x] 3.4 Add the route `/<slug:slug>/access/` to `events/urls.py` with name `event-access`, placed BEFORE the generic `<slug:slug>/` form route to avoid shadowing

## 4. Update CTA Surfaces

- [x] 4.1 In `send_event_emails()` in `events/views.py`: build the absolute access URL using `reverse('events:event-access', kwargs={'slug': event.slug})` and the same host/protocol resolution logic used for `logo_url`. Pass `access_url` in the email template context
- [x] 4.2 Update `client_confirmation.html`: replace the CTA button `href="{{ event.invitation_link }}"` with `href="{{ access_url }}"`; remove the raw URL fallback paragraph; wrap the button block with a Django conditional checking `event.event_datetime` is not null AND `event.invitation_link` is truthy
- [x] 4.3 Update `form.html`: replace `ctaLink.href = "{{ event.invitation_link|escapejs }}"` with `"{% url 'events:event-access' slug=event.slug %}"` and wrap the CTA block with a Django conditional checking `event.event_datetime` is not null

## 5. Tests

- [x] 5.1 Write test for EventAccessView: redirects to invitation_link when within 1 hour of event start
- [x] 5.2 Write test for EventAccessView: renders countdown page when more than 1 hour before event
- [x] 5.3 Write test for EventAccessView: renders "ended" page when event has passed (duration > 0)
- [x] 5.4 Write test for EventAccessView: skips ended check when duration=0 (treats as undefined)
- [x] 5.5 Write test for EventAccessView: returns 404 when invitation_link is missing
- [x] 5.6 Write test for EventAccessView: returns 404 when event_datetime is missing
- [x] 5.7 Write test for Event model `clean()`: rejects duration=0 when datetime is set
- [x] 5.8 Write test for Event model `clean()`: allows duration=0 when datetime is null
- [x] 5.9 Run full test suite and confirm no regressions

## 6. Spec Archive Preparation

- [x] 6.1 Update `openspec/specs/event-forms/spec.md` with the delta changes (new fields, admin fieldset, gated CTA behavior, access_url in email context)
