## ADDED Requirements

### Requirement: Granular weakness analysis
The system SHALL provide a mechanism to analyze and extract the bottom-performing question groups for a collective set of reports, distinct from summary-level area analysis.

#### Scenario: Extract question group weaknesses
- **WHEN** calculation is requested for question group weaknesses
- **THEN** the system returns the two lowest-scoring question groups across the dataset
- **AND** these are used to provide specific improvement recommendations in the report

## MODIFIED Requirements

### Requirement: Shared PDF generation utility
The system SHALL provide a standalone function in `utils/group_report_generator.py` named `generate_group_report_pdf` that SHALL:
- Accept a QuerySet of Report objects.
- Render dynamic "Priority Actions" based on the two lowest-scoring areas for the group.
- **NEW**: Include dynamic "Weakness Question Groups" context for granular reporting.
- Include dynamic "Additional Recommendations" from the Company model if available.
- Render the HTML template and generates PDF bytes via WeasyPrint.

#### Scenario: Generate PDF with dynamic priority actions
- **WHEN** the PDF is generated for a group of reports
- **THEN** it SHALL include exactly two "Priority Actions" blocks corresponding to the lowest-scoring areas
- **AND** it SHALL round all displayed percentages to two decimal places.

#### Scenario: Generate PDF with granular weaknesses
- **WHEN** the PDF is generated for a group of reports
- **THEN** the context SHALL include `weakness_question_groups` containing the two lowest-scoring question groups.
