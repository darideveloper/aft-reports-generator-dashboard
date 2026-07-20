## Context

The public event form at `events/templates/events/form.html` is rendered via `EventFormView` (iframe-embeddable) and submitted via `fetch()` to `LeadSubmitView` at `POST /api/events/<slug>/submit/`. The `LeadSubmitSerializer` in `events/serializers.py` validates the incoming JSON, pops the honeypot `website` field, and saves the `Lead` model instance.

There is currently no legal consent step. The form collects name, email, phone, etc. and immediately sends them to the server. Adding a required "I accept terms" checkbox is the minimum change needed for regulatory compliance without altering the data model.

The project already has a `website` honeypot field in the serializer that follows the validate→pop pattern — the terms checkbox will follow the same structural pattern, just with different validation (must be truthy vs. must be falsy).

## Goals / Non-Goals

**Goals:**
- Add a mandatory checkbox to the form with the label text **"He leído y acepto los Términos y Condiciones y el Aviso de Privacidad."** linking to `https://www.leadforward.mx/legal`.
- Reject submissions where the checkbox is unchecked or absent with a 400 + field-level error in Spanish.
- Persist nothing new — the `Lead` model stays unchanged.
- Existing CSV/Excel exports (`lead-export`) are unaffected.
- All existing tests pass without modification.

**Non-Goals:**
- No DB migration, no new model field, no new column on Lead.
- No change to the client confirmation email.
- No change to the iframe embed behavior or postMessage resizing.
- No change to the Event model (no toggle to enable/disable the checkbox — it's always present).
- No change to the invitation link CTA or post-submit success state.

## Decisions

### Decision 1: Checkbox rendering — bold label linking to a single URL

**Choice:** Render a single checkbox with a `<label>` wrapping the `<input>`. The label text is **"He leído y acepto los Términos y Condiciones y el Aviso de Privacidad."** where the entire spanned text is a single hyperlink to `https://www.leadforward.mx/legal`. The text is bold (`font-weight: 700`).

The existing form CSS uses custom properties (`--text-main`, `--primary`, etc.) — the label will use the same font stack and color as other labels.

Placement: after the last conditional field group (company) and before the submit button, matching the visual flow.

The markup structure:
```html
<div class="form-group terms-group">
    <label class="terms-label" for="terms">
        <input type="checkbox" name="terms" id="terms" required>
        <span>He leído y acepto los <a href="https://www.leadforward.mx/legal" target="_blank" rel="noopener noreferrer">Términos y Condiciones y el Aviso de Privacidad</a>.</span>
    </label>
</div>
```

### Decision 2: Serializer — `BooleanField(required=True, write_only=True)`

**Choice:** Add `terms = serializers.BooleanField(required=True, write_only=True)` to `LeadSubmitSerializer`.

In `validate()`, after the existing field config loop and honeypot pop, check `attrs.get("terms")` is truthy. If not, raise `ValidationError({"terms": "Debe aceptar los Términos y Condiciones y el Aviso de Privacidad."})`.

Pop `terms` from `attrs` before returning, same as `website`. The model `create()` never sees it.

**Alternative considered:** storing it on the Lead model. Rejected — the checkbox is purely a consent gate at submission time; no downstream consumer reads it. Storing adds column overhead, migration, and export noise for zero value.

**Alternative considered:** frontend-only validation with no server check. Rejected — a bot can bypass DOM-based validation. Server-side check is required for legal defense.

### Decision 3: Admin notification email — optionally display consent

**Choice:** Show a `"Aceptó términos"` row in the admin notification email (`admin_notification.html`). The value is hardcoded as `"Sí"` when the submission passes validation (since unchecked submissions are rejected, every successful submission has consent).

Implementation: pass an additional context variable like `terms_accepted=True` from `views.py:send_event_emails()`. The template conditionally renders a row:
```html
<tr><th>Aceptó términos</th><td>Sí</td></tr>
```

**Alternative considered:** don't modify the email. Rejected — the admin user (event organizer) should see that the lead gave consent; it's the only record outside the server logs.

**Alternative considered:** pass the raw checkbox value through the `Lead` instance. Not possible since we're not storing it. Explicit parameter is cleaner.

### Decision 4: Error display — inline field error matching existing pattern

**Choice:** The checkbox error follows the same JS pattern as other fields:
- Django template (`form.html`) renders an `.error-message` div next to the checkbox.
- The JS fetch handler in `form.html:319-331` already iterates `result.errors` keys and sets field-level errors by `document.getElementById('group-${field}')`. Since the key will be `"terms"`, the pattern works automatically with `id="group-terms"` and `id="error-terms"`.

No changes needed to the form JS — it's already generic over error keys.

### Decision 5: Checkbox required attribute in HTML

**Choice:** Add HTML5 `required` attribute to the checkbox input. Browsers will prevent form submission without checking the box as a first line of defense. The server-side validation catches cases where `required` is stripped (e.g., curl, Postman, bots).

## Risks / Trade-offs

- **[One link for two documents]** The URL `https://www.leadforward.mx/legal` serves both terms and privacy together. If the legal team later splits them into separate URLs, the checkbox text and link will need updating. → Mitigation: the copy is in a single place (the template); updating is straightforward.
- **[No audit trail]** Since the checkbox value isn't stored, there is no per-lead record that "this specific lead accepted terms at this timestamp." If an auditor needs proof, only the server log (if DEBUG) or the admin notification email (if SMTP is reliable) can provide it. → Mitigation: the admin notification email now carries the consent row. For stricter compliance, the checkbox could be stored — but the user explicitly opted out. Acceptable for the current requirement.
- **[CSV/Export isolation]** Zero risk here. The proposal and design explicitly isolate the checkbox from the `lead-export` capability. Regression tests on exports cover that gap.

## Migration Plan

1. Add checkbox markup to `events/templates/events/form.html` after the last conditional field, before the submit button.
2. Add CSS for the checkbox styling (bold label, consistent spacing).
3. Add `terms` field to `LeadSubmitSerializer` (`events/serializers.py`), validate, pop.
4. Optionally modify `events/views.py:send_event_emails()` to pass `terms_accepted=True` and update `admin_notification.html`.
5. Update tests — existing `LeadSubmitAPITestCase` must still pass; add new tests covering: unchecked `terms` → 400, checked `terms` → 201, `terms` not stored on Lead row.
6. Run `python manage.py test events` to confirm green.
7. Deploy: no migrations, no env changes. Pure template + serializer change.
8. Rollback: revert the single commit. Exports are untouched by the revert.