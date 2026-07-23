## ADDED Requirements

### Requirement: Event administrators can configure event date, time and duration
The `Event` model SHALL include `event_datetime` (nullable `DateTimeField`) and `duration_minutes` (nullable `PositiveSmallIntegerField`, default 0) fields. These fields SHALL be added to the explicit `fieldsets` in `EventAdmin` so they appear in the admin form. The migration adding these fields SHALL be fully backward compatible.

#### Scenario: Admin configures event date and duration
- **WHEN** an administrator edits an event in the admin panel
- **THEN** the form contains a datetime input for `event_datetime` labeled "Fecha y hora del evento"
- **AND** a number input for `duration_minutes` labeled "Duración (minutos)"
- **AND** both fields are placed in the first admin fieldset (general event info)
- **AND** saving the form with new values persists them to the database

#### Scenario: Migration is backward compatible
- **WHEN** the migration is applied to a database with existing events
- **THEN** all existing events have `event_datetime=NULL` and `duration_minutes=0`
- **AND** the migration can be rolled back

### Requirement: Model validation for event date and duration
The Event model SHALL implement a `clean()` method that validates `duration_minutes > 0` when `event_datetime` is set. This validation SHALL be enforced on all save operations through the admin form.

#### Scenario: Validation rejects zero duration when datetime is set
- **WHEN** an administrator sets `event_datetime` to a valid future datetime
- **AND** sets `duration_minutes` to 0
- **THEN** the form fails validation with a field-level error on `duration_minutes`
- **AND** the event is NOT saved

#### Scenario: Empty duration is allowed when no datetime is set
- **WHEN** an administrator sets `event_datetime` to NULL or empty
- **AND** `duration_minutes` is 0
- **THEN** the event saves successfully

### Requirement: Absolute access URL is built in Python for emails
The `send_event_emails()` function SHALL build an absolute URL for the access page using `reverse('events:event-access')` and the same host/protocol resolution logic used for `logo_url`. This absolute URL SHALL be passed as `access_url` in the email template context. The raw `invitation_link` SHALL NOT be exposed in the email body HTML.

#### Scenario: Email contains absolute access URL
- **WHEN** a valid lead is submitted to an event with `invitation_link` and `event_datetime` set
- **THEN** the email template context includes `access_url` as a full `https://` URL
- **AND** the CTA button in the email links to the absolute `access_url`
- **AND** the raw `invitation_link` does not appear anywhere in the email HTML

## MODIFIED Requirements

### Requirement: Optional Event Invitation Link
The system MUST allow administrators to configure an optional invitation URL on each `Event` plus an optional button label, and the system MUST surface the resulting call-to-action (CTA) through an intermediate access gate page at `/events/<slug>/access/` that validates the event time before revealing the link. The CTA SHALL NOT link directly to the invitation URL — all CTA links in the client confirmation email and post-submit form state SHALL point to `/events/<slug>/access/`.

The `Event` model fields:
- `invitation_link`: a `URLField` with `max_length=500`, `blank=True`, `null=True`, restricted to `http`/`https` schemes.
- `invitation_label`: a `CharField` with `max_length=60`, `blank=True`, `default=""`. Falls back to `"Acceder al evento"` when blank.
- `event_datetime`: a nullable `DateTimeField` for the event start time.
- `duration_minutes`: a `PositiveSmallIntegerField`, default 0, for event duration in minutes.

Visibility rules for the CTA:
- The intermediate access URL MUST be rendered in the client confirmation email only when `event.invitation_link` is truthy and `event.event_datetime` is not null.
- The intermediate access URL MUST be rendered in the post-submit success state of the public form only when `event.invitation_link` is truthy and `event.event_datetime` is not null.
- The CTA MUST NOT be rendered on the public form pre-submit view.
- The CTA MUST NOT be rendered in the admin notification email.
- The CTA MUST NOT link directly to `event.invitation_link` in any surface — it MUST link to `/events/<slug>/access/`.
- The link button text MUST default to `"Acceder al evento"` when `invitation_label` is empty, but the access page MAY override this with contextually appropriate text (e.g., "Entrar al evento" when the event is starting).

