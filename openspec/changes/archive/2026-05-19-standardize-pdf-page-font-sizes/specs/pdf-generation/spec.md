## MODIFIED Requirements

### Requirement: Group Report Generation
The system SHALL provide the capability to generate group reports from HTML templates using WeasyPrint, demonstrating advanced CSS features like headers, footers, and page-breaking tables. The reports SHALL adhere to the standardized Letter page size and font styling (11pt body, 12pt bold headings).

#### Scenario: Generate a group report PDF with multiple pages
- **WHEN** the group report generation command is executed
- **THEN** a PDF is generated containing a consistent header and footer on every page (except where explicitly hidden)
- **THEN** the PDF contains a table with dynamic rows that spans multiple pages without breaking individual rows
- **THEN** the PDF utilizes CSS-driven colors and embedded images (logos) correctly
- **THEN** the PDF page size is Letter and font sizes follow the 11pt/12pt standard
