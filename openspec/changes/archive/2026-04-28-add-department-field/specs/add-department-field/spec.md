# Capability: area-field

The system MUST capture and display the area of each participant.

## ADDED Requirements

### Requirement: Participant Area Storage
The `Participant` model SHALL include a `department` field that stores the participant's area within their company.

#### Scenario: Storing participant area
- **GIVEN** a valid set of area choices (e.g., HR, IT, Sales)
- **WHEN** a participant is created with a selected area
- **THEN** the area should be persisted in the database associated with that participant

### Requirement: API Support for Area
The participant registration API SHALL accept a `department` field in the participant data payload.

#### Scenario: Registering a participant with an area
- **WHEN** a POST request is made to `/api/response/` with `department` in the `participant` object
- **THEN** the system should validate that the area is one of the allowed choices
- **AND** the participant should be saved with the provided area

### Requirement: Area Options in API
The options API SHALL include the list of valid area choices.

#### Scenario: Retrieving area options
- **WHEN** a GET request is made to `/api/options/`
- **THEN** the response body should include a `department` key
- **AND** the value should be a list of valid area objects (value and label)

### Requirement: Admin Visibility for Area
The Django admin interface SHALL display the `department` of each participant and allow filtering by it.

#### Scenario: Filtering participants by area in admin
- **GIVEN** participants assigned to different areas
- **WHEN** the administrator views the Participant list in the admin dashboard
- **THEN** they should see an "Area" column
- **AND** they should be able to filter the list using an "Area" filter sidebar
