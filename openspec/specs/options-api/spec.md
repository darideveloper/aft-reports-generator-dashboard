# options-api Specification

## Purpose
TBD - created by archiving change add-options-api. Update Purpose after archive.
## Requirements
### Requirement: Retrieve Dropdown Options
The system SHALL provide a `GET` endpoint at `/api/options/` that returns the choices defined in `core/choices.py`.

#### Scenario: Successful retrieval of options
- **WHEN** a GET request is made to `/api/options/`
- **THEN** the response status should be 200 OK
- **AND** the response body should contain a dictionary of options
- **AND** the keys should include `gender`, `birth_range`, `position`, and `status`
- **AND** each value should be a list of objects with `value` and `label` properties

