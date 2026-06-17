## ADDED Requirements

### Requirement: Validate SMTP configuration and credentials
The system SHALL provide a test endpoint at `/tests/validate-email/` to allow checking SMTP health.

#### Scenario: Successful connection verification (Emulated mode)
- **WHEN** a client performs a `GET` request to `/tests/validate-email/` with a valid `token` query parameter and no `real` parameter or `real=false`
- **THEN** the system SHALL attempt to open and close the SMTP connection without sending a real email, and return a HTTP `200 OK` response with a JSON payload indicating success and emulated status.

#### Scenario: Successful test email dispatch (Real mode)
- **WHEN** a client performs a `GET` request to `/tests/validate-email/` with a valid `token` query parameter, `real=true`, and a valid destination `email` query parameter
- **THEN** the system SHALL attempt to establish the SMTP connection, dispatch a real test email to the recipient, close the connection, and return a HTTP `200 OK` response with a JSON payload indicating success and real status.

#### Scenario: Missing or invalid token
- **WHEN** a client performs a `GET` request to `/tests/validate-email/` with an invalid token or missing `token` parameter
- **THEN** the system SHALL return a HTTP `403 Forbidden` response with a JSON payload indicating an authentication error.

#### Scenario: Missing recipient email for real send
- **WHEN** a client performs a `GET` request to `/tests/validate-email/` with a valid `token` query parameter, `real=true`, but without the `email` query parameter
- **THEN** the system SHALL return a HTTP `400 Bad Request` response with a JSON payload indicating that the destination email is required.

#### Scenario: SMTP connection failure
- **WHEN** a client performs a `GET` request to `/tests/validate-email/` with a valid token, and the SMTP host connection or authentication fails
- **THEN** the system SHALL catch the exception, log it, and return a HTTP `500 Internal Server Error` response with a JSON payload containing the error message.
