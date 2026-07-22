## Why

Leads captured through event registration forms can be exported from the Django admin today, but only as CSV. Spreadsheet-native output (`.xlsx`) is a frequent request from the marketing team because Excel preserves column types (e.g., dates render as real dates, not strings), avoids Excel's CSV-import encoding hiccups, and opens directly without an import wizard. Today users must rename or re-save the CSV inside Excel; an `.xlsx` action in the same dropdown removes that step.

## What Changes

- Add a second admin action `export_as_excel` to `events.admin.LeadAdmin`, surfaced in the same action dropdown as the existing `export_as_csv`.
- The Excel file MUST use the identical column set and order as the CSV export: `Nombre, Email, Teléfono, Puesto de trabajo, Empresa, Evento, Spam, Fecha de Registro`.
- Spanish boolean rendering (`Sí`/`No`) for the `Spam` column MUST be preserved, matching the CSV behavior, so downstream consumers see consistent text across both formats.
- The export MUST be served with a sensible filename and the proper SPDX/Office Open XML MIME type so browsers trigger a download rather than rendering inline.
- No changes to the existing CSV action; no DB schema changes; no new endpoints.

## Capabilities

### New Capabilities
- `lead-export`: Admin-side capabilities for exporting `Lead` rows from the Django admin, covering both CSV (existing behavior to be captured) and XLSX (new) outputs with a shared column schema.

### Modified Capabilities
<!-- None — the CSV export is currently undocumented in any spec; capturing both formats under the new `lead-export` capability avoids retroactively modifying another capability. -->

## Impact

- **Code**: `events/admin.py` — add `export_as_excel` action method, register it on `LeadAdmin.actions`.
- **Dependencies**: A new runtime dependency is required. Two candidate libraries (see `design.md`): `openpyxl` (purpose-built, lightweight, recommended) or `xlsxwriter`. Either must be added to the project's dependency manifest (`requirements.txt` or equivalent, matching the project's existing install convention).
- **Tests**: New tests in `events/tests.py` covering: action presence on `LeadAdmin.actions`, header row column order, cell values for a representative lead, spam boolean rendering, and the response `Content-Type`/disposition headers. Existing CSV tests (if any) must remain green.
- **Admin UX**: Two distinct actions appear in the dropdown — `Exportar registros seleccionados a CSV` and the new `Exportar registros seleccionados a Excel`. Selecting rows before invoking the action is supported, identical to the CSV flow.
- **No impact** on the public form, `LeadSubmitView`, models, migrations, or email dispatch path.