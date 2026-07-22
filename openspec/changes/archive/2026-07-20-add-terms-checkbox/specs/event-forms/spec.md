## MODIFIED Requirements

### Requirement: JSON Lead Submission API with Honeypot Protection and Terms Consent
The system SHALL expose a public, CSRF-exempt JSON POST endpoint `/api/events/<slug>/submit/` to register lead submissions. If a hidden honeypot field is filled, the submission MUST be silently flagged or rejected to prevent spam. The submission MUST also include a boolean `terms` field that the user must set to `true` as acceptance of the event's terms and privacy policy. Submissions where `terms` is missing, `false`, or not a boolean MUST be rejected with a field-level validation error.

- The `terms` field MUST NOT be persisted to the `Lead` model. It MUST be validated and then discarded before the model `save()` call, following the same transient-field pattern as the `website` honeypot field.
- The validation error message for a missing or unchecked `terms` MUST read: `"Debe aceptar los Términos y Condiciones y el Aviso de Privacidad."`
- The admin notification email MAY include a row indicating `Aceptó términos` with the value `"Sí"` to provide the event organizer with evidence of consent.

#### Scenario: Lead submitted successfully with terms accepted
- **WHEN** a client sends a JSON POST request containing values for Name and Phone, leaving the honeypot field `website` empty
- **AND** the request includes `"terms": true`
- **THEN** the system registers a new `Lead` database record, returns a JSON success response `{"status": "ok"}`, and does not reload the page
- **AND** the resulting `Lead` row does not contain a `terms` column or any record of the terms acceptance value

#### Scenario: Submission rejected when terms is missing
- **WHEN** a client sends a JSON POST request containing valid values for all active required fields, but omits the `terms` key entirely
- **THEN** the system returns HTTP 400 with a field-level error `{"terms": ["Debe aceptar los Términos y Condiciones y el Aviso de Privacidad."]}`
- **AND** no `Lead` record is created

#### Scenario: Submission rejected when terms is false
- **WHEN** a client sends a JSON POST request containing valid values for all active required fields, but `"terms": false`
- **THEN** the system returns HTTP 400 with a field-level error on `terms`
- **AND** no `Lead` record is created

#### Scenario: Spam submission blocked by honeypot
- **WHEN** a bot submits a JSON POST request where the honeypot field `website` contains a value (e.g. "http://spam.org")
- **AND** the request includes `"terms": true` (bots can fill checkboxes)
- **THEN** the system flags the Lead as spam, prevents dispatching SMTP emails, and returns a simulated response to the client
- **AND** the `terms` value is still not persisted

## ADDED Requirements

### Requirement: Form Checkbox for Terms and Privacy Consent
The public event form at `/events/<slug>/` SHALL render a mandatory checkbox above the submit button with the label text **"He leído y acepto los Términos y Condiciones y el Aviso de Privacidad."** The entire spanned text (both document names) SHALL hyperlink to `https://www.leadforward.mx/legal` with `target="_blank"` and `rel="noopener noreferrer"`, styled as bold text.

- The checkbox SHALL use the HTML5 `required` attribute so browsers block submission client-side before the AJAX call.
- The error display pattern SHALL match the existing field-level error pattern (`form-group.has-error` + `.error-message`).
- The checkbox SHALL appear unconditionally — it is not controlled by any per-event field toggle on the `Event` model.

#### Scenario: Checkbox renders with bold linked label
- **WHEN** a client accesses the event form at `/events/<slug>/`
- **THEN** the HTML contains a checkbox input with `id="terms"` and `name="terms"`
- **AND** the adjacent label text contains the hyperlink `<a href="https://www.leadforward.mx/legal" target="_blank" rel="noopener noreferrer">`
- **AND** the label text reads verbatim: `He leído y acepto los Términos y Condiciones y el Aviso de Privacidad.`
- **AND** the label text is rendered in bold (`font-weight` of `700` or a `<strong>` equivalent)
- **AND** the checkbox group appears after the last conditional field and immediately above the submit button

#### Scenario: Checkbox error displayed inline
- **WHEN** a client submits the form without checking the checkbox
- **AND** the server returns 400 with a `terms` error
- **THEN** the checkbox group receives the `has-error` CSS class
- **AND** the corresponding `.error-message` element displays the validation text