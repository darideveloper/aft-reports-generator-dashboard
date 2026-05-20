# dynamic-pdf-report Specification

## Purpose
Document the requirements for dynamic PDF report generation using Django templates and WeasyPrint.
## Requirements
### Requirement: Django-based PDF Rendering
The system SHALL render the organizational PDF report using the Django `render_to_string` utility, allowing for dynamic data injection through a context dictionary.

#### Scenario: Successful PDF rendering from template
- **WHEN** a request is made to preview the PDF report
- **THEN** the system renders the `survey/pdf/report_template.html` template with the provided context and generates a PDF via WeasyPrint

### Requirement: Dynamic Variable Injection
The system MUST support the injection of dynamic data into the template, including but not limited to: company name, number of participants, report date, and scoring results.

#### Scenario: Verify dynamic data in generated PDF
- **WHEN** the template is rendered with `company_name="Acme Corp"` and `participant_count=50`
- **THEN** the resulting PDF contains "Acme Corp" and "50" in the designated fields on the cover page

### Requirement: Static Asset Resolution for WeasyPrint
The system SHALL ensure that CSS files and images referenced in the Django template are correctly resolved and embedded by WeasyPrint during the PDF generation process.

#### Scenario: CSS and Images load correctly
- **WHEN** WeasyPrint processes the rendered HTML
- **THEN** it successfully locates and applies `style.css` and embeds images from the `assets/` directory using an appropriate `base_url`

### Requirement: Dynamic Knowledge Area Details
The system SHALL support the display of area-specific details next to the results charts in the PDF report.

#### Scenario: Displaying bar chart details
- **WHEN** a `QuestionGroup` has the `details_bar_chart` field populated
- **THEN** that text SHALL be included in the report context and rendered adjacent to the corresponding bar chart.

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

