# form-persistence Specification

## Purpose
TBD - created by archiving change add-backend-form-persistence. Update Purpose after archive.
## Requirements
### Requirement: Save Form Progress
The system SHALL allow saving specific form state for a given email and survey.

#### Scenario: User saves progress
- **WHEN** a POST request is sent to `/api/progress/` with valid `email`, `survey` (ID), `current_screen`, and `data` (JSON blob)
- **THEN** the system SHALL create a new `FormProgress` record if one does not exist
- **OR** update the existing record if it does exist
- **AND** return a 200/201 status with the saved data.

#### Scenario: User already completed survey
- **WHEN** a POST request is sent to `/api/progress/`
- **BUT** the user (email) has already submitted answers for this survey
- **THEN** the system SHALL return a 400 Bad Request error with code `ALREADY_SUBMITTED`.

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

