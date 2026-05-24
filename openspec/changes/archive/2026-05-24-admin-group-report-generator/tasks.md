## 1. Model

- [x] 1.1 Add `GroupReport` model to `survey/models.py` with fields: reports (M2M), company (FK nullable), pdf_file, status, logs, created_at, updated_at — plus save() method that triggers n8n webhook (matching ReportsDownload pattern)
- [x] 1.2 Create and run migration for the new model

## 2. Shared PDF Generator

- [x] 2.1 Create `utils/group_report_generator.py` with `generate_group_report_pdf(reports)` — extract the PDF-building logic from `GroupReportPDFView.get()` into this standalone function
- [x] 2.2 Refactor `GroupReportPDFView.get()` to call `generate_group_report_pdf()` instead of inline logic

## 3. Admin-Only Route

- [x] 3.1 Add `login_required` + `staff_member_required` decorators (or `user_passes_test`) to `GroupReportPDFView.get()` to restrict to admin users only
- [x] 3.2 Verify the route still works for admins and redirects unauthenticated users to login

## 4. Background Command

- [x] 4.1 Create `survey/management/commands/create_group_report.py` — picks oldest pending GroupReport, calls `generate_group_report_pdf()`, saves PDF to FileField, updates status
- [x] 4.2 Register the n8n webhook endpoint `aft-create-group-report-file` in n8n to trigger this command (external config, documented in the model save method)

## 5. Admin Integration

- [x] 5.1 Register `GroupReport` with Django admin (`GroupReportAdmin`) with list display fields (id, status, company, report count, created_at) and a "Download" link button for completed items
- [x] 5.2 Add a custom admin download view on `GroupReportAdmin` to serve the PDF inline (e.g., `get_download_view`)
- [x] 5.3 Add "Generate group report" action to `ReportAdmin` that creates a GroupReport with selected reports
- [x] 5.4 Add "Generate group report" button to `CompanyAdmin` via `get_urls()` override with a custom admin view that creates a GroupReport for that company's completed reports — includes a guard: show error message if no completed reports exist

## 6. Tests

- [x] 6.1 Test GroupReport model save triggers webhook (mock requests.get)
- [x] 6.2 Test GroupReport save handles webhook failure gracefully
- [x] 6.3 Test shared PDF generator returns valid PDF bytes for a set of reports
- [x] 6.4 Test admin action creates GroupReport with selected reports
- [x] 6.5 Test management command processes pending GroupReport correctly
- [x] 6.6 Test admin-only route restriction (unauthorized redirect, non-admin 403)
