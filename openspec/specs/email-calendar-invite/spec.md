# email-calendar-invite Specification

## Purpose
Defines how the client confirmation email surfaces Add-to-Calendar actions when the Event has `event_datetime` set: a table-based calendar buttons section, an `.ics` attachment, and plain-text URL fallbacks. Extracted from change `event-email-calendar-buttons`.

## Requirements

### Requirement: Email calendar buttons section
The system SHALL render an `Agregar a tu calendario:` section in the client confirmation email when the Event has `event_datetime` set, containing three link buttons: Google Calendar (target `_blank`), Outlook (target `_blank`), and Apple Calendar (hosted absolute `.ics` URL). The section SHALL use table-based layout with all-inline styles, text-only labels, and no flex, SVG, or `<style>` reliance.

#### Scenario: Calendar section shown when datetime set
- **WHEN** a lead is submitted to an event with `event_datetime` set
- **THEN** the client HTML contains `Agregar a tu calendario:` inside a `<table role="presentation">` with inline `background-color` styling, plus an `<a>` with `google.com/calendar` and `target="_blank"`, an `<a>` with `outlook.office.com` and `target="_blank"`, and an `<a>` with the absolute `/ics/` URL (which MAY omit `target="_blank"`)

#### Scenario: Calendar section hidden when datetime missing
- **WHEN** a lead is submitted to an event with `event_datetime=None`
- **THEN** the client HTML contains no `Agregar a tu calendario:` text, no `google.com/calendar` link, no `outlook.office.com` link, and no `/ics/` link

#### Scenario: Calendar section independent of invitation link
- **WHEN** an event has `event_datetime` set but `invitation_link` empty
- **THEN** the calendar section is still rendered (while the access CTA remains hidden)

### Requirement: ICS attachment on client email
The system SHALL attach `{event.slug}.ics` with mimetype `text/calendar` containing `_build_ics_content(event)` output (`METHOD:PUBLISH`, stable `UID:{slug}@aft-dashboard`) to the client confirmation email whenever `event_datetime` is set.

#### Scenario: Attachment present with datetime
- **WHEN** a lead is submitted to an event with `event_datetime` set
- **THEN** `mail.outbox` client message has one attachment named `<slug>.ics` with mimetype `text/calendar` whose content contains `BEGIN:VCALENDAR`, `DTSTART`, `DTEND`, `SUMMARY`, and `UID:<slug>@aft-dashboard`

#### Scenario: No attachment without datetime
- **WHEN** a lead is submitted to an event with `event_datetime=None`
- **THEN** the client message has zero attachments

### Requirement: Plain-text calendar fallback
The system SHALL append the raw Google, Outlook, and ICS URLs to the plain-text body of the client email whenever the calendar section is rendered.

#### Scenario: Text body contains calendar URLs
- **WHEN** a lead is submitted to an event with `event_datetime` set
- **THEN** the text body contains `google.com/calendar`, `outlook.office.com`, and `/ics/`