#### Scenario: Event with invitation link — email CTA points to access page
- **WHEN** an event has `invitation_link="https://zoom.us/j/123"`, `event_datetime` set, and `invitation_label="Unirse ahora"`
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email contains a button with text `Unirse ahora`
- **AND** the button's `href` equals the intermediate access URL `/events/<slug>/access/` (not the raw Zoom URL)
- **AND** the raw Zoom URL does NOT appear as visible text in the email

#### Scenario: Event without invitation link — no CTA in email
- **WHEN** an event has no `invitation_link` (NULL or empty)
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email contains no invitation CTA button, no access URL, and no raw URL

#### Scenario: Event without event_datetime — no CTA in email
- **WHEN** an event has `invitation_link` set but `event_datetime` is NULL
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email contains no invitation CTA button or access URL

#### Scenario: Event with invitation link — post-submit form state links to access page
- **WHEN** a client submits a lead to an event with `invitation_link` set and `event_datetime` set
- **AND** the server responds with HTTP 201
- **THEN** the form is hidden and the success state is shown
- **AND** the post-submit CTA button points to `/events/<slug>/access/` (not the raw invitation URL)

#### Scenario: Event without invitation link — post-submit form state shows no CTA
- **WHEN** a lead submission returns 201 for an event with no `invitation_link`
- **THEN** no invitation CTA is shown in the success state

#### Scenario: Spam submission does not reveal the access URL via email
- **WHEN** a bot submission triggers the honeypot
- **THEN** no client confirmation email is sent and the access URL is not distributed

### Requirement: Client Confirmation Email Body Format
The system SHALL render the client confirmation email using a concise, fixed body format when `event.email_active` is true and the lead has a non-empty email address. The email MUST greet the lead by name, confirm the event title in bold, express appreciation, and provide a contact line. If the event has `invitation_link` and `event_datetime` both set, a CTA button linking to the absolute access URL (`access_url` from Python context) SHALL appear in the email. The raw invitation URL SHALL NOT appear in the email body.

#### Scenario: Client confirmation email uses the concise format
- **WHEN** a valid lead with name "Ana García" and email "ana@example.com" is submitted to an event titled "WEBINAR | PULSO Digital"
- **THEN** the client confirmation email HTML body contains the following sequence:
  - A heading reading "¡Gracias por registrarte!"
  - A greeting line reading "Hola Ana García"
  - A confirmation line reading "Queremos confirmarte que hemos recibido exitosamente tus datos para el evento: WEBINAR | PULSO Digital" with the event title in bold
  - A line reading "Agradecemos tu interés en participar."
  - A line reading "Si tienes alguna duda, por favor ponte en contacto con nosotros respondiendo a este mensaje."

#### Scenario: Client confirmation email omits the legacy future-updates sentence
- **WHEN** a valid lead is submitted to any event
- **THEN** the client confirmation email body MUST NOT contain "Estaremos compartiendo más detalles y novedades del evento próximamente a través de esta dirección de correo electrónico."

#### Scenario: Client confirmation email falls back when lead name is missing
- **WHEN** a valid lead without a name is submitted
- **THEN** the greeting line reads "Hola participante"
- **AND** the confirmation line still renders the event title in bold

#### Scenario: Client confirmation email with access CTA when event is configured
- **WHEN** a valid lead is submitted to an event configured with `invitation_link`, `event_datetime`, branding colors, and a logo
- **THEN** the email applies the corporate primary color to the top border and heading
- **AND** the logo is rendered at the top
- **AND** a CTA button is shown linking to the absolute `access_url` with `target="_blank"` and `rel="noopener noreferrer"`
- **AND** the raw invitation link URL is NOT rendered in the email body
- **AND** the footer displays "Saludos cordiales, El equipo LeadForward Global Solutions MJ"

#### Scenario: Client confirmation email without CTA when event has no date
- **WHEN** a valid lead is submitted to an event with `invitation_link` set but `event_datetime` is NULL
- **THEN** the client confirmation email contains no CTA button and no access URL
