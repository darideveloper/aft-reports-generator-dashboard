## Context

The events app currently delivers a lead through two surfaces: a confirmation email (HTML + text fallback) and a post-submit iframe state. Neither surface has a way to expose a join link to the event itself. The new feature adds an optional, per-event `invitation_link` plus a per-event `invitation_label`, and surfaces the resulting CTA on exactly those two existing touchpoints.

Current surfaces and how this change touches each:

```
                ┌──────────────────────────────────────────────┐
                │  Django App  (events/)                      │
                │                                              │
   POST lead →  │  LeadSubmitView → serializer.save()          │
                │       │                                      │
                │       └─► send_event_emails(lead)            │
                │              ├─► admin_notification.html     │
                │              └─► client_confirmation.html ◄──┼── NEW CTA block
                │                                              │     (if event.invitation_link)
                │  EventFormView → form.html                   │
                │       │                                      │
                │       └─► iframe 201 success state    ◄──────┼── NEW CTA element + JS
                │                                              │     (if event.invitation_link)
                │                                              │
                │  Event Model                                 │
                │       └─► NEW: invitation_link (URLField)    │
                │       └─► NEW: invitation_label (CharField)  │
                └──────────────────────────────────────────────┘
```

The `Event` model is the single point of configuration. There is no `InvitationLink` separate entity, no per-lead token, no expiration. This keeps the feature additive and the data model flat.

## Goals / Non-Goals

**Goals**

- Allow an organizer to set one optional join URL per event, plus an optional button label.
- Render that URL as a CTA button in the **client confirmation email** and the **post-submit iframe success state** only.
- Validate the URL to allow only `http` and `https` schemes.
- Stay backward compatible: existing events must keep working with no visible change.
- Add admin surface and tests; do not break the existing test suite.

**Non-Goals**

- Multiple CTAs per event (e.g. one for joining, one for materials).
- Per-lead personalized or expiring tokens.
- A/B testing the CTA copy.
- Tracking clicks or analytics.
- Making the button label translatable (project is single-language es-mx).
- Fixing the existing misleading success message that says "Hemos enviado un correo de confirmación" even when `email_active=False`. Flagged during exploration; explicitly deferred.
- Modifying the public form area above/below the form (pre-submit view). The CTA appears only after a successful 201.
- Showing the CTA in the admin notification email (organizer-facing, not attendee-facing).

## Decisions

### 1. Two fields, not one

Use two fields on `Event`: `invitation_link` (the URL) and `invitation_label` (the button text). The user explicitly asked for per-event label configurability. A single combined `URLField(..., help_text="…")` would force the default copy on every event.

**Why over a single `CharField` with embedded label?** URL validation (scheme restriction) and the existence of a meaningful empty state are easier to express as a dedicated `URLField`. The label is free-form, short, optional — `CharField(max_length=60, blank=True, default="")` is the natural fit.

**Why not a separate `InvitationLink` model with FK to `Event`?** Each event has at most one link. A model-per-link would add a join, a separate admin inline, and a query on the email/iframe path. The `Event` row is already loaded for both render paths. A single URLField on `Event` is the smallest change that satisfies the requirement.

### 2. `URLField` with scheme-restricted validator, max_length=500

```python
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_http_https_validator = URLValidator(schemes=["http", "https"])

def _validate_http_https_url(value: str) -> None:
    try:
        _http_https_validator(value)
    except ValidationError:
        raise ValidationError("El enlace debe ser una URL http(s) válida.")
```

- `URLField` gives us admin input that produces a clickable link and clean storage (`max_length=200` by default — widened to `500` to fit Zoom/Meet URLs with tracking params).
- Restricting to `http`/`https` blocks `javascript:`, `data:`, `file:`, `vbscript:`, etc. These are real XSS vectors in HTML email and iframes.
- `blank=True, null=True` is required because the field is optional and the migration must work on rows that pre-date the change.
- The validator is module-level so `from events.models import _validate_http_https_url` is trivial if a future test wants to call it directly.

