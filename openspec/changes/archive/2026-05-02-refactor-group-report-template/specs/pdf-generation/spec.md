## RENAMED Requirements
- FROM: `### Requirement: Sample WeasyPrint PDF Generation`
- TO: `### Requirement: Group Report Generation`
- FROM: `### Requirement: Live WeasyPrint PDF Preview`
- TO: `### Requirement: Live Group Report Preview`

## MODIFIED Requirements
### Requirement: Group Report Generation
The system SHALL provide the capability to generate group reports from HTML templates using WeasyPrint, demonstrating advanced CSS features like headers, footers, and page-breaking tables.

#### Scenario: Generate a group report PDF with multiple pages
- **WHEN** the group report generation command is executed
- **THEN** a PDF is generated containing a consistent header and footer on every page (except where explicitly hidden)
- **THEN** the PDF contains a table with dynamic rows that spans multiple pages without breaking individual rows
- **THEN** the PDF utilizes CSS-driven colors and embedded images (logos) correctly

### Requirement: Live Group Report Preview
The system SHALL provide an HTTP endpoint to preview the WeasyPrint group report in real-time, facilitating template development.

#### Scenario: View the group report preview in the browser
- **WHEN** a user navigates to the `/preview-pdf/` URL
- **THEN** the server compiles the `group_report.html` using WeasyPrint
- **THEN** the server returns an inline PDF response that the browser renders natively