# group-report-generation Specification (Delta)

## ADDED Requirements

### Requirement: Nominal ranking table column headers
The system SHALL display the following column headers in the "Ranking nominal" table (section 6 of the group report PDF):
- "Rkg." instead of "Rank." for the ranking column
- "Semaf." instead of "Semáf." for the status column

#### Scenario: Nominal ranking table renders with updated headers
- **WHEN** the group report PDF is generated
- **THEN** the "Ranking nominal" table header SHALL display "Rkg." for the ranking column
- **AND** the "Semáf." header SHALL display as "Semaf."

#### Scenario: Existing columns are unchanged
- **WHEN** the group report PDF is generated
- **THEN** the "Nombre", "Posición", "Índice", and "Nivel" headers SHALL remain unchanged
