## Why

The current client confirmation email for event registrations contains extra copy ("Estaremos compartiendo más detalles y novedades...") that makes the message longer than desired and dilutes the confirmation intent. Stakeholders want a cleaner, more direct confirmation email that matches the updated brand communications format: a concise greeting, confirmation of registration, appreciation, and a contact line.

## What Changes

- Update `events/templates/events/emails/client_confirmation.html` to use a simplified email body matching the exact format provided by the product team.
- Replace the hardcoded recipient name and event name in the new format with Django template variables (`{{ lead.name }}`, `{{ event.title }}`).
- Preserve all existing behavior and conditional logic: branding colors, optional logo, optional invitation-link CTA, footer signature, and HTML/text alternative generation.
- Update existing tests in `events/tests.py` that assert on the old email body copy so they match the new content.

## Capabilities

### New Capabilities
<!-- No new capabilities are introduced by this change. -->

### Modified Capabilities
- `event-forms`: The content/format of the branded client confirmation email is changing. The requirement that the email confirms registration using the corporate branding remains, but the specific body copy and structure are updated to the new concise format.

## Impact

- **File:** `events/templates/events/emails/client_confirmation.html`
- **File:** `events/tests.py` (email content assertions)
- **No database or model changes** are required.
- **No API contract changes** are required.
- The admin notification email and SMTP sending logic remain unchanged.
