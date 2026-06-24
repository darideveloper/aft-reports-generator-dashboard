## Why

Event registrations currently end at the form submit: the user gets a confirmation email and a "success" iframe state, but no way to actually reach the event itself. Organizers hosting virtual sessions (Zoom, Meet, Teams) have no in-product mechanism to deliver the join link, so they paste it manually into the event description, a follow-up email, or a third-party page. The events app already renders two touchpoints per successful lead (client email + post-submit iframe state) — both are wasted real estate for a CTA that is the whole point of the registration.

## What Changes

- Add two optional fields to the `Event` model:
  - `invitation_link` — `URLField`, max length 500, http(s) only, blank/null. Holds the join URL for the event.
  - `invitation_label` — `CharField`, max length 60, blank, default empty. Optional per-event override of the button text; falls back to `"Acceder al evento"`.
- Render a styled "Acceder al evento" CTA button (with per-event label override) in the client confirmation email **only** when `invitation_link` is set. The button is paired with the raw URL as plain-text fallback below it so email clients that strip buttons still expose a clickable link.
- Render the same CTA in the post-submit success state of the public form (the iframe view) **only** when `invitation_link` is set. The CTA is hidden when no link is configured.
- Expose both fields in the Django admin: list display shows the link, fieldsets expose both fields for editing.
- Add a custom URL validator restricted to `http`/`https` schemes to block `javascript:` and other dangerous schemes from being injected into HTML email and the iframe view.
- Add a migration that adds both fields as nullable/blank — fully backward compatible with existing events and leads.

The admin notification email and the public form area above/below the form deliberately receive **no** invitation CTA. The admin email is informational; the pre-submit form view is for first-time visitors who should not be sent away before they register.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `event-forms`: extend the existing "Form Rendering inside WordPress Iframes" requirement with a scenario covering the post-submit invitation CTA, and the existing "SMTP Auto-notifications with Error Resilience" requirement with a scenario covering the client-email invitation CTA. The base capability stays the same; only new observable behaviors are added.

## Impact

- **Code**:
  - `events/models.py` — two new `Event` fields + module-level http(s) URL validator
  - `events/admin.py` — `list_display` and `fieldsets` updates
  - `events/migrations/0002_*.py` — additive `AddField` operations, no data backfill
  - `events/templates/events/form.html` — new hidden CTA element + JS branch on the 201 response
  - `events/templates/events/emails/client_confirmation.html` — new CTA block gated on `event.invitation_link`
  - `events/tests.py` — new tests for the validator, default label, custom label, button+URL presence/absence in email and iframe
- **APIs**: no public API surface change. `LeadSubmitSerializer` accepts no new client-facing fields. The new fields are admin-only.
- **Backwards compatibility**: 100%. Existing events keep `invitation_link=NULL` / `invitation_label=""`; templates guard the CTA behind `{% if event.invitation_link %}` so no rendered output changes for events without a link.
- **Security**: custom `URLValidator(schemes=["http", "https"])` blocks `javascript:`, `data:`, `file:` and other schemes that could XSS the email HTML or the iframe page. The form-side `target="_blank"` links ship with `rel="noopener noreferrer"`.
- **Localization**: new visible string is `"Acceder al evento"`, es-mx, matching the rest of the project. No new translation surface.
