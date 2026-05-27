## MODIFIED Requirements

### Requirement: Shared PDF generation utility
The system SHALL provide a standalone function in `utils/group_report_generator.py` named `generate_group_report_pdf` that SHALL:
- Accept a QuerySet of Report objects.
- Render dynamic "Priority Actions" based on the two lowest-scoring areas for the group.
- Include dynamic "Additional Recommendations" from the Company model if available.
- Render the HTML template and generates PDF bytes via WeasyPrint.

#### Scenario: Generate PDF with dynamic priority actions
- **WHEN** the PDF is generated for a group of reports
- **THEN** it SHALL include exactly two "Priority Actions" blocks corresponding to the lowest-scoring areas
- **AND** it SHALL round all displayed percentages to two decimal places.
