## Context

The application relies on SMTP settings defined in `project/settings.py` (e.g., `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) to dispatch event registrations and report notifications. Currently, there is no automated endpoint to check the health and configuration of the SMTP connection, meaning connection issues are only caught when real email dispatches fail. 

## Goals / Non-Goals

**Goals:**
- Provide a secure HTTP GET endpoint at `/tests/validate-email/` to validate SMTP setup.
- Enable monitoring via external tools like Uptime Kuma.
- Support testing only the connection handshake (TCP connection + SMTP AUTH validation) by default to avoid sending real spam emails.
- Support optional real mail sending for manual verification.

**Non-Goals:**
- Providing a generic health check endpoint (database, Redis, disk space) under this specific view.
- Managing Uptime Kuma configuration automatically.

## Decisions

### 1. View Framework: Django REST Framework APIView
We will implement the validation view as a DRF `APIView` in `core/views.py`.
- **Rationale**: DRF is already integrated into the project (used in `survey` and `events`). `APIView` simplifies response creation, query param parsing, exception mapping, and rate limiting integration.
- **Alternatives Considered**: Standard Django `View` with `JsonResponse`. Rejected because it requires manual JSON wrapping and doesn't benefit from standard DRF conventions.

### 2. Authentication: Pre-shared token query parameter (`?token=...`)
The view will be public (empty DRF `authentication_classes` and `permission_classes`), but the method will enforce token validation against an environment variable `SMTP_TEST_TOKEN`.
- **Rationale**: A query parameter is simple to test using standard browsers, curl, and is fully supported by Uptime Kuma. 
- **Alternatives Considered**: Custom headers (e.g. `X-SMTP-Token`). While more secure against browser history logging, Uptime Kuma URL-based config is simpler and standard. We will configure a dedicated token strictly for this view.

### 3. Emulated Verification: `connection.open()`
To validate the SMTP settings without sending an actual email, we will call `open()` on Django's mail connection.
- **Rationale**: Calling `open()` triggers the network connection, TLS/SSL handshake, and the SMTP AUTH process. If it succeeds, the credentials and mail server parameters are guaranteed to be valid. Closing it immediately prevents sending actual emails, saving resources and avoiding spam filters.
- **Alternatives Considered**: Always sending a real email. Rejected because Uptime Kuma monitors typically run every 1-5 minutes, which would result in hundreds of spam emails daily.

## Risks / Trade-offs

- **[Risk]**: Token exposure in logs.
  - *Mitigation*: The `SMTP_TEST_TOKEN` only grants access to this specific SMTP status endpoint. It does not allow reading database records or performing other operations.
- **[Risk]**: Abuse of the `real=true` parameter to send spam.
  - *Mitigation*: The `real` send parameter requires a valid destination `email` and is still protected by the token, preventing unauthorized users from triggering it.
