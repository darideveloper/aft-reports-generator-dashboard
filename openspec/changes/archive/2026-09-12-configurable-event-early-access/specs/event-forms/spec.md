## MODIFIED Requirements

### Requirement: Event Creation and Configuration
The system SHALL allow administrators to create events in the admin panel with a custom URL slug and toggle the active/required status of predefined fields (Name, Job Position, Email, Phone, Company).
- All models, verbose names, help text, and field names in the admin dashboard MUST be presented in Spanish (es-mx) matching project localization conventions.
- The `Event` and `Lead` models MUST explicitly define `id = models.AutoField(primary_key=True)` as their primary key.
- The `Lead.job_position` field MUST be a standard free-text `CharField` allowing any arbitrary text inputs, not constrained to the project's internal `POSITION_CHOICES`.
- The `Event` model MUST define `access_early_minutes` as a `PositiveIntegerField` with default `30`, Spanish `verbose_name="Anticipación de acceso (minutos)"` and help text explaining it controls how many minutes before the start the invitation link becomes visible (`0` = only from the start). The field MUST appear in the admin alongside `event_datetime` and `duration_minutes`.

#### Scenario: Admin creates and configures an event
- **WHEN** the admin creates an event with title "Conferencia Anual", slug "conferencia-anual-2026", and configures Name (active/required), Phone (active/optional), and Company (inactive)
- **THEN** the event configuration is saved, a public form page in Spanish becomes available at `/events/conferencia-anual-2026/`, and the dashboard displays the event in the side panel.

#### Scenario: Admin configures early-access window
- **WHEN** the admin creates an event without touching the early-access field
- **THEN** `access_early_minutes` defaults to `30`
- **WHEN** the admin sets it to `15` (or `0`, or `90`)
- **THEN** the value is saved and the access gate reveals the invitation link that many minutes before `event_datetime`
