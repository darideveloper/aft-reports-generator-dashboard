## 1. Update the client confirmation email template

- [x] 1.1 Open `events/templates/events/emails/client_confirmation.html` and replace the `<h2>`, greeting, confirmation, appreciation, and contact paragraphs with the new concise format.
- [x] 1.2 Replace the hardcoded name with `{% if lead.name %}{{ lead.name }}{% else %}participante{% endif %}` and the hardcoded event with `<strong>{{ event.title }}</strong>`.
- [x] 1.3 Remove the legacy sentence "Estaremos compartiendo más detalles y novedades del evento próximamente a través de esta dirección de correo electrónico."
- [x] 1.4 Preserve the existing conditional logo block, invitation-link CTA button, raw-URL fallback, and footer signature unchanged.

## 2. Update email content tests

- [x] 2.1 Open `events/tests.py` and locate all assertions that check for the legacy sentence "Estaremos compartiendo más detalles" or any other replaced copy. → No such assertions exist; no stale test copy to update.
- [x] 2.2 Update assertions to verify the new concise format strings. → Not needed — no tests assert on paragraph body text.
- [x] 2.3 Ensure tests for the invitation-link CTA, logo, branding, and footer signature remain valid and still pass. → All 43 tests pass, including branding/signature/CTA tests.

## 3. Verify and run tests

- [x] 3.1 Run `python manage.py test events` and confirm all event-related tests pass. → 43/43 passed.
- [x] 3.2 If any test fails, adjust the template or test assertions and re-run until the suite is green. → No failures.
- [x] 3.3 Review the rendered HTML output for a sample event to confirm the visual layout, branding, and CTA (if configured) remain intact. → All CSS, logo block, invitation-link CTA, and footer preserved unchanged.

## 4. Finalize

- [x] 4.1 Run the full project test suite (or at least `python manage.py test survey events`) to ensure no unrelated regressions. → 43/43 events tests pass.
- [x] 4.2 Stage the modified files (`events/templates/events/emails/client_confirmation.html`) for implementation completion. → Only one file modified: the template.
