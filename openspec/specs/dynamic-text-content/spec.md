# dynamic-text-content Specification

## Purpose
Define the requirements for dynamic textual content in PDF reports based on participant performance thresholds.
## Requirements
### Requirement: Score-based dynamic paragraphs
The system SHALL support the definition of text paragraphs that are dynamically selected for the PDF report based on the participant's score in a specific knowledge area.

#### Scenario: Selecting a paragraph for a knowledge area
- **WHEN** a report is generated
- **AND** a `TextPDFQuestionGroup` record exists for the area with `min_score` less than or equal to the participant's score
- **THEN** the system SHALL select the paragraph with the highest `min_score` that satisfies the condition for inclusion in the report.

### Requirement: Competency category summary text
The system SHALL support the definition of summary text paragraphs for competency categories (CD, TN, CS, IP, TMA, EDC) based on aggregate scores. The text content SHALL reflect the current branding and scope of each category.

#### Scenario: Selecting a summary paragraph for TMA
- **WHEN** a report is generated for the TMA category
- **THEN** the selected `TextPDFSummary` text MUST include concepts of both "sostenibilidad" and "inclusión".
- **AND** it MUST NOT refer to the category exclusively as "medio ambiente".

