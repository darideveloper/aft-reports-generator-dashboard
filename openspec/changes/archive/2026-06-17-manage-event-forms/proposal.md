## Why

The application currently lacks a mechanism to run and manage standalone marketing or registration event forms. Implementing this feature will allow the admin to generate unique form URLs per event, collect lead data within a responsive layout suitable for WordPress iframe embedding, and trigger SMTP email notifications to both the admin and the registered client.

## What Changes

- **Add Standalone Events App**: Create a new Django app (`events`) to isolate the new functionality from the existing survey assessment models.
- **Dynamic Predefined Form Fields**: Allow the admin to toggle which common fields (Name, Job Position, Email, Phone, Company) are active and required on a per-event basis.
- **Iframe Integration Support**: Allow public event forms to bypass default clickjacking protections (`X-Frame-Options`) for embedding in WordPress, and implement client-side automatic height resizing messages.
- **AJAX Lead Submission API**: Implement a public, CSRF-exempt JSON POST API endpoint for lead registrations with honeypot spam protection.
- **SMTP Auto-notifications**: Set up a global SMTP email configuration to dispatch admin notification and client confirmation emails upon successful lead submission.

## Capabilities

### New Capabilities
- `event-forms`: Provides tools for administrators to define custom events with dynamic predefined fields, display responsive forms inside WordPress iframes, capture registrations via a JSON API, and trigger SMTP email confirmations.

### Modified Capabilities
<!-- None. This is a completely new standalone capability. -->

## Impact

- **Settings**: Modifies `project/settings.py` to register the new `events` app and configure global SMTP settings.
- **URLs**: Modifies `project/urls.py` to route `/events/` and `/api/events/` requests.
- **Dependencies**: No new package dependencies; standard Django features and DRF (which is already installed) will be utilized.
- **Security**: The new endpoint is CSRF-exempt to work inside third-party iframes, relying on honeypot logic and rate throttling to mitigate spam.
