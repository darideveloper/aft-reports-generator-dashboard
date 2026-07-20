# event-forms Specification

## Purpose
Defines how the events app creates configurable registration forms, renders them inside WordPress iframes, accepts lead submissions with anti-spam protections, and sends SMTP notifications with branded client confirmations. The app also supports an optional per-event invitation link that surfaces as a CTA in the client confirmation email and the post-submit success state of the form.
## Requirements
### Requirement: Event Creation and Configuration
The system SHALL allow administrators to create events in the admin panel with a custom URL slug and toggle the active/required status of predefined fields (Name, Job Position, Email, Phone, Company).
- All models, verbose names, help text, and field names in the admin dashboard MUST be presented in Spanish (es-mx) matching project localization conventions.
- The `Event` and `Lead` models MUST explicitly define `id = models.AutoField(primary_key=True)` as their primary key.
- The `Lead.job_position` field MUST be a standard free-text `CharField` allowing any arbitrary text inputs, not constrained to the project's internal `POSITION_CHOICES`.

#### Scenario: Admin creates and configures an event
- **WHEN** the admin creates an event with title "Conferencia Anual", slug "conferencia-anual-2026", and configures Name (active/required), Phone (active/optional), and Company (inactive)
- **THEN** the event configuration is saved, a public form page in Spanish becomes available at `/events/conferencia-anual-2026/`, and the dashboard displays the event in the side panel.

### Requirement: Form Rendering inside WordPress Iframes
The system SHALL render a responsive HTML form showing only active configured fields in Spanish using the corporate branding colors and displaying the company logo at the top of the form as configured in the system branding settings, and the view MUST be exempt from clickjacking protection (`X-Frame-Options`) to allow rendering inside WordPress iframes.

#### Scenario: Form view displays active fields and allows framing
- **WHEN** a client accesses the URL `/events/conferencia-anual-2026/`
- **THEN** the response includes the HTML page containing input fields in Spanish for Name and Phone, excludes the input for Company, omits the standard `X-Frame-Options: DENY` header, applies the corporate color scheme to interactive elements (inputs, buttons, success alerts) from the global branding configuration, and renders the corporate logo (`https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg`) at the top of the form.

### Requirement: Dynamic Iframe Resizing
The system SHALL broadcast the scroll height of the form page via JavaScript `postMessage` on load and window resize events, allowing the parent page to resize the iframe.

#### Scenario: Height update broadcasted to parent
- **WHEN** the event form page completes rendering or its window is resized
- **THEN** client-side JavaScript sends a `postMessage` containing the document scroll height with the message type `resize-iframe` to the parent window.

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

### Requirement: SMTP Auto-notifications with Error Resilience
Upon successful lead registration, the system SHALL send a notification email to the event's contact email and a branded thank-you confirmation email to the client using a globally configured SMTP server. 
- The client confirmation email MUST use the corporate color palette and display the company logo as configured in the system branding settings.
- The client confirmation email footer signature MUST read "El equipo LeadForward Global Solutions MJ".
- The email transmission operations MUST enforce a timeout constraint of 5 seconds.
- The form submission MUST succeed even if SMTP sending fails.

#### Scenario: Successful submission triggers emails
- **WHEN** a valid lead is registered via the submission API
- **THEN** the system triggers one email to the event organizer containing lead details and one email to the client's email address confirming their registration, styled with the corporate branding colors, the corporate logo resolved from settings, and containing the footer signature "El equipo LeadForward Global Solutions MJ".

#### Scenario: Database save succeeds despite SMTP failure
- **WHEN** a valid lead is submitted but the SMTP mail server connection fails or times out
- **THEN** the system successfully saves the `Lead` to the database, logs the SMTP error, and returns a JSON success response to the client.


### Requirement: Optional Event Invitation Link
The system MUST allow administrators to configure an optional invitation URL on each `Event` plus an optional button label, and the system MUST surface the resulting call-to-action (CTA) in two specific places and only in those two places: the client confirmation email and the post-submit success state of the public form.

The `Event` model MUST expose two new fields:
- `invitation_link`: a `URLField` with `max_length=500`, `blank=True`, `null=True`, restricted by a custom validator to the URL schemes `http` and `https` only. Any other scheme (including but not limited to `javascript`, `data`, `file`, `vbscript`, `ftp`) MUST be rejected at validation time.
- `invitation_label`: a `CharField` with `max_length=60`, `blank=True`, `default=""`. The label is optional; if blank, the CTA MUST use the default string `"Acceder al evento"`.

Visibility rules for the CTA:
- The CTA MUST be rendered in the client confirmation email only when `event.invitation_link` is truthy.
- The CTA MUST be rendered in the post-submit success state of the public form only when `event.invitation_link` is truthy.
- The CTA MUST NOT be rendered on the public form area above or below the form (pre-submit view).
- The CTA MUST NOT be rendered in the admin notification email.
- Events without an `invitation_link` MUST render no invitation CTA in any surface; their output MUST be byte-identical (in the relevant regions) to their pre-change output.

