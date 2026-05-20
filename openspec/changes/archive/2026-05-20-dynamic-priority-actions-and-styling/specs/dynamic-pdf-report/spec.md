# Spec Delta: Dynamic Priority Actions and Single-Column Styling

## ADDED Requirements
### Requirement: The PDF report SHALL dynamically generate the "Señal Prioritaria" actions based on the lowest scoring knowledge areas.
The PDF report SHALL display actionable items directly correlated with the lowest scored areas of a specific company.
#### Scenario: The report is generated for a company
- **GIVEN** a company has completed surveys
- **WHEN** the group report PDF is generated
- **THEN** the priority actions section on page 11 MUST display the actionable recommendations corresponding to the two question groups with the lowest average scores for that company.

### Requirement: The PDF report SHALL present lists of participant names using a single-column layout without overflow.
Participant names MUST be displayed without spanning multiple columns, preserving readability.
#### Scenario: A long list of names is printed
- **GIVEN** a category (like "Embajador Estratégico") contains multiple names
- **WHEN** the group report PDF is generated
- **THEN** the names MUST be displayed in a single column layout
- **AND** the names MUST NOT split awkwardly across pages.