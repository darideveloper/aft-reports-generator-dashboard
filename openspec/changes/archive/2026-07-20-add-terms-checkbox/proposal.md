## Why

The event registration form currently captures lead data and sends it to the server without any legal consent signal. Mexican and international privacy regulations (LFPDPPP, GDPR) require that users explicitly accept terms and privacy policies before their data is submitted. Adding a mandatory checkbox to the form provides the legal audit trail and aligns with the privacy link already displayed in the project's branding.

## What Changes

- Add a required checkbox to `events/templates/events/form.html` before the submit button with the text **"He leído y acepto los Términos y Condiciones y el Aviso de Privacidad."**
- The phrase "Términos y Condiciones y el Aviso de Privacidad" links to `https://www.leadforward.mx/legal` (single hyperlink wrapping both documents).
- Add validation in `events/serializers/LeadSubmitSerializer` requiring the checkbox to be truthy; reject the submission with a field-level error if unchecked.
- The checkbox value is NOT persisted to the `Lead` model — it is validated and then discarded before `save()`, following the existing honeypot pattern.
- No new DB columns, no migrations, no changes to CSV/Excel exports.
- The existing exports (`Nombre, Email, Teléfono, Puesto de trabajo, Empresa, Evento, Spam, Fecha de Registro`) are unaffected — the checkbox never touches the Lead model.

## Capabilities

### New Capabilities
<!-- None — the checkbox extends existing form submission behaviour, it doesn't introduce a new standalone capability. -->

### Modified Capabilities
- `event-forms`: The form submission flow adds a legal-consent validation step. The `LeadSubmitSerializer` gains a new transient field (`terms`). The form template gains a new required checkbox. The admin notification email gains a row indicating consent was given (recommended, see design). No DB schema changes.

## Impact

- **Code**: `events/templates/events/form.html` — add checkbox markup + CSS. `events/serializers.py` — add `terms` field to serializer and validate it. `events/views.py` — potentially forward consent status to `send_event_emails` for the admin notification. `events/templates/events/emails/admin_notification.html` — optionally display consent row.
- **Tests**: Existing `LeadSubmitAPITestCase` tests must continue to pass. New tests: missing/unchecked `terms` returns 400; checked `terms` passes validation; checkbox is not stored on the Lead row.
- **Exports**: Zero impact. CSV/Excel export column schema (`lead-export` spec) only reads `Lead` model fields; the checkbox is not stored.
- **No migrations**, no new dependencies, no new endpoints, no iframe behavior changes, no DB schema changes.