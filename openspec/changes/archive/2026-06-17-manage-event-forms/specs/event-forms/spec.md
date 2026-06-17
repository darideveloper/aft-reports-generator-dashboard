## ADDED Requirements

### Requirement: Event Creation and Configuration
The system SHALL allow administrators to create events in the admin panel with a custom URL slug and toggle the active/required status of predefined fields (Name, Job Position, Email, Phone, Company).
- All models, verbose names, help text, and field names in the admin dashboard MUST be presented in Spanish (es-mx) matching project localization conventions.
- The `Event` and `Lead` models MUST explicitly define `id = models.AutoField(primary_key=True)` as their primary key.
- The `Lead.job_position` field MUST be a standard free-text `CharField` allowing any arbitrary text inputs, not constrained to the project's internal `POSITION_CHOICES`.

#### Scenario: Admin creates and configures an event
- **WHEN** the admin creates an event with title "Conferencia Anual", slug "conferencia-anual-2026", and configures Name (active/required), Phone (active/optional), and Company (inactive)
- **THEN** the event configuration is saved, a public form page in Spanish becomes available at `/events/conferencia-anual-2026/`, and the dashboard displays the event in the side panel.

### Requirement: Form Rendering inside WordPress Iframes
The system SHALL render a responsive HTML form showing only active configured fields in Spanish, and the view MUST be exempt from clickjacking protection (`X-Frame-Options`) to allow rendering inside WordPress iframes.

#### Scenario: Form view displays active fields and allows framing
- **WHEN** a client accesses the URL `/events/conferencia-anual-2026/`
- **THEN** the response includes the HTML page containing input fields in Spanish for Name and Phone, excludes the input for Company, and omits the standard `X-Frame-Options: DENY` header.

### Requirement: Dynamic Iframe Resizing
The system SHALL broadcast the scroll height of the form page via JavaScript `postMessage` on load and window resize events, allowing the parent page to resize the iframe.

#### Scenario: Height update broadcasted to parent
- **WHEN** the event form page completes rendering or its window is resized
- **THEN** client-side JavaScript sends a `postMessage` containing the document scroll height with the message type `resize-iframe` to the parent window.

### Requirement: JSON Lead Submission API with Honeypot Protection
The system SHALL expose a public, CSRF-exempt JSON POST endpoint `/api/events/<slug>/submit/` to register lead submissions. If a hidden honeypot field is filled, the submission MUST be silently flagged or rejected to prevent spam.

#### Scenario: Lead submitted successfully via AJAX
- **WHEN** a client sends a JSON POST request containing values for Name and Phone, leaving the honeypot field `website` empty
- **THEN** the system registers a new `Lead` database record, returns a JSON success response `{"status": "ok"}`, and does not reload the page.

#### Scenario: Spam submission blocked by honeypot
- **WHEN** a bot submits a JSON POST request where the honeypot field `website` contains a value (e.g. "http://spam.org")
- **THEN** the system rejects the submission or flags the Lead as spam, prevents dispatching SMTP emails, and returns a simulated response to the client.

### Requirement: SMTP Auto-notifications with Error Resilience
Upon successful lead registration, the system SHALL send a notification email to the event's contact email and a thank-you confirmation email to the client using a globally configured SMTP server. 
- The email transmission operations MUST enforce a timeout constraint of 5 seconds.
- The form submission MUST succeed even if SMTP sending fails.

#### Scenario: Successful submission triggers emails
- **WHEN** a valid lead is registered via the submission API
- **THEN** the system triggers one email to the event organizer containing lead details and one email to the client's email address confirming their registration.

#### Scenario: Database save succeeds despite SMTP failure
- **WHEN** a valid lead is submitted but the SMTP mail server connection fails or times out
- **THEN** the system successfully saves the `Lead` to the database, logs the SMTP error, and returns a JSON success response to the client.
