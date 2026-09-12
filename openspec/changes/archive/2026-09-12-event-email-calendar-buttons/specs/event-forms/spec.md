## ADDED Requirements

### Requirement: Client confirmation email calendar integration
The system SHALL extend the client confirmation email with the `email-calendar-invite` calendar section and `.ics` attachment whenever the Event has `event_datetime` set, independent of the access CTA visibility rules. All existing body format, branding, logo, signature, and SMTP resilience requirements remain unchanged.

#### Scenario: Email with datetime includes both access CTA and calendar
- **WHEN** a lead is submitted to an event with `invitation_link` and `event_datetime` set
- **THEN** the client HTML contains the access CTA linking to the absolute `access_url` AND the `Agregar a tu calendario:` section with attachment

#### Scenario: Email with datetime but no invitation link includes only calendar
- **WHEN** a lead is submitted to an event with `event_datetime` set but no `invitation_link`
- **THEN** the client HTML contains the calendar section with attachment but no access CTA

#### Scenario: Spam submission still sends no email
- **WHEN** a honeypot-flagged submission is saved with `is_spam=True`
- **THEN** no client email (and therefore no calendar section or attachment) is sent
