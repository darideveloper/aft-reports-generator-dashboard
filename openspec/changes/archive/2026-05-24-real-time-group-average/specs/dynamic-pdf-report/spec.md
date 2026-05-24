## ADDED Requirements

### Requirement: Dynamic Group Average Calculation
The system SHALL calculate the company-wide average score in real-time during the individual PDF report generation process.

#### Scenario: Aggregating company scores for individual report
- **GIVEN** a company has multiple submitted reports
- **WHEN** an individual report is being generated
- **THEN** the system SHALL calculate the average of all existing report totals for that company
- **AND** this value SHALL be injected into the PDF context as `company_average_total`
- **AND** the value MUST be rounded to 2 decimal places.

## MODIFIED Requirements

### Requirement: Dynamic Variable Injection
The system MUST support the injection of dynamic data into the template, including but not limited to: company name, number of participants, report date, and scoring results. The `company_average_total` MUST be provided by a real-time aggregation helper rather than a static database field.

#### Scenario: Verify dynamic data in generated PDF
- **WHEN** the template is rendered with `company_name="Acme Corp"`, `participant_count=50`, and a dynamically calculated `company_average_total`
- **THEN** the resulting PDF contains "Acme Corp", "50", and the correct calculated average in the designated fields
