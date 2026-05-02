## ADDED Requirements
### Requirement: Sample WeasyPrint PDF Generation
The system SHALL provide a sample capability to generate PDFs from HTML templates using WeasyPrint, demonstrating advanced CSS features like headers, footers, and page-breaking tables.

#### Scenario: Generate a sample PDF with multiple pages
- **WHEN** the sample PDF generation command is executed
- **THEN** a PDF is generated containing a consistent header and footer on every page (except where explicitly hidden)
- **THEN** the PDF contains a table with dynamic rows that spans multiple pages without breaking individual rows
- **THEN** the PDF utilizes CSS-driven colors and embedded images (logos) correctly