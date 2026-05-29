## MODIFIED Requirements

### Requirement: The PDF report SHALL dynamically generate the "Señal Prioritaria" actions based on the lowest scoring knowledge areas.
The PDF report SHALL display actionable items directly correlated with the lowest scored areas of a specific company. These areas SHALL use the updated labels.

#### Scenario: The report is generated for a company with low score in Futuro sustentable e inclusivo
- **GIVEN** a company has completed surveys
- **AND** "Futuro sustentable e inclusivo" (TMA) is one of the two lowest scoring areas
- **WHEN** the group report PDF is generated
- **THEN** the priority actions section on page 11 MUST display the actionable recommendations corresponding to "Futuro sustentable e inclusivo".
