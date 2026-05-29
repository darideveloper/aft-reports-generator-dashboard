## MODIFIED Requirements

### Requirement: Competency category summary text
The system SHALL support the definition of summary text paragraphs for competency categories (CD, TN, CS, IP, TMA, EDC) based on aggregate scores. The text content SHALL reflect the current branding and scope of each category.

#### Scenario: Selecting a summary paragraph for TMA
- **WHEN** a report is generated for the TMA category
- **THEN** the selected `TextPDFSummary` text MUST include concepts of both "sostenibilidad" and "inclusión".
- **AND** it MUST NOT refer to the category exclusively as "medio ambiente".
