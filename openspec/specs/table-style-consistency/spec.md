## ADDED Requirements

### Requirement: Consistent Table Colors
The system SHALL use background colors for table headers and columns that match the provided Google Doc reference.

#### Scenario: Verify Interpretation Table Colors
- **WHEN** the "Escala de Interpretación" table is rendered
- **THEN** its headers have a muted teal/gray background (`#d9e2f3` or similar based on visual match).

#### Scenario: Verify Indicators Table Colors
- **WHEN** the "Indicador" table is rendered
- **THEN** the "Indicador" header has a darker gold background (`#fce5cd`) and the "Resultado" header/column has a lighter gold background (`#fff2cc`).
