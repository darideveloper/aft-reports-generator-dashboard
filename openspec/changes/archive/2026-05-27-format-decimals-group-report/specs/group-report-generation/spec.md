## MODIFIED Requirements

### Requirement: Shared PDF generation utility
The system SHALL provide a standalone function in `utils/group_report_generator.py` named `generate_group_report_pdf` that SHALL:
- Accept a QuerySet of Report objects.
- Render dynamic "Priority Actions" based on the two lowest-scoring areas for the group.
- Include dynamic "Weakness Question Groups" context for granular reporting.
- Include dynamic "Additional Recommendations" from the Company model if available.
- Render the HTML template and generates PDF bytes via WeasyPrint.
- Ensure that ALL decimal values (scores, averages, percentages, max/min values, and level reference ranges) displayed in the report are formatted to exactly two decimal places (e.g., "56.50").

#### Scenario: Generate PDF with dynamic priority actions
- **WHEN** the PDF is generated for a group of reports
- **THEN** it SHALL include exactly two "Priority Actions" blocks corresponding to the lowest-scoring areas
- **AND** it SHALL format all displayed percentages and scores to exactly two decimal places.

#### Scenario: Generate PDF with granular weaknesses
- **WHEN** the PDF is generated for a group of reports
- **THEN** the context SHALL include `weakness_question_groups` containing the two lowest-scoring question groups.

#### Scenario: Formatting of maximum and minimum scores
- **WHEN** the group report PDF is generated
- **THEN** the "Resultado máximo" and "Resultado mínimo" in the Global Index section SHALL display exactly two decimal places.

#### Scenario: Formatting of nominal ranking scores
- **WHEN** the group report PDF is generated
- **THEN** every score in the "Ranking nominal" table SHALL display exactly two decimal places.

#### Scenario: Formatting of level reference ranges
- **WHEN** the group report PDF is generated
- **THEN** the score ranges in the "Nivel de dominio tecnológico" table (Page 3) SHALL display exactly two decimal places for both minimum and maximum values (e.g., "0.00 – 59.00").
