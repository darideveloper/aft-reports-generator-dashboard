# structural-modifiers Specification

## Purpose
Establish the requirements for flexible survey group behavior and metadata tagging via the structural modifier system.
## Requirements
### Requirement: Flexible question group behavior
The system SHALL support `QuestionGroupModifier` records that can be associated with `QuestionGroup` instances to signal special behavior or formatting in the frontend/API.

#### Scenario: Retrieving modifiers via API
- **WHEN** a client retrieves survey structure via the API
- **THEN** the list of associated modifier names SHALL be included in the response for each question group.

