# form-persistence Specification

## Purpose
Specify requirements for maintaining participant survey state across sessions, allowing users to save their progress and resume from the last completed screen.
## Requirements
### Requirement: Save Form Progress
The system SHALL allow saving specific form state for a given email and survey using the `FormProgress` model.

#### Scenario: User saves progress
- **WHEN** a POST request is sent to `/api/progress/` with valid `email`, `survey` (ID), `current_screen`, and `data` (JSON blob)
- **THEN** the system SHALL create or update the `FormProgress` record for that specific survey and email.
- **AND** return a 200/201 status with the saved data.

### Requirement: Retrieve Form Progress
The system SHALL allow retrieving saved progress by email and survey ID.

#### Scenario: Retrieve existing progress
- **WHEN** a GET request is sent to `/api/progress/` with valid `email` and `survey` (ID) query parameters
- **AND** a matching `FormProgress` record exists
- **THEN** the system SHALL return 200 OK with the stored `data` and `current_screen`.

#### Scenario: Progress not found
- **WHEN** a GET request is sent to `/api/progress/`
- **AND** no matching record exists
- **THEN** the system SHALL return 404 Not Found.

### Requirement: Clear Form Progress
The system SHALL allow deleting progress records.

#### Scenario: Delete progress
- **WHEN** a DELETE request is sent to `/api/progress/` with `email` and `survey` query parameters
- **THEN** the system SHALL delete the corresponding `FormProgress` record and return 204 No Content.