**Alternatives considered:**

- **`CharField` with manual URL parsing** — fewer guarantees, re-implements what `URLField` does.
- **Built-in `URLField` without scheme restriction** — leaves the XSS gap. Not acceptable for an email-rendered and iframe-rendered string.
- **Pre-validate on `save()` instead of `validators=[...]`** — runs too late; the form/admin would 500 on bad input rather than show a clean validation error.

### 3. Default label fallback via a model property

The model exposes `Event.invitation_label_display` which centralizes the fallback rule:

```python
@property
def invitation_label_display(self) -> str:
    if self.invitation_label and self.invitation_label.strip():
        return self.invitation_label.strip()
    return "Acceder al evento"
```

Both templates use `{{ event.invitation_label_display }}` instead of the inline `|default:"Acceder al evento"` filter. The property handles three cases that the filter mishandles:
- empty string → fallback
- whitespace-only string (e.g. `"   "`) → fallback (the `|default` filter does NOT trim; it only checks truthiness, and a non-empty whitespace string is truthy)
- `None` → fallback (in-memory instances only; the column is `NOT NULL` with `default=""`)

Templates do `{{ event.invitation_label_display }}` (with `|escapejs` in the form.html JS branch and `style="color: #ffffff; text-decoration: none;"` on the email `<a>` for email-client compatibility).

We do **not** store the default in the database, and we do **not** add a `clean()` method that mutates the value.

**Why?** Keeps the on-disk representation honest. An admin can tell at a glance whether they set a custom label. Changing the project-wide default later is a one-line property edit, not a data migration.

**Trade-off:** The default literal `"Acceder al evento"` lives in one model property, two template files, and the test module. Acceptable for a Spanish-only project.

### 4. CTA placement: only in the post-submit iframe state

The user asked for the CTA **only** in the client email **and** the post-submit success state. The form area above the form must stay clean. The current `form.html` 201 branch is:

```js
if (response.status === 201) {
    form.style.display = 'none';
    successAlert.style.display = 'block';
    sendIframeHeight();
}
```

We add a sibling element `#invitation-cta` (initially `display: none`) and only show it server-side, inside the same script block, when `event.invitation_link` is truthy:

```html
{% if event.invitation_link %}
<div id="invitation-cta" class="alert alert-success" style="display:none; text-align:center;">
  <a id="invitation-cta-link" href="#"
     target="_blank" rel="noopener noreferrer"
     style="background-color: {{ branding.colors.primary|default:'#0a3c58' }};
            color: #ffffff; padding: 12px 24px; border-radius: 6px;
            text-decoration: none; font-weight: bold; display: inline-block;">
    {{ event.invitation_label|default:"Acceder al evento" }}
  </a>
</div>
{% endif %}
```

The JS reveals it on success and stamps the href/label:

```js
{% if event.invitation_link %}
const ctaEl  = document.getElementById('invitation-cta');
const ctaLink = document.getElementById('invitation-cta-link');
ctaLink.href  = "{{ event.invitation_link|escapejs }}";
ctaLink.textContent = "{{ event.invitation_label_display|escapejs }}";
ctaEl.style.display = 'block';
{% endif %}
```

