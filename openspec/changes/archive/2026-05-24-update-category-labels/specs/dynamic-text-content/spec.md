## MODIFIED Requirements

### Requirement: Competency category summary text
The system SHALL support the definition of summary text paragraphs for competency categories (CD, TN, CS, IP, TMA, EDC) based on aggregate scores. The labels for these categories SHALL be:
- CD: Cultura digital
- TN: Tecnología y negocios
- CS: Ciberseguridad
- IP: Impacto personal
- TMA: Futuro sustentable e inclusivo
- EDC: Ecosistema digital de colaboración

#### Scenario: Selecting a summary paragraph for Futuro sustentable e inclusivo
- **WHEN** a report is generated
- **AND** the category score for TMA is calculated
- **AND** a `TextPDFSummary` record exists for TMA with `min_score` less than or equal to the category score
- **THEN** the system SHALL select the paragraph with the highest `min_score` for the "Futuro sustentable e inclusivo" category.
