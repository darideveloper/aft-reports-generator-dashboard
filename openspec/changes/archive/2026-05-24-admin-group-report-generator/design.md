## Context

The project generates individual participant PDF reports and group PDF reports (aggregated statistics across many participants). The group report is currently available at `/group-report-pdf/<company_id>/` with no authentication, and only works per-company. Admins need a way to generate these group reports for arbitrary subsets of reports and have them available for download.

The existing `ReportsDownload` model and its background processing (n8n webhook → management command) provide the proven async pattern to follow.

## Goals / Non-Goals

**Goals:**
- Restrict the synchronous `/group-report-pdf/<company_id>/` route to admin users only
- Create a new `GroupReport` model to track generation status and store the PDF
- Extract PDF generation into a shared utility function callable from both sync and async contexts
- Add admin action on Report list to select reports and trigger async group report generation
- Add admin button on Company list to trigger group report generation for a company's reports
- Process group report generation asynchronously via n8n webhook → management command (matching ReportsDownload pattern)
- Provide a download view for completed group report PDFs

**Non-Goals:**
- Changing the content or template of the group report PDF itself
- Replacing the existing ReportsDownload flow
- Adding Celery/RQ or any new async infrastructure
- Modifying individual participant report generation

## Decisions

### 1. New `GroupReport` model vs. extending `ReportsDownload`
**Decision**: New `GroupReport` model.
**Rationale**: `ReportsDownload` zips individual participant PDFs. `GroupReport` generates a single aggregated PDF with different content (calculations, summaries). Combining them into one model would require a type discriminator and conditional logic throughout, making both flows harder to reason about and test independently.

### 2. Shared PDF generator function
**Decision**: Extract the `get()` logic from `GroupReportPDFView` into `utils/group_report_generator.py` as a function `generate_group_report_pdf(reports: QuerySet[Report]) -> bytes`.
**Rationale**: Both the sync route (for debugging preview) and the async management command need the same PDF bytes. A standalone function avoids duplication and makes the logic testable without HTTP or view infrastructure. The view becomes a thin wrapper that calls the function and wraps result in an `HttpResponse`.

### 3. Company button implementation
**Decision**: Override `CompanyAdmin.get_urls()` to add a custom admin view that creates a `GroupReport` for that company's reports and triggers the n8n webhook, with a `change_form` button linking to it.
**Rationale**: This follows Django admin conventions for adding per-row actions without touching the list display template directly. The custom view reuses the same webhook trigger logic as the Report action.

### 4. Download route
**Decision**: Serve the generated PDF via a custom admin view on `GroupReportAdmin` (e.g., `/admin/survey/groupreport/<id>/download/`).
**Rationale**: Keeps the PDF behind admin auth naturally. No need for a separate URL pattern outside the admin — the download is always admin-only by definition.

### 5. n8n webhook trigger
**Decision**: Create a new n8n webhook endpoint (e.g., `/aft-create-group-report-file`) that parallels `aft-create-reports-download-file`. The `GroupReport.save()` method triggers it exactly like `ReportsDownload.save()` does.
**Rationale**: Consistency with the existing pattern. The n8n flow polls the management command, which processes pending `GroupReport` records. No new async infrastructure needed.

## Risks / Trade-offs

- **n8n dependency**: If n8n webhook fails or is unreachable, the GroupReport will remain stuck in "pending" status. **Mitigation**: The webhook call is a fire-and-forget trigger — the actual processing reads from the DB. If the webhook call fails, an admin can manually run the management command.
- **Large datasets**: A group report for hundreds of reports may be slow to generate or produce a very large PDF. **Mitigation**: The generation runs asynchronously via management command, so it won't block the admin UI. The command logs progress and handles errors gracefully (same pattern as `create_reports_download_file.py`).
- **PDF generation memory**: WeasyPrint loads the entire HTML/CSS in memory. **Mitigation**: The current approach already handles this for per-company reports; same limits apply. The async command can be run in a controlled environment.
