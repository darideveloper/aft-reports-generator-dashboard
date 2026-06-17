## Why

The system currently lacks a way to monitor the SMTP credential validity and connection status in real-time. This makes it difficult to detect email delivery issues (due to password expiration, network changes, or firewall blocks) before they affect users registering for events or receiving reports. Adding a test endpoint allows automated monitoring via tools like Uptime Kuma to proactively alert administrators of SMTP failures.

## What Changes

- Add a new HTTP GET endpoint at `/tests/validate-email/` (under the `core` app).
- Support two validation modes:
  - **Emulated (Connection check only)**: Validates host, port, protocol, and credentials without sending a real email.
  - **Real Send**: Sends a physical validation email to the specified address.
- Protect the endpoint with a custom pre-shared token query parameter (`?token=<TOKEN>`) to prevent abuse and unauthorized use of SMTP resources.
- Introduce `SMTP_TEST_TOKEN` environment variable configuration.

## Capabilities

### New Capabilities
- `smtp-validation`: Provides a secure HTTP validation endpoint for monitoring and testing the project's SMTP settings.

### Modified Capabilities
*None*

## Impact

- **API**: A new public path `/tests/validate-email/` will be registered.
- **Settings**: Requires the addition of `SMTP_TEST_TOKEN` in `project/settings.py` and environment configurations (`.env.dev` / `.env.prod`).
- **Dependencies**: No new packages or dependencies are required. Uses standard Django `django.core.mail` tools.
