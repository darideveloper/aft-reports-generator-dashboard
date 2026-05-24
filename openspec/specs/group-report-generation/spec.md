## ADDED Requirements

### Requirement: Admin-only sync preview
The system SHALL restrict the `/group-report-pdf/<company_id>/` route to authenticated admin users only. The view SHALL generate the group PDF synchronously and return it inline for preview/debugging.

#### Scenario: Authenticated admin accesses preview
- **WHEN** an authenticated admin user navigates to `/group-report-pdf/5/`
- **THEN** the system returns a PDF of the group report for company ID 5

#### Scenario: Unauthenticated user accesses preview
- **WHEN** an unauthenticated user navigates to `/group-report-pdf/5/`
- **THEN** the system redirects to the admin login page

#### Scenario: Non-admin user accesses preview
- **WHEN** a logged-in non-admin user navigates to `/group-report-pdf/5/`
- **THEN** the system returns a 403 Forbidden response

### Requirement: GroupReport model
The system SHALL provide a `GroupReport` Django model with the following fields:
- `id` (AutoField, primary key)
- `reports` (ManyToManyField to Report)
- `company` (ForeignKey to Company, nullable — populated only when triggered from Company button)
- `pdf_file` (FileField, nullable — the generated group PDF)
- `status` (CharField with choices: pending, processing, completed, error; default: pending)
- `logs` (TextField, nullable)
- `created_at` (DateTimeField, auto)
- `updated_at` (DateTimeField, auto)

#### Scenario: Create GroupReport via Report admin action
- **WHEN** an admin selects reports in the Report list and chooses "Generate group report" action
- **THEN** a new `GroupReport` is created with those reports and status "pending"
- **AND** the company field is null

#### Scenario: Create GroupReport via Company button
- **WHEN** an admin clicks "Generate group report" on a Company admin row
- **THEN** a new `GroupReport` is created with all completed reports for that company and status "pending"
- **AND** the company field points to that company

### Requirement: Webhook trigger on save
When a new `GroupReport` is created, the system SHALL make an HTTP GET request to the n8n webhook URL configured as `N8N_BASE_WEBHOOKS + "/aft-create-group-report-file"` (matching the existing `ReportsDownload` save pattern).

#### Scenario: Successful webhook call
- **WHEN** a new `GroupReport` is saved
- **AND** the n8n webhook returns HTTP 200
- **THEN** the GroupReport status remains "pending"

#### Scenario: Failed webhook call
- **WHEN** a new `GroupReport` is saved
- **AND** the n8n webhook returns non-200 status
- **THEN** the GroupReport status is set to "error"
- **AND** the error details are logged in the `logs` field

### Requirement: Shared PDF generation utility
The system SHALL provide a standalone function in `utils/group_report_generator.py` named `generate_group_report_pdf(reports: QuerySet) -> bytes` that:
- Accepts a QuerySet of Report objects
- Runs all group calculations via `SurveyCalcsGroupTexts`
- Renders the HTML template `survey/pdf/group_report_template.html`
- Generates PDF bytes via WeasyPrint
- Returns the raw PDF bytes

#### Scenario: Generate PDF from reports
- **WHEN** the function is called with a QuerySet of reports
- **THEN** it returns valid PDF bytes
- **AND** the PDF contains aggregated data from all provided reports

### Requirement: Async background generation command
The system SHALL provide a Django management command `create_group_report` that:
- Finds the oldest `GroupReport` with status "pending" (ordered by `created_at`)
- Sets its status to "processing"
- Calls `generate_group_report_pdf()` with the linked reports
- Saves the PDF bytes to the `pdf_file` field
- Sets status to "completed"
- Logs progress and errors to the `logs` field

#### Scenario: Successful processing
- **WHEN** the command runs
- **AND** a pending GroupReport exists
- **THEN** the GroupReport status transitions to "completed"
- **AND** the pdf_file field contains the generated PDF

#### Scenario: No pending reports
- **WHEN** the command runs
- **AND** no pending GroupReport exists
- **THEN** the command exits with a message

#### Scenario: Generation failure
- **WHEN** the command runs
- **AND** PDF generation raises an exception
- **THEN** the GroupReport status is set to "error"
- **AND** the exception details are saved in the logs field

### Requirement: Admin action on Report list
The `ReportAdmin` SHALL have an admin action "Generate group report" that:
- Creates a new `GroupReport` with all selected reports
- Triggers the n8n webhook on save
- Displays a success message to the admin directing them to the GroupReport admin table

#### Scenario: Reports selected and action triggered
- **WHEN** an admin selects one or more reports in the Report list
- **AND** selects "Generate group report" from the action dropdown
- **AND** clicks "Go"
- **THEN** a GroupReport is created with the selected reports
- **AND** a success message is shown

### Requirement: Admin button on Company list
The `CompanyAdmin` SHALL have a "Generate group report" button for each company row. Clicking it SHALL:
- Collect all completed reports for that company
- Create a new `GroupReport` with those reports and the company FK set
- Trigger the n8n webhook on save
- Redirect back to the Company list with a success message

#### Scenario: Company button clicked with completed reports
- **WHEN** an admin views the Company list
- **AND** clicks "Generate group report" for a company that has completed reports
- **THEN** a GroupReport is created for that company's completed reports
- **AND** a success message is shown
- **AND** the admin is redirected back to the Company list

#### Scenario: Company button clicked with no completed reports
- **WHEN** an admin views the Company list
- **AND** clicks "Generate group report" for a company that has zero completed reports
- **THEN** no GroupReport is created
- **AND** an error message is shown explaining no completed reports exist
- **AND** the admin is redirected back to the Company list

### Requirement: GroupReport admin table
The system SHALL register `GroupReport` with the Django admin, displaying:
- ID, status, company (if set), number of reports, created_at
- A "Download" button when status is "completed" — linking to the generated PDF file
- Filters by status, created_at

#### Scenario: Download completed group report
- **WHEN** an admin views the GroupReport list
- **AND** a GroupReport has status "completed"
- **THEN** a download button is displayed
- **AND** clicking it serves the PDF file

### Requirement: Download view
The system SHALL provide an admin view at `GroupReportAdmin` to serve the generated PDF file. The view SHALL:
- Require admin authentication (automatic via admin)
- Return the PDF with `Content-Disposition: inline` so it renders in the browser
- Return 404 if no PDF file exists

#### Scenario: Download existing PDF
- **WHEN** an admin accesses the download URL for a completed GroupReport
- **THEN** the PDF is served inline in the browser

#### Scenario: Download non-existent PDF
- **WHEN** an admin accesses the download URL for a GroupReport without a PDF
- **THEN** a 404 response is returned
