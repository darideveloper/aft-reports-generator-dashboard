## MODIFIED Requirements

### Requirement: Retrieve Dropdown Options
The system SHALL provide a `GET` endpoint at `/api/options/` that returns the choices centralized in `core/choices.py`.

#### Scenario: Successful retrieval of options
- **WHEN** a GET request is made to `/api/options/`
- **THEN** it SHALL return a JSON object with keys `gender`, `birth_range`, `position`, and `status`.
- **AND** the labels and values MUST match the constants in `core/choices.py`.
