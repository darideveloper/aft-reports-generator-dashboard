## ADDED Requirements

### Requirement: Client Confirmation Email Body Format
The system SHALL render the client confirmation email using a concise, fixed body format when `event.email_active` is true and the lead has a non-empty email address. The email MUST greet the lead by name, confirm the event title in bold, express appreciation, and provide a contact line. The format MUST match the exact structure below, with placeholders substituted at send time.

#### Scenario: Client confirmation email uses the new concise format
- **WHEN** a valid lead with name "Ana García" and email "ana@example.com" is submitted to an event titled "WEBINAR | PULSO Digital"
- **THEN** the client confirmation email HTML body contains the following sequence of rendered text blocks:
  - A heading reading "¡Gracias por registrarte!"
  - A greeting line reading "Hola Ana García"
  - A confirmation line reading "Queremos confirmarte que hemos recibido exitosamente tus datos para el evento: WEBINAR | PULSO Digital" with the event title rendered in bold
  - A line reading "Agradecemos tu interés en participar."
  - A line reading "Si tienes alguna duda, por favor ponte en contacto con nosotros respondiendo a este mensaje."

#### Scenario: Client confirmation email omits the legacy future-updates sentence
- **WHEN** a valid lead is submitted to any event
- **THEN** the client confirmation email body MUST NOT contain the text "Estaremos compartiendo más detalles y novedades del evento próximamente a través de esta dirección de correo electrónico."

#### Scenario: Client confirmation email falls back when lead name is missing
- **WHEN** a valid lead without a name is submitted to an event titled "Conferencia Anual"
- **THEN** the greeting line reads "Hola participante" or equivalent fallback text
- **AND** the confirmation line still renders the event title "Conferencia Anual" in bold

#### Scenario: Existing branding, logo, invitation CTA, and footer are preserved
- **WHEN** a valid lead is submitted to an event configured with branding colors, a logo, and an invitation link
- **THEN** the email continues to apply the corporate primary color to the top border and heading
- **AND** the logo is rendered at the top when configured
- **AND** the invitation-link CTA button and raw-URL fallback appear in the same position and style as before
- **AND** the footer continues to display "Saludos cordiales, El equipo LeadForward Global Solutions MJ"

## MODIFIED Requirements

### Requirement: SMTP Auto-notifications with Error Resilience
Upon successful lead registration, the system SHALL send a notification email to the event's contact email and a branded thank-you confirmation email to the client using a globally configured SMTP server. 
- The client confirmation email MUST use the corporate color palette and display the company logo as configured in the system branding settings.
- The client confirmation email footer signature MUST read "El equipo LeadForward Global Solutions MJ".
- The client confirmation email body MUST follow the concise format defined in the "Client Confirmation Email Body Format" requirement.
- The email transmission operations MUST enforce a timeout constraint of 5 seconds.
- The form submission MUST succeed even if SMTP sending fails.

#### Scenario: Successful submission triggers emails
- **WHEN** a valid lead is registered via the submission API
- **THEN** the system triggers one email to the event organizer containing lead details and one email to the client's email address confirming their registration, styled with the corporate branding colors, the corporate logo resolved from settings, containing the footer signature "El equipo LeadForward Global Solutions MJ", and using the concise client confirmation body format.

#### Scenario: Database save succeeds despite SMTP failure
- **WHEN** a valid lead is submitted but the SMTP mail server connection fails or times out
- **THEN** the system successfully saves the `Lead` to the database, logs the SMTP error, and returns a JSON success response to the client.
