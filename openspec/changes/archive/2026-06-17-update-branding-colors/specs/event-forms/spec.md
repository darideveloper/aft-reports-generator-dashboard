## MODIFIED Requirements

### Requirement: Form Rendering inside WordPress Iframes
The system SHALL render a responsive HTML form showing only active configured fields in Spanish using the corporate branding colors and displaying the company logo at the top of the form as configured in the system branding settings, and the view MUST be exempt from clickjacking protection (`X-Frame-Options`) to allow rendering inside WordPress iframes.

#### Scenario: Form view displays active fields and allows framing
- **WHEN** a client accesses the URL `/events/conferencia-anual-2026/`
- **THEN** the response includes the HTML page containing input fields in Spanish for Name and Phone, excludes the input for Company, omits the standard `X-Frame-Options: DENY` header, applies the corporate color scheme to interactive elements (inputs, buttons, success alerts) from the global branding configuration, and renders the corporate logo (`https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg`) at the top of the form.

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
