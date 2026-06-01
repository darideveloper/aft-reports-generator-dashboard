## ADDED Requirements

### Requirement: ReportsDownload admin list link
The `ReportsDownloadAdmin` SHALL provide a "Descargar Reportes" button in the list view when the status is "completed". The button SHALL:
- Link to the generated ZIP file.
- Include `target="_blank"` to open the download in a new tab.

#### Scenario: Download completed ZIP
- **WHEN** an admin views the ReportsDownload list
- **AND** a record has status "completed"
- **THEN** a "Descargar Reportes" button is displayed
- **AND** clicking it opens the ZIP download in a new tab
