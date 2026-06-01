## Why

The `GroupReport` download link in the admin list view is currently broken because it uses a relative URL (`download/`) that lacks the required primary key (`pk`), causing 404 errors. Additionally, existing download links for individual reports and batch downloads open in the same tab, which disrupts the administrator's workflow by navigating them away from the management interface.

## What Changes

- **Fix GroupReport Download Link**: Update the `GroupReport` admin list view to generate download links that include the record's primary key (e.g., `{pk}/download/`).
- **Standardize Download Behavior**: Update all download links in the Django admin (including individual reports, batch report downloads, and group reports) to open in a new browser tab (`target="_blank"`) for a seamless user experience.

## Capabilities

### New Capabilities
- `admin-download-ux`: Defines the requirement for all admin-side document download links to be functional and open in new tabs.

### Modified Capabilities
- `group-report-generation`: Update the generation interface to ensure accessibility of the result.
- `batch-report-downloads`: Update the results list to open downloads in new tabs.

## Impact

- **Affected Files**: `survey/admin.py`.
- **User Interface**: Django Admin (`GroupReport`, `Report`, `ReportsDownload` list views).
- **APIs**: No changes to backend APIs, only UI/Link generation logic.
