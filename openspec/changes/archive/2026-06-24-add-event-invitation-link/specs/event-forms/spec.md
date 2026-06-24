## ADDED Requirements

### Requirement: Optional Event Invitation Link
The system MUST allow administrators to configure an optional invitation URL on each `Event` plus an optional button label, and the system MUST surface the resulting call-to-action (CTA) in two specific places and only in those two places: the client confirmation email and the post-submit success state of the public form.

The `Event` model MUST expose two new fields:
- `invitation_link`: a `URLField` with `max_length=500`, `blank=True`, `null=True`, restricted by a custom validator to the URL schemes `http` and `https` only. Any other scheme (including but not limited to `javascript`, `data`, `file`, `vbscript`, `ftp`) MUST be rejected at validation time.
- `invitation_label`: a `CharField` with `max_length=60`, `blank=True`, `default=""`. The label is optional; if blank, the CTA MUST use the default string `"Acceder al evento"`.

Visibility rules for the CTA:
- The CTA MUST be rendered in the client confirmation email only when `event.invitation_link` is truthy.
- The CTA MUST be rendered in the post-submit success state of the public form only when `event.invitation_link` is truthy.
- The CTA MUST NOT be rendered on the public form area above or below the form (pre-submit view).
- The CTA MUST NOT be rendered in the admin notification email.
- Events without an `invitation_link` MUST render no invitation CTA in any surface; their output MUST be byte-identical (in the relevant regions) to their pre-change output.

When the CTA is rendered, it MUST be a styled clickable button linking to `event.invitation_link` with `target="_blank"` and `rel="noopener noreferrer"`. In the client email, the raw URL MUST also appear as plain-text fallback directly below the button so that email clients which strip buttons still expose a clickable link. In the post-submit iframe state, the CTA MUST be revealed by JavaScript only after a `201` response from the submission endpoint, and MUST never be visible before submission.

The default label string `"Acceder al evento"` is a project-level default, defined in the templates and tests, and MUST be applied whenever `invitation_label` is empty or whitespace.

The migration that introduces the two fields MUST be purely additive: nullable, no data backfill, fully backward compatible with existing events.

#### Scenario: Event with invitation link and custom label — email contains CTA with custom label and raw URL fallback
- **WHEN** an event has `invitation_link="https://zoom.us/j/123?pwd=abc"` and `invitation_label="Ver grabación"`
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email HTML contains an `<a>` element whose `href` equals `https://zoom.us/j/123?pwd=abc`, with `target="_blank"` and `rel="noopener noreferrer"`, displaying the text `Ver grabación`
- **AND** the email HTML also contains the raw URL `https://zoom.us/j/123?pwd=abc` as plain text below the button
- **AND** the admin notification email contains no reference to the invitation URL or label

#### Scenario: Event with invitation link but no custom label — email uses default label
- **WHEN** an event has `invitation_link="https://zoom.us/j/123"` and `invitation_label=""`
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email HTML contains a button displaying the default text `Acceder al evento` and pointing to `https://zoom.us/j/123`
- **AND** the raw URL appears as plain text below the button

#### Scenario: Event without invitation link — no CTA in email
- **WHEN** an event has no `invitation_link` (NULL or empty)
- **AND** a lead is submitted for that event
- **THEN** the client confirmation email contains no `Acceder al evento` button, no `href` referencing the URL, and no fallback plain-text URL paragraph

#### Scenario: Event with invitation link — post-submit iframe state shows CTA
- **WHEN** a client submits a lead to an event with `invitation_link="https://zoom.us/j/123"` and `invitation_label="Unirse ahora"`
- **AND** the server responds with HTTP 201
- **THEN** the form is hidden and the success state is shown
- **AND** an invitation CTA element is revealed in the success state
- **AND** that CTA's `href` equals `https://zoom.us/j/123`, has `target="_blank"` and `rel="noopener noreferrer"`, and displays the text `Unirse ahora`

#### Scenario: Event with invitation link and default label — post-submit iframe state uses default label
- **WHEN** a lead submission returns 201 for an event with `invitation_link` set and `invitation_label` blank
- **THEN** the post-submit invitation CTA displays the default text `Acceder al evento`

#### Scenario: Event without invitation link — post-submit iframe state shows no CTA
- **WHEN** a lead submission returns 201 for an event with no `invitation_link`
- **THEN** the form is hidden and the success state is shown
- **AND** no invitation CTA element is present or revealed in the DOM

#### Scenario: Invitation link with non-http(s) scheme is rejected at validation
- **WHEN** an administrator saves an event with `invitation_link="javascript:alert(1)"`
- **THEN** the form fails validation with a field-level error on `invitation_link` stating the URL must be a valid http(s) URL
- **AND** the event is NOT saved

#### Scenario: Invitation link with valid http(s) URL is accepted
- **WHEN** an administrator saves an event with `invitation_link="https://zoom.us/j/123?pwd=abc&utm_source=mail"`
- **THEN** the event is saved successfully with that URL stored verbatim
- **AND** both the email CTA `href` and the iframe CTA `href` equal that exact URL

#### Scenario: Long URL with tracking parameters fits within the 500-character limit
- **WHEN** an administrator saves an event with an `invitation_link` of 480 characters containing `https://`, a path, a query string, and UTM parameters
- **THEN** the event is saved successfully and the URL is delivered intact in both the email and the iframe CTA

#### Scenario: Spam submission does not reveal the CTA via the email channel
- **WHEN** a bot submission triggers the honeypot and the lead is saved with `is_spam=True`
- **THEN** no client confirmation email is sent
- **AND** the CTA does not reach the attendee via email

#### Scenario: Migration is fully backward compatible
- **WHEN** the migration introducing `invitation_link` and `invitation_label` is applied to a database that already contains events
- **THEN** all existing events are preserved with `invitation_link=NULL` and `invitation_label=""`
- **AND** rendering any existing event in the email or iframe surface produces no invitation CTA
- **AND** the migration is reversible by running the reverse operation

#### Scenario: Admin edit form exposes both new fields
- **WHEN** an administrator opens the event edit page at `/admin/events/event/<id>/change/`
- **THEN** the page contains an input named `invitation_link` and an input named `invitation_label`
- **AND** the labels rendered next to those inputs read `Enlace de invitación` and `Texto del botón de invitación` respectively
- **AND** saving the form with a new value persists that value to the database

#### Scenario: Admin list view renders the invitation link as a clickable element
- **WHEN** an administrator opens the event list page at `/admin/events/event/`
- **THEN** the row for an event with `invitation_link` set contains a clickable `<a>` element whose `href` equals that URL, with `target="_blank"` and `rel="noopener noreferrer"`
- **AND** the row for an event without `invitation_link` displays the placeholder `—` (em-dash) for that column, with no `<a>` element
