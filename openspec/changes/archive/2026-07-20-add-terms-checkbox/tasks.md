## 1. Serializer — add `terms` field and validation

- [x] 1.1 Add `terms = serializers.BooleanField(required=True, write_only=True)` to `LeadSubmitSerializer` in `events/serializers.py`
- [x] 1.2 In `LeadSubmitSerializer.validate()`, after the field-config loop and before the honeypot pop, add: `if not attrs.get("terms"): raise ValidationError({"terms": "Debe aceptar los Términos y Condiciones y el Aviso de Privacidad."})`
- [x] 1.3 Pop `attrs.pop("terms", None)` after validation (alongside the existing `attrs.pop("website", None)`)

## 2. Form template — add checkbox markup

- [x] 2.1 Add a `<div class="form-group terms-group">` block in `events/templates/events/form.html` after the last conditional field (company) and before the submit button
- [x] 2.2 Inside it, render: `<input type="checkbox" name="terms" id="terms" required>` with a `<label>` wrapping it and a `<span>` containing the linked bold text: `He leído y acepto los <a href="https://www.leadforward.mx/legal" target="_blank" rel="noopener noreferrer">Términos y Condiciones y el Aviso de Privacidad</a>.`
- [x] 2.3 Add a sibling `<div class="error-message" id="error-terms"></div>` for inline validation errors (matches the existing per-field pattern)
- [x] 2.4 Add CSS for `.terms-group`, `.terms-label`, and `.terms-group.has-error` — consistent spacing and bold font-weight

## 3. Admin notification email — add consent row (optional, per design)

- [x] 3.1 Modify `events/views.py:send_event_emails(lead)` to accept and forward a `terms_accepted=True` parameter, or hardcode `True` in the admin email context since unchecked submissions are rejected server-side
- [x] 3.2 Add a row to `events/templates/events/emails/admin_notification.html`: `<tr><th>Aceptó términos</th><td>Sí</td></tr>` (unconditional — all successful submissions have consent)

## 4. Tests

- [x] 4.1 Test: submitting with `"terms": true` passes validation (extends existing `LeadSubmitAPITestCase.test_successful_lead_submission`)
- [x] 4.2 Test: submitting without `terms` key returns 400 with a field-level error on `terms`
- [x] 4.3 Test: submitting with `"terms": false` returns 400
- [x] 4.4 Test: verifying `terms` is not stored on the `Lead` row (query DB after successful submission, assert no `terms` attribute)
- [x] 4.5 Test: spam submission (honeypot triggered) with `"terms": true` still saves as spam and does not persist `terms`

## 5. Validation

- [x] 5.1 Run `python manage.py test events` — all events tests green (43 tests, +2 new)
- [x] 5.2 Confirm no migrations were generated (`python manage.py makemigrations events --dry-run` → "No changes detected")
- [x] 5.3 Confirm `requirements.txt` is unchanged
- [x] 5.4 Confirm existing CSV/Excel exports (`lead-export`) are unaffected by running `python manage.py test events.tests.LeadExportActionsTestCase` (11 tests pass)