# Capability: department-field

The system MUST capture and display the department or area of each participant.

## ADDED Requirements

### Requirement: Participant Department Storage
The `Participant` model SHALL include a `department` field that stores the participant's area within their company.

#### Scenario: Storing participant department
- **GIVEN** a valid set of department choices (e.g., HR, IT, Sales)
- **WHEN** a participant is created with a selected department
- **THEN** the department should be persisted in the database associated with that participant

### Requirement: API Support for Department
The participant registration API SHALL accept a `department` field in the participant data payload.

#### Scenario: Registering a participant with a department
- **WHEN** a POST request is made to `/api/response/` with `department` in the `participant` object
- **THEN** the system should validate that the department is one of the allowed choices
- **AND** the participant should be saved with the provided department

### Requirement: Department Options in API
The options API SHALL include the list of valid department choices.

#### Scenario: Retrieving department options
- **WHEN** a GET request is made to `/api/options/`
- **THEN** the response body should include a `department` key
- **AND** the value should be a list of valid department objects (value and label)

### Requirement: Admin Visibility for Department
The Django admin interface SHALL display the `department` of each participant and allow filtering by it.

#### Scenario: Filtering participants by department in admin
- **GIVEN** participants assigned to different departments
- **WHEN** the administrator views the Participant list in the admin dashboard
- **THEN** they should see a "Department" column
- **AND** they should be able to filter the list using a "Department" filter sidebar
