## MODIFIED Requirements

### Requirement: Validate SMTP configuration and credentials
The system SHALL provide a test endpoint at `/tests/validate-email/` to allow checking SMTP health.

#### Scenario: Successful connection verification (Emulated mode)
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with a valid JSON body containing a valid `token` and no `real` field or `real` set to false
- **THEN** the system SHALL attempt to open and close the SMTP connection without sending a real email, and return an HTTP `200 OK` response with a JSON payload indicating success and emulated status.

#### Scenario: Successful test email dispatch (Real mode)
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with a valid JSON body containing a valid `token`, `real` set to true, and a valid destination `email` field
- **THEN** the system SHALL attempt to establish the SMTP connection, dispatch a real test email to the recipient, close the connection, and return an HTTP `200 OK` response with a JSON payload indicating success and real status.

#### Scenario: Missing or invalid token
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with an invalid token or missing `token` field in the JSON body
- **THEN** the system SHALL return an HTTP `403 Forbidden` response with a JSON payload indicating an authentication error.

#### Scenario: Missing recipient email for real send
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with a valid JSON body containing a valid `token` and `real` set to true, but without the `email` field
- **THEN** the system SHALL return an HTTP `400 Bad Request` response with a JSON payload indicating that the destination email is required.

#### Scenario: SMTP connection failure
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with a valid JSON body containing a valid token, and the SMTP host connection or authentication fails
- **THEN** the system SHALL catch the exception, log it, and return an HTTP `500 Internal Server Error` response with a JSON payload containing the error message.

#### Scenario: Invalid JSON payload
- **WHEN** a client performs a `POST` request to `/tests/validate-email/` with a malformed or non-JSON body
- **THEN** the system SHALL return an HTTP `400 Bad Request` response with a JSON payload indicating that the request body must be valid JSON.
