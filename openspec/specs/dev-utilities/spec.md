# dev-utilities Specification

## Purpose
Document the requirements for management commands used to scaffold development environments and manage test data.
## Requirements
### Requirement: Automated environment scaffolding
The system SHALL provide tools to populate the database with initial survey structures and mock data for development.

#### Scenario: Loading initial data
- **WHEN** the `load_initial_data` command is executed
- **THEN** it populates the database with predefined `Company`, `Survey`, `QuestionGroup`, `Question`, and `Option` records.

#### Scenario: Generating test responses
- **WHEN** the `create_test_responses` command is executed
- **THEN** it generates a specified number of `Participant`, `Answer`, and `Report` records for stress testing and UI verification.

#### Scenario: Cleaning up test data
- **WHEN** the `delete_test_responses` command is executed
- **THEN** it removes all `Participant`, `Answer`, and `Report` records created during testing, restoring the database to a clean state.

