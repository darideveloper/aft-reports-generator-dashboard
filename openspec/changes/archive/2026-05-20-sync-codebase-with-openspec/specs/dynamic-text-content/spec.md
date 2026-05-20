## ADDED Requirements

### Requirement: Score-based dynamic paragraphs
The system SHALL support the definition of text paragraphs that are dynamically selected for the PDF report based on the participant's score in a specific knowledge area.

#### Scenario: Selecting a paragraph for a knowledge area
- **WHEN** a report is generated
- **AND** a `TextPDFQuestionGroup` record exists for the area with `min_score` less than or equal to the participant's score
- **THEN** the system SHALL select the paragraph with the highest `min_score` that satisfies the condition for inclusion in the report.

### Requirement: Competency category summary text
The system SHALL support the definition of summary text paragraphs for competency categories (CD, TN, CS, IP, TMA, EDC) based on aggregate scores.

#### Scenario: Selecting a summary paragraph
- **WHEN** a report is generated
- **AND** a `TextPDFSummary` record exists for the category with `min_score` less than or equal to the category score
- **THEN** the system SHALL select the paragraph with the highest `min_score` for that category.
