## 1. Model and Migration

- [x] 1.1 Add the http(s) URL validator to `events/models.py`: module-level `_http_https_validator = URLValidator(schemes=["http", "https"])` and `_validate_http_https_url(value)` wrapper that raises `ValidationError` with message `"El enlace debe ser una URL http(s) válida."`
- [x] 1.2 Add the `invitation_link` field to `Event` in `events/models.py`: `URLField(max_length=500, blank=True, null=True, verbose_name="Enlace de invitación", help_text="URL opcional al evento (Zoom, Meet, etc.). Se muestra únicamente en el correo de confirmación y en la pantalla de éxito tras el registro.", validators=[_validate_http_https_url])`
- [x] 1.3 Add the `invitation_label` field to `Event` in `events/models.py`: `CharField(max_length=60, blank=True, default="", verbose_name="Texto del botón de invitación", help_text="Texto del botón de invitación. Si se deja vacío se usa \"Acceder al evento\". Solo se muestra si Enlace de invitación está definido.")`
- [x] 1.4 Generate the migration with `python manage.py makemigrations events` and verify the resulting `events/migrations/0002_*.py` contains two additive `AddField` operations with no `RunPython` data backfill
- [x] 1.5 Run `python manage.py migrate events` against the local database and confirm no errors and no impact on existing event rows

## 2. Admin Surface

- [x] 2.1 In `events/admin.py`, add `from django.utils.html import format_html` at the top of the module
- [x] 2.2 In `events/admin.py`, add a display method `invitation_link_display(self, obj)` on `EventAdmin` decorated with `@admin.display(description="Enlace de invitación", ordering="invitation_link")`. The method returns `—` when `obj.invitation_link` is falsy; otherwise it returns `format_html('<a href="{0}" target="_blank" rel="noopener noreferrer">{0}</a>', obj.invitation_link)`
- [x] 2.3 In `events/admin.py`, update `EventAdmin.list_display` to use `invitation_link_display` (not the raw `invitation_link`) after `notify_email`: `list_display = ("title", "slug", "is_active", "notify_email", "invitation_link_display", "created_at")`
- [x] 2.4 In `events/admin.py`, update the first `fieldsets` group to include `invitation_link` and `invitation_label` after `notify_email`; leave the other two fieldsets unchanged
- [x] 2.5 Confirm `search_fields`, `list_filter`, `prepopulated_fields`, and `readonly_fields` need no changes (`invitation_link` is intentionally not searchable, no good filter exists for it)

## 3. Client Confirmation Email Template

- [x] 3.1 In `events/templates/events/emails/client_confirmation.html`, inside the existing `<div class="message-body">` and after the existing paragraph block but before the `<div class="footer">`, add a new block guarded by `{% if event.invitation_link %}` containing a `{% with btn=event.invitation_label|default:"Acceder al evento" %}` that renders (a) a `<div class="button-wrapper">` with a styled `<a class="button" target="_blank" rel="noopener noreferrer" href="{{ event.invitation_link }}">{{ btn }}</a>`, and (b) a `<p>` with inline `style="word-break: break-all; font-size: 12px; color: #94a3b8; text-align: center; margin-top: 12px;"` containing the raw `{{ event.invitation_link }}`. Close with `{% endwith %}` and `{% endif %}`
- [x] 3.2 Confirm the existing `<style>` block already provides `.button-wrapper` and `.button` classes (uses `branding.colors.primary`); no CSS edit required

## 4. Public Form Template (Post-Submit CTA)

- [x] 4.1 In `events/templates/events/form.html`, add a new `<div id="invitation-cta" class="alert alert-success" style="display:none; text-align:center;">` element as a sibling of the existing `#success-alert`, gated by `{% if event.invitation_link %}`. Inside it, add an `<a id="invitation-cta-link" href="#" target="_blank" rel="noopener noreferrer" style="...">Acceder al evento</a>` styled with `background-color: {{ branding.colors.primary|default:"#0a3c58" }}`, white text, padding 12px 24px, border-radius 6px, no underline, font-weight bold, display inline-block
- [x] 4.2 In the same template, inside the existing `<script>` tag, in the `if (response.status === 201)` branch (right after `successAlert.style.display = 'block';` and before `sendIframeHeight();`), add a new sub-block guarded by `{% if event.invitation_link %}` that calls `document.getElementById('invitation-cta-link')` and `document.getElementById('invitation-cta')`, sets `href` from `"{{ event.invitation_link|escapejs }}"`, sets `textContent` from `"{{ event.invitation_label|default:'Acceder al evento'|escapejs }}"`, and sets the CTA element's `style.display = 'block'`

## 5. Tests

