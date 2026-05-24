## Why

The project already generates individual PDF reports per participant and group PDF reports per company via `/group-report-pdf/<company_id>/`. However, admins have no way to generate group reports on demand for arbitrary subsets of reports (not just one company), and the existing route is publicly accessible with no auth. Adding admin-controlled, async group report generation closes this gap and follows the existing ReportsDownload background pattern.

## What Changes

- **Admin-only route**: Restrict `/group-report-pdf/<company_id>/` to admin users only (for debugging/preview)
- **New `GroupReport` model**: Parallels `ReportsDownload` — stores status, linked reports, generated PDF file, and logs
- **Shared PDF generator**: Extract the report-building logic from `GroupReportPDFView.get()` into a standalone reusable function in `utils/`
- **Admin action on Report table**: "Generate group report" checkbox action that creates a `GroupReport` and triggers async n8n webhook
- **Admin button on Company list**: "Generate group report" button per company row, creates `GroupReport` with that company's reports
- **Async management command**: `create_group_report.py` polls pending `GroupReport` records, calls the shared PDF generator, saves the file, marks completed
- **Download route**: Serve the generated PDF via a custom admin view on `GroupReportAdmin` (e.g., `/admin/survey/groupreport/<id>/download/`)

## Capabilities

### New Capabilities
- `group-report-generation`: Background generation of group report PDFs from arbitrary report subsets, with admin entry points (Report action + Company button), async processing via n8n → management command (matching ReportsDownload pattern), and an admin-only sync preview endpoint

### Modified Capabilities

None.

## Impact

- **New model**: `survey.models.GroupReport`
- **New management command**: `survey/management/commands/create_group_report.py`
- **Modified view**: `survey.views.GroupReportPDFView` — add admin permission check
- **New utility**: `utils/group_report_generator.py` — shared PDF generation function
- **Modified admin**: `survey.admin.ReportAdmin` — new action; `survey.admin.CompanyAdmin` — custom button
- **New n8n webhook trigger**: similar to `aft-create-reports-download-file`
- **No breaking changes** — existing functionality preserved
- **Note**: The sync preview route (`/group-report-pdf/<company_id>/`) uses ALL reports for debugging. The async Company button filters to `completed` reports only. This is intentional — preview shows raw data; production generation only uses finalized reports.
