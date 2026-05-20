## ADDED Requirements

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
