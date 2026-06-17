## Context

The system has an HTTP GET endpoint at `/tests/validate-email/` to validate SMTP connection settings and credentials. This endpoint is public (no authentication/permission classes), but enforces a security token check. Exposure of this token and potential test email addresses in URL query parameters poses security risks (e.g. leaking in access logs, browser history, proxies). Converting the endpoint to HTTP POST with a JSON body mitigates these concerns.

## Goals / Non-Goals

**Goals:**
- Update `/tests/validate-email/` to accept HTTP POST requests only.
- Parse `token`, `real`, and `email` parameters from the JSON request body instead of query parameters.
- Provide clear error handling for invalid or malformed JSON payloads.

**Non-Goals:**
- Changing actual SMTP handshake/delivery logic.
- Adding database-backed authentication/authorization to this monitoring endpoint.

## Decisions

### 1. HTTP Method transition to POST
- **Decision**: Reject GET requests on `/tests/validate-email/` and only allow POST.
- **Rationale**: GET requests should not carry sensitive parameters like tokens in the URL. POST requests transfer data in the request body, which is encrypted in transit under HTTPS and not logged in standard web server access logs.

### 2. Handling DRF request.data ParseError
- **Decision**: Catch `ParseError` raised when accessing `request.data` on a malformed JSON payload and return HTTP 400.
- **Rationale**: DRF raises a `ParseError` when a client sends invalid JSON. Explicitly catching this allows returning a custom JSON error matching the specifications.

### 3. Transition tests to APITestCase
- **Decision**: Change `SMTPValidationEndpointTests` parent class from `django.test.TestCase` to `rest_framework.test.APITestCase`.
- **Rationale**: `APITestCase` overrides the default `self.client` with DRF's `APIClient`, which supports sending JSON payloads natively using `format="json"`.

## Risks / Trade-offs

- **Risk**: Existing automated monitoring scripts using the GET endpoint will fail after the change.
- **Mitigation**: This is an internal/utility test endpoint. The client configuration must be updated to use POST with a JSON body.