The label source is the model property `invitation_label_display` (see Decision #3), which centralizes the default-and-trim logic. The template's only job here is to apply `|escapejs` for safe JS interpolation.

**Why a sibling, not a child of `#success-alert`?** The success alert is a pre-existing element with styling we should not perturb. A sibling keeps CSS, dynamic iframe height, and `display: none` toggling surgical.

**Why `|escapejs`?** Both `invitation_link` and `invitation_label` are admin-editable text. The link is also a URL. Injecting either into a JavaScript string literal without `|escapejs` is a server-side XSS vector (e.g. `invitation_label=</script><script>...`). The `|escapejs` filter is the Django-recommended sanitizer for JS-context interpolation.

### 5. Email: button + raw URL fallback

The client confirmation email gets a single new block, gated on `event.invitation_link`:

```django
{% if event.invitation_link %}
<div class="button-wrapper">
  <a href="{{ event.invitation_link }}"
     target="_blank" rel="noopener noreferrer"
     class="button"
     style="color: #ffffff; text-decoration: none;">{{ event.invitation_label_display }}</a>
</div>
<p style="word-break: break-all; font-size: 12px; color: #94a3b8;
          text-align: center; margin-top: 12px;">
  {{ event.invitation_link }}
</p>
{% endif %}
```

The existing `<style>` defines `.button-wrapper` and `.button` (uses `branding.colors.primary`). The button text color (`color: #ffffff`) and `text-decoration: none` are duplicated as **inline style** on the `<a>` tag because some email clients (Outlook desktop, certain mobile clients) ignore CSS class selectors from `<style>` blocks. Inline style is the bulletproof channel for transactional email.

The `<p>` is a plain-text fallback for clients that strip buttons entirely. `word-break: break-all` prevents long tracking URLs from overflowing the 600px container.

### 6. Admin surface

Both new fields MUST be editable in the event edit form, and `invitation_link` MUST be visible in the event list view. The first `fieldsets` group gains both new fields, placed after `notify_email` (which they are conceptually adjacent to — both are "what we send to whom"):

```python
fieldsets = (
    (None, {
        "fields": ("title", "slug", "is_active", "notify_email",
                   "invitation_link", "invitation_label")
    }),
    ("Campos del Formulario (Activo)",  {...}),  # unchanged
    ("Campos del Formulario (Requerido)", {...}),  # unchanged
)
```

For `list_display`, the raw `URLField` shows as plain text in Django admin. To give the organizer a one-click reach, the change introduces a tiny display method that renders the URL as a clickable `<a target="_blank" rel="noopener noreferrer">`, or `—` (em-dash) when the field is blank. `invitation_label` is NOT in `list_display` (too long, low information density relative to the link itself).

```python
from django.utils.html import format_html

@admin.display(description="Enlace de invitación", ordering="invitation_link")
def invitation_link_display(self, obj):
    if not obj.invitation_link:
        return "—"
    return format_html(
        '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
        obj.invitation_link,
        obj.invitation_link,
    )

list_display = ("title", "slug", "is_active", "notify_email",
                "invitation_link_display", "created_at")
```

`search_fields` is intentionally NOT extended with `invitation_link` — URL search is noisy and rarely useful. `list_filter` is unchanged (no good filter for a single optional URL). `readonly_fields` does not need to list the new fields — they are editable. `prepopulated_fields` is unchanged (only `slug` is prepopulated from `title`).

**Alternatives considered:**

- **Plain `URLField` in `list_display`** — works but renders as long unbroken text. Bad UX; the list page becomes unreadable for events with long tracking URLs.
- **Adding `invitation_label` to `list_display` as well** — would crowd the list view. The label is fully derivable from the link (it is the button text) and is rarely edited, so the edit page is the right place to show it.

### 7. Migration strategy

A single auto-generated migration `0002_event_invitation_link.py` (or `0002_event_invitation.py` if grouped) that does:

```python
operations = [
    migrations.AddField(
        model_name="event",
        name="invitation_link",
        field=models.URLField(
            blank=True, max_length=500, null=True,
            verbose_name="Enlace de invitación",
            help_text="URL opcional ...",
            validators=[...],
        ),
    ),
    migrations.AddField(
        model_name="event",
        name="invitation_label",
        field=models.CharField(
            blank=True, default="", max_length=60,
            verbose_name="Texto del botón de invitación",
            help_text="...",
        ),
    ),
]
```

No `RunPython` data backfill, no `default=` on the URL field. The migration is purely additive. Rollback is `migrate events 0001`.

## Risks / Trade-offs

- **[Server-side XSS via `invitation_label` or `invitation_link` if `|escapejs` is forgotten on the form.html branch]** → Mitigated by the test `test_invitation_label_escapejs_safe` which creates an event with a label of `</script><script>alert(1)</script>`, GETs the form, and asserts that the rendered response contains the escaped form (`\u003C`) and does NOT contain a raw `<script>` injection that would break out of the inline `<script>` block. Risk is small because the field is admin-only, not user-submitted.
- **[Default label "Acceder al evento" duplicated across files]** → Mitigated by centralizing the fallback rule in `Event.invitation_label_display` (model property). The literal still appears in 3 source files (the property, the form.html static initial text, and test assertions) but the property is the single source of truth for the runtime fallback. A future i18n pass would only need to update the property.
- **[Spambot triggers the 201 branch and "sees" the CTA]**
  → Mitigated by the fact that the CTA reveal happens in JavaScript that runs only in a real browser. A bot that POSTs the JSON and reads the response never executes the iframe JS. No data leak.
- **[Long URLs break the email layout]** → Mitigated by `word-break: break-all` on the fallback `<p>`. Buttons wrap on the styled `<a>` via standard inline-block behavior; visual breakage is bounded. The long-URL render test (`test_long_url_intact_in_client_email` and `test_long_url_intact_in_iframe_template`) verifies the full URL is delivered intact in both surfaces, not just stored in the DB.
- **[Email button text invisible in clients that strip `<style>` blocks]** → Mitigated by adding inline `style="color: #ffffff; text-decoration: none;"` directly on the `<a>` tag in the email template. Some email clients (notably Outlook desktop) ignore CSS class selectors from `<style>` blocks; inline style survives them.
- **[Django admin URL field rendering on `list_display`]** → Mitigated by the new `invitation_link_display` method which renders the URL as a clickable `<a target="_blank" rel="noopener noreferrer">`. Empty values render as `—`. Verified by an automated test (task 5.8).
- **[Test coverage gap if old tests aren't re-run]** → All existing tests (honeypot, missing-required, branding, SMTP error) must continue to pass. The new tests are additive. Mitigation: run `python manage.py test events` before declaring done.
- **[Email client support for `target="_blank"`]** → Universal on webmail. Some mobile clients ignore it and navigate the current tab. Acceptable.
- **[No CSRF / X-Frame changes]** → The form is already CSRF-exempt on the public POST endpoint; no change there. The iframe exemption is already in place via `xframe_options_exempt`. No new exposure.

## Migration Plan

- **Apply:** `python manage.py migrate events` (auto-generated migration; additive, no backfill, zero downtime).
- **Verification:** `python manage.py check` and `python manage.py test events` must both pass.
- **Rollback:** `python manage.py migrate events 0001` — drops both columns. Any event that had been configured with a link loses that data. Acceptable because no production event has been configured with a link at the time this change is proposed (feature does not exist yet).
- **Smoke test post-deploy:**
  1. In admin, edit an event, set `invitation_link = "https://zoom.us/j/123"`, save.
  2. Submit a valid lead to that event.
  3. Confirm the client email arrives with the button and the raw URL fallback.
  4. Confirm the iframe post-submit state shows the button and clicking it opens the URL in a new tab.
  5. Submit a lead to an event without `invitation_link`. Confirm no CTA appears in either surface.
- **No infrastructure changes.** No new env vars, no new dependencies (`django.core.validators.URLValidator` ships with Django).

## Open Questions

None remaining. All decisions were confirmed during the explore-mode discussion:

| Question                                     | Answer                                          |
|----------------------------------------------|-------------------------------------------------|
| Where does the link appear?                  | Client email + post-submit iframe only          |
| Field type?                                  | `URLField`                                      |
| Form placement?                              | Post-submit success state only                  |
| Button label?                                | Per-event configurable, default `"Acceder al evento"` |
| Admin email includes link?                   | No                                              |
| Email fallback?                              | Raw URL as plain-text below the button          |
| Fix success message dynamic copy?            | Out of scope (deferred)                         |
| OpenSpec structure?                          | Extend existing `event-forms` capability        |
| `URLField` max length?                       | 500                                             |
