## Context

The Django admin interface for `Report`, `ReportsDownload`, and `GroupReport` models includes custom columns that render action buttons for downloading or viewing generated documents. 

1. **`GroupReportAdmin`**: The "Descargar PDF" button currently uses a relative path `download/` which resolves to `/admin/survey/groupreport/download/` in the list view, but the registered URL pattern expects an ID: `/admin/survey/groupreport/<pk>/download/`.
2. **Standardization**: All download/view buttons in the admin currently open in the same tab, which is a suboptimal user experience for administrators who need to remain on the management page while inspecting documents.

## Goals / Non-Goals

**Goals:**
- Fix the broken link in `GroupReportAdmin` list view.
- Ensure all admin-side file download/view buttons open in a new browser tab.
- Maintain consistency across all three admin models (`Report`, `ReportsDownload`, `GroupReport`).

**Non-Goals:**
- Changes to the PDF or ZIP generation logic.
- Changes to the underlying models or database schema.

## Decisions

### 1. Link Generation in `GroupReportAdmin`
- **Decision**: Update `custom_links` to use `f"{obj.pk}/download/"`.
- **Rationale**: This ensures the link correctly includes the record's primary key, matching the custom URL pattern defined in `get_urls`.

### 2. Standardize `target="_blank"` for Admin Links
- **Decision**: Add `target="_blank"` to the `<a>` tags in `ReportAdmin.custom_links`, `ReportsDownloadAdmin.custom_links`, and `GroupReportAdmin.custom_links`.
- **Rationale**: This fulfills the requirement to open downloads in new tabs, preventing navigation away from the admin list views.

### 3. Maintain Status-Based Styling
- **Decision**: Keep the existing conditional logic that sets buttons to `btn-primary` when completed and `btn-secondary disabled` when pending/error.
- **Rationale**: This provides clear visual feedback to the admin about which documents are ready for viewing.

## Risks / Trade-offs

- **Risk**: Some browsers might block multiple popups/new tabs if triggered too quickly, but since these are individual manual clicks, the risk is negligible.
- **Trade-off**: `target="_blank"` can sometimes lead to many open tabs if the user doesn't close them, but this is the standard expectation for "download/view" buttons in administrative dashboards.
