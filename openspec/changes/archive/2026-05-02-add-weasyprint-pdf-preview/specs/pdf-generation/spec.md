## ADDED Requirements
### Requirement: Live WeasyPrint PDF Preview
The system SHALL provide an HTTP endpoint to preview the sample WeasyPrint PDF in real-time, facilitating template development.

#### Scenario: View the PDF preview in the browser
- **WHEN** a user navigates to the `/preview-pdf/` URL
- **THEN** the server compiles the `pdf_sample.html` using WeasyPrint
- **THEN** the server returns an inline PDF response that the browser renders natively