## MODIFIED Requirements

### Requirement: GroupReport admin table
The system SHALL register `GroupReport` with the Django admin, displaying:
- ID, status, company (if set), number of reports, created_at
- A "Descargar PDF" button when status is "completed" — linking to the generated PDF file using the object's primary key in the URL (e.g., `/{pk}/download/`).
- The button SHALL include `target="_blank"`.
- Filters by status, created_at

#### Scenario: Download completed group report
- **WHEN** an admin views the GroupReport list
- **AND** a GroupReport has status "completed"
- **THEN** a "Descargar PDF" button is displayed
- **AND** the button link includes the record's primary key
- **AND** clicking it opens the PDF file in a new tab

### Requirement: Download view
The system SHALL provide an admin view at `GroupReportAdmin` to serve the generated PDF file. The view SHALL:
- Require admin authentication (automatic via admin)
- Match the URL pattern `/{pk}/download/`
- Return the PDF with `Content-Disposition: inline` so it renders in the browser
- Return 404 if no PDF file exists or the object is not found

#### Scenario: Download existing PDF
- **WHEN** an admin accesses the download URL `/{pk}/download/` for a completed GroupReport
- **THEN** the PDF is served inline in the browser