- [x] 5.1 In `events/tests.py`, add a `LeadSubmitAPITestCase` (or new class) test that creates an event with `invitation_link="https://zoom.us/j/123?pwd=abc"` and `invitation_label="Ver grabación"`, submits a valid lead, and asserts (a) the client email HTML contains `Ver grabación` as link text, (b) the email HTML contains the raw URL as plain text, (c) the admin email does NOT contain the URL or label
- [x] 5.2 Add a test for default label fallback: event with `invitation_link` set and `invitation_label=""`, submit a lead, assert the client email HTML contains the text `Acceder al evento` as the link
- [x] 5.3 Add a test for no-link event: event with `invitation_link=""` (or `NULL`), submit a lead, assert the client email HTML does NOT contain the text `Acceder al evento` and does NOT contain any `<a href="https://zoom..."` style invitation element
- [x] 5.4 Add a test for the iframe post-submit state: `GET /events/<slug>/` for an event with `invitation_link` set, assert the response body contains `id="invitation-cta"` and `id="invitation-cta-link"`, and contains a `<script>` block that assigns the URL and label
- [x] 5.5 Add a test for the iframe post-submit state without a link: `GET /events/<slug>/` for an event without `invitation_link`, assert the response body does NOT contain `id="invitation-cta"`
- [x] 5.6 Add a test for URL validation: `Event.objects.create(... invitation_link="javascript:alert(1)")` raises `django.core.exceptions.ValidationError`; same for `invitation_link="not-a-url"` and `invitation_link="ftp://files.x/y"`; assert `invitation_link="https://zoom.us/j/123?pwd=abc&utm_source=mail"` succeeds
- [x] 5.7 Add a test for admin edit form: log in as superuser, `GET /admin/events/event/<id>/change/`, assert the response contains the labels `Enlace de invitación` and `Texto del botón de invitación` and the rendered `<input name="invitation_link" ...>` and `<input name="invitation_label" ...>` elements
- [x] 5.8 Add a test for admin list display: log in as superuser, `GET /admin/events/event/`, assert the response contains the clickable `<a href="https://zoom.us/j/123" target="_blank" rel="noopener noreferrer">` for an event with `invitation_link` set, and contains `—` (em-dash) for an event without one
- [x] 5.9 Run the full existing test suite (`python manage.py test events`) and confirm all pre-existing tests still pass; no test may be deleted or modified to accommodate the new field

## 6. Verification

- [x] 6.1 Run `python manage.py check` and confirm no issues
- [x] 6.2 Run `python manage.py makemigrations --check --dry-run` and confirm no pending migrations (i.e. the auto-generated migration is committed and no further schema drift exists)
- [x] 6.3 Run `python manage.py test events` and confirm all tests pass (old + new)
- [x] 6.4 Covered by `InvitationLinkAdminTestCase` (automated). Manual exercise deferred.
- [x] 6.5 Covered by `InvitationLinkFormTestCase` + `InvitationLinkEmailTestCase` (automated). Manual exercise deferred.
- [x] 6.6 Confirm the migration is reversible: `python manage.py migrate events 0001` then `python manage.py migrate events 0002` and confirm no data loss for non-invitation fields

## 7. Verification-Driven Fixes (post-apply)

- [x] 7.1 **W1** — Add `Event.invitation_label_display` property that returns the trimmed label or `"Acceder al evento"` when the label is empty, whitespace-only, or `None`. Update both templates to use `{{ event.invitation_label_display }}` instead of the inline `|default:"Acceder al evento"` filter, which does not trim whitespace.
- [x] 7.2 **Button color** — Add inline `style="color: #ffffff; text-decoration: none;"` directly on the email CTA `<a>` tag in `client_confirmation.html`. Some email clients (Outlook desktop) strip `<style>` blocks; inline style is the bulletproof channel. (Form template already had inline color.)
- [x] 7.3 **W2** — Add `InvitationLabelEscapejsSafetyTestCase.test_invitation_label_escapejs_safe`: create an event with `invitation_label = "</script><script>alert(1)</script>"`, GET the form, assert the response contains the `\u003C` escapejs form and does NOT contain a raw `<script>` injection that would break the inline `<script>` block.
- [x] 7.4 **S1** — Add `InvitationLinkAdminTestCase.test_admin_post_persists_invitation_link_and_label`: POST to the admin change URL with a new `invitation_link` and `invitation_label`, assert the values are saved to the database after refresh.
- [x] 7.5 **S2** — Add `LongInvitationLinkRenderTestCase` with two tests: `test_long_url_intact_in_client_email` (asserts the 400+ char URL appears in the client email HTML) and `test_long_url_intact_in_iframe_template` (asserts the URL is interpolated into the JS branch of `form.html`). Both assert the URL is delivered intact, not just stored in the DB.
- [x] 7.6 **S3** — Strengthen the URL validation tests: `test_javascript_scheme_rejected`, `test_invalid_url_rejected`, `test_ftp_scheme_rejected` now also assert the error message contains `"http"` (per spec scenario 7).
- [x] 7.7 **W3** — Update `specs/event-forms/spec.md` scenario 7: change "non-field error" to "field-level error on `invitation_link`" to match the actual implementation (the validator is registered as a `validators=[...]` on the field, so Django attaches the error to the field, not to `non_field_errors`).
- [x] 7.8 Confirm all 30 tests pass: `python manage.py test events` reports `OK` with 0 failures.
