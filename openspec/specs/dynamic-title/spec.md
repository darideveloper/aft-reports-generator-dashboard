# dynamic-title Specification

## Purpose
TBD - created by archiving change make-report-title-dynamic. Update Purpose after archive.
## Requirements
### Requirement: Dynamic Footer Acronym
The footer of each page in the PDF report SHALL use the value of the `PDF_REPORT_ACRONYM` environment variable.

#### Scenario: Custom Acronym in Footer
- **Given** the environment variable `PDF_REPORT_ACRONYM` is set to "DCA"
- **When** a report is generated
- **Then** the footer of the PDF pages should contain the text "Reporte DCA de [Name]"

### Requirement: Dynamic Main Title
The main title of the report SHALL use the value of the `PDF_REPORT_TITLE` environment variable.

#### Scenario: Custom Title on First Page
- **Given** the environment variable `PDF_REPORT_TITLE` is set to "Evaluación de Competencias Digitales"
- **When** a report is generated
- **Then** the first page of the PDF should display "Evaluación de Competencias Digitales" as the main header/title.