When the CTA is rendered, it MUST be a styled clickable button linking to `event.invitation_link` with `target="_blank"` and `rel="noopener noreferrer"`. In the client email, the raw URL MUST also appear as plain-text fallback directly below the button so that email clients which strip buttons still expose a clickable link. In the post-submit iframe state, the CTA MUST be revealed by JavaScript only after a `201` response from the submission endpoint, and MUST never be visible before submission.

The default label string `"Acceder al evento"` is a project-level default, defined in the templates and tests, and MUST be applied whenever `invitation_label` is empty or whitespace.

The migration that introduces the two fields MUST be purely additive: nullable, no data backfill, fully backward compatible with existing events.

#### Scenario: Event with invitation link and custom label — email contains CTA with custom label and raw URL fallback
- **WHEN** an event has `invitation_link="https://zoom.us/j/123?pwd=abc"` and `invitation_label="Ver grabación"`
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email HTML contains an `<a>` element whose `href` equals `https://zoom.us/j/123?pwd=abc`, with `target="_blank"` and `rel="noopener noreferrer"`, displaying the text `Ver grabación`
- **AND** the email HTML also contains the raw URL `https://zoom.us/j/123?pwd=abc` as plain text below the button
- **AND** the admin notification email contains no reference to the invitation URL or label

#### Scenario: Event with invitation link but no custom label — email uses default label
- **WHEN** an event has `invitation_link="https://zoom.us/j/123"` and `invitation_label=""`
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email HTML contains a button displaying the default text `Acceder al evento` and pointing to `https://zoom.us/j/123`
- **AND** the raw URL appears as plain text below the button

#### Scenario: Event without invitation link — no CTA in email
- **WHEN** an event has no `invitation_link` (NULL or empty)
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email contains no `Acceder al evento` button, no `href` referencing the URL, and no fallback plain-text URL paragraph

#### Scenario: Event with invitation link — post-submit iframe state shows CTA
- **WHEN** a client submits a lead to an event with `invitation_link="https://zoom.us/j/123"` and `invitation_label="Unirse ahora"`
- **AND** the server responds with HTTP 201
- **THEN** the form is hidden and the success state is shown
- **AND** an invitation CTA element is revealed in the success state
- **AND** that CTA's `href` equals `https://zoom.us/j/123`, has `target="_blank"` and `rel="noopener noreferrer"`, and displays the text `Unirse ahora`

#### Scenario: Event with invitation link and default label — post-submit iframe state uses default label
- **WHEN** a lead submission returns 201 for an event with `invitation_link` set and `invitation_label` blank
- **THEN** the post-submit invitation CTA displays the default text `Acceder al evento`

#### Scenario: Event without invitation link — post-submit iframe state shows no CTA
- **WHEN** a lead submission returns 201 for an event with no `invitation_link`
- **THEN** the form is hidden and the success state is shown
- **AND** no invitation CTA element is present or revealed in the DOM

#### Scenario: Invitation link with non-http(s) scheme is rejected at validation
- **WHEN** an administrator saves an event with `invitation_link="javascript:alert(1)"`
- **THEN** the form fails validation with a field-level error on `invitation_link` stating the URL must be a valid http(s) URL
- **AND** the event is NOT saved

#### Scenario: Invitation link with valid http(s) URL is accepted
- **WHEN** an administrator saves an event with `invitation_link="https://zoom.us/j/123?pwd=abc&utm_source=mail"`
- **THEN** the event is saved successfully with that URL stored verbatim
- **AND** both the email CTA `href` and the iframe CTA `href` equal that exact URL

#### Scenario: Long URL with tracking parameters fits within the 500-character limit
- **WHEN** an administrator saves an event with an `invitation_link` of 480 characters containing `https://`, a path, a query string, and UTM parameters
- **THEN** the event is saved successfully and the URL is delivered intact in both the email and the iframe CTA

#### Scenario: Spam submission does not reveal the CTA via the email channel
- **WHEN** a bot submission triggers the honeypot and the lead is saved with `is_spam=True`
- **THEN** no client confirmation email is sent
- **AND** the CTA does not reach the attendee via email

#### Scenario: Migration is fully backward compatible
- **WHEN** the migration introducing `invitation_link` and `invitation_label` is applied to a database that already contains events
- **THEN** all existing events are preserved with `invitation_link=NULL` and `invitation_label=""`
- **AND** rendering any existing event in the email or iframe surface produces no invitation CTA
- **AND** the migration is reversible by running the reverse operation

#### Scenario: Admin edit form exposes both new fields
- **WHEN** an administrator opens the event edit page at `/admin/events/event/<id>/change/`
- **THEN** the page contains an input named `invitation_link` and an input named `invitation_label`
- **AND** the labels rendered next to those inputs read `Enlace de invitación` and `Texto del botón de invitación` respectively
- **AND** saving the form with a new value persists that value to the database

#### Scenario: Admin list view renders the invitation link as a clickable element
- **WHEN** an administrator opens the event list page at `/admin/events/event/`
- **THEN** the row for an event with `invitation_link` set contains a clickable `<a>` element whose `href` equals that URL, with `target="_blank"` and `rel="noopener noreferrer"`
- **AND** the row for an event without `invitation_link` displays the placeholder `—` (em-dash) for that column, with no `<a>` element
