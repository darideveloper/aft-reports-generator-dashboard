# Design: Synchronization Strategy

## Architectural Overview
The synchronization effort maps existing code patterns to OpenSpec requirements. The key areas being formalized are:

### 1. Batch Download System
The system uses a `ReportsDownload` model to track requests for batch PDF downloads.
- **Workflow**: Admin selects reports -> `ReportsDownload` instance created (status `pending`) -> Webhook sent to n8n -> n8n triggers `create_reports_download_file` management command -> ZIP generated and saved to `zip_file` -> Status updated to `completed`.
- **Integrations**: AWS S3 for ZIP storage, n8n for workflow orchestration.

### 2. Custom Benchmarking (Target Scores)
The `CompanyDesiredScore` model allows companies to define custom target scores per `QuestionGroup`.
- **Logic**: If `Company.use_average` is `False`, the system uses `CompanyDesiredScore` values for the comparison bar in the PDF report charts instead of the global average.
- **Automation**: `Company.save()` automatically scaffolds these records when switching to custom scores.

### 3. Result Persistence
Instead of calculating scores on-the-fly for every report view, the system persists results in:
- `ReportQuestionGroupTotal`: Scores per knowledge area.
- `ReportSummaryScore`: Averages per competency category (CD, TN, etc.).
This ensures report consistency and enables faster cross-report analysis (averages).

### 4. Developer Utilities
Management commands are formalized as part of the system's operational requirements to ensure consistent environment setup and testing.
- `load_initial_data`: Scaffolds basic survey structures.
- `create_test_responses`: Generates mock data for performance and layout testing.
- `delete_test_responses`: Restores the environment by removing test data.

### 5. Dynamic Content & Flexibility
- **Score-Based Paragraphs**: `TextPDFQuestionGroup` and `TextPDFSummary` models allow the PDF report to vary its textual content based on performance thresholds.
- **Structural Modifiers**: `QuestionGroupModifier` provides a mechanism to tag groups with metadata that the frontend or API can use to alter survey behavior without changing the core model schema.
