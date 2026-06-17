## Why

The SMTP validation endpoint currently accepts HTTP GET requests with query parameters. Converting it to HTTP POST with a JSON body is more secure, follows REST best practices for endpoints that trigger actions, and avoids exposing tokens or emails in browser history, proxy logs, or web server access logs.

## What Changes

- Change the HTTP method of the SMTP validation endpoint from `GET` to `POST`.
- **BREAKING**: Change the data input format from URL query parameters (`?token=...&real=...&email=...`) to a JSON request body (`{"token": "...", "real": ..., "email": "..."}`).
- Validate incoming JSON format and reject requests with invalid JSON, missing required fields, or invalid parameter types.

## Capabilities

### New Capabilities

### Modified Capabilities

- `smtp-validation`: Update the SMTP validation requirement to use HTTP POST with a JSON payload instead of HTTP GET with query parameters.

## Impact

- `core/views.py`: Modify `ValidateEmailView` to handle `POST` requests and extract parameters from `request.data` instead of `request.query_params`.
- `core/tests.py`: Update the test cases to perform `POST` requests with JSON payloads and test the updated validation logic.
- `project/urls.py`: The URL pattern `/tests/validate-email/` remains the same but will only allow `POST` requests.
