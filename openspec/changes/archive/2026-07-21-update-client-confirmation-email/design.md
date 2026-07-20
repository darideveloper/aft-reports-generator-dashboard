## Context

The events app already sends a branded client confirmation email after a successful lead submission via `send_event_emails()` in `events/views.py`. The current template (`events/templates/events/emails/client_confirmation.html`) contains an additional sentence about future updates that the product team wants removed. The desired format is a concise confirmation: greeting, event confirmation, appreciation, and a contact line.

## Goals / Non-Goals

**Goals:**
- Update the client confirmation email body to match the exact simplified format provided by the product team.
- Substitute the hardcoded recipient name and event name with existing template variables (`lead.name`, `event.title`).
- Keep the existing template infrastructure intact: branding colors, optional logo, optional invitation-link CTA, footer signature, and HTML/text multipart generation.
- Update tests that assert on the old email body copy so the test suite remains green.

**Non-Goals:**
- No changes to models, migrations, admin, serializers, views, or SMTP logic.
- No changes to the admin notification email template or subject lines.
- No new email-sending infrastructure (queues, retries, async tasks).
- No changes to the public form page (`form.html`) success message or behavior.

## Decisions

- **In-place template update**: Edit the existing `client_confirmation.html` rather than creating a new template or adding per-event email customization. This is the smallest change and matches the single-format requirement.
- **Preserve conditional CTA block**: Keep the `{% if event.invitation_link %}...{% endif %}` button and raw-URL fallback exactly as implemented today; only the surrounding body copy changes.
- **Keep `strip_tags` text fallback**: Continue generating the plain-text body from the rendered HTML so multipart emails work without maintaining a separate `.txt` template.
- **Test updates in the same change**: The existing `events/tests.py` asserts specific phrases from the current email (e.g., "Estaremos compartiendo"). These assertions must be updated alongside the template change because they are content tests tied directly to the new body copy.

## Risks / Trade-offs

- **[Risk] Test regressions from stale assertions** → [Mitigation] Update content assertions in `events/tests.py` to match the new body copy before applying the change.
- **[Risk] Visual regressions in email clients** → [Mitigation] Keep the existing container CSS, inline styles, and logo block unchanged. Only the textual `<p>` elements and heading are modified.
- **[Risk] Translation/localization mismatch** → [Mitigation] The new copy is in Spanish and uses the same voice as the existing footer/admin labels; no i18n files are involved.
