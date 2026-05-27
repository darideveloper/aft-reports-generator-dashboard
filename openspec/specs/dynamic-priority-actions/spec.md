# dynamic-priority-actions Specification

## Purpose
TBD - created by archiving change sync-openspecs-with-codebase. Update Purpose after archive.
## Requirements
### Requirement: Dynamic Identification of Priority Areas
The system SHALL identify the two competency areas (QuestionGroups) with the lowest scores for a given group report context.

#### Scenario: Identify two lowest scores
- **WHEN** the priority actions logic is triggered
- **THEN** it SHALL sort all areas by their average score in ascending order
- **AND** select the top two areas for action mapping.

### Requirement: Mapping Areas to Priority Action Blocks
The system SHALL map the identified lowest areas to predefined action blocks containing a title and a list of specific recommendations.

#### Scenario: Generate action blocks for PDF
- **WHEN** the two lowest areas are identified (e.g., "Ciberseguridad" and "Cultura Digital")
- **THEN** it SHALL retrieve the corresponding text blocks from the internal `PRIORITY_ACTIONS_MAPPING`
- **AND** pass these blocks to the PDF template for rendering.

