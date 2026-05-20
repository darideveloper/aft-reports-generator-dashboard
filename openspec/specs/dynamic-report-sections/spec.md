## ADDED Requirements

### Requirement: Dynamic Executive Summary
The system SHALL inject dynamic scores, levels, and descriptive text into the Executive Summary section.

#### Scenario: Executive Summary renders correctly
- **WHEN** the template is rendered with `average_score=75`, `level="Intermedio"`, and `strengths=["Digital Culture"]`
- **THEN** these values appear in the "Resumen ejecutivo" section of the generated PDF.

### Requirement: Dynamic Tabular Data
The system MUST support dynamic rendering of tables for participant distribution, area results, and theme rankings using Django template loops.

#### Scenario: Tables display multiple rows from context
- **WHEN** the template is provided with a list of 6 management areas and their scores
- **THEN** the "Resultados por área de gestión" table displays exactly 6 rows matching the provided data.

### Requirement: Dynamic Heatmap Rendering
The system SHALL render a dynamic heatmap showing participants and their performance across all 13 themes.

#### Scenario: Heatmap shows all participants
- **WHEN** 42 participants are provided in the context
- **THEN** the heatmap table renders 42 rows, each with appropriate performance dots for the 13 themes.

### Requirement: Categorized Participant Lists
The system MUST display lists of participants categorized by their technological profile (e.g., Ambassadors, Champions, Critical Risks).

#### Scenario: Strategic Reading lists are populated
- **WHEN** "Carlos Gomez" is marked as a "Champion de Transformación" in the context
- **THEN** his name appears under the corresponding heading in the "Lectura estratégica" section.
