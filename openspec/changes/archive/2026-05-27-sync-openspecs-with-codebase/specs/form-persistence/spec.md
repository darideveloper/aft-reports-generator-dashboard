## MODIFIED Requirements

### Requirement: Save Form Progress
The system SHALL allow saving specific form state for a given email and survey using the `FormProgress` model.

#### Scenario: User saves progress
- **WHEN** a POST request is sent to `/api/progress/` with valid `email`, `survey` (ID), `current_screen`, and `data` (JSON blob)
- **THEN** the system SHALL create or update the `FormProgress` record for that specific survey and email.
- **AND** return a 200/201 status with the saved data.
