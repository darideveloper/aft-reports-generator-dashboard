# batch-report-downloads Specification

## Purpose
Define the requirements for batch PDF report generation and distribution via ZIP archives and asynchronous background processing.
## Requirements
### Requirement: Batch report download tracking
The system SHALL provide a `ReportsDownload` model to manage and track the status of batch report ZIP generation.

#### Scenario: Creating a download request
- **WHEN** an administrator selects multiple reports for download
- **THEN** a `ReportsDownload` record is created with status `pending`.

### Requirement: Asynchronous ZIP generation via webhook
The system SHALL integrate with an external automation service (n8n) to orchestrate the generation of the ZIP file.

#### Scenario: Triggering the workflow
- **WHEN** a `ReportsDownload` record is saved for the first time
- **THEN** it sends an HTTP GET request to the configured n8n webhook URL.

### Requirement: Background processing of ZIP files
The system SHALL provide a management command `create_reports_download_file` that processes pending download requests.

#### Scenario: Generating the ZIP
- **WHEN** the command finds a `pending` request
- **THEN** it downloads the PDF files for all associated reports, creates a ZIP archive, uploads it to storage, and updates the status to `completed`.

