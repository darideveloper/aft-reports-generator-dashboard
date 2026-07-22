# lead-export Specification

## Purpose
Defines how the Django admin's `LeadAdmin` exposes lead data export actions (CSV and Excel), the shared column schema both formats respect, the file format and styling of the Excel workbook, preservation of the pre-existing CSV output, and the constraint that the Excel export introduces no new runtime dependencies.

## Requirements

### Requirement: Lead Export Actions Surface
The Django admin's `LeadAdmin` SHALL expose two row-selection actions in the same action dropdown, registered together on `actions`: `export_as_csv` (existing behavior) and `export_as_excel` (new). Both actions MUST operate on the queryset of `Lead` rows selected by the administrator; both MUST be reachable from the `Lead` changelist at `/admin/events/lead/`.

The action descriptions displayed in the dropdown MUST be in Spanish, matching project localization conventions:
- `export_as_csv` → `"Exportar registros seleccionados a CSV"` (existing, unchanged).
- `export_as_excel` → `"Exportar registros seleccionados a Excel"`.

#### Scenario: Both export actions are listed in the dropdown
- **WHEN** an administrator opens `/admin/events/lead/` and inspects the action dropdown
- **THEN** the dropdown contains both `Exportar registros seleccionados a CSV` and `Exportar registros seleccionados a Excel`
- **AND** the order of actions matches the order declared on `LeadAdmin.actions`

#### Scenario: Action requires row selection
- **WHEN** the administrator submits the action form without selecting any lead rows
- **THEN** Django's standard admin machinery surfaces the existing "No items selected" message and no file is generated

### Requirement: Shared Column Schema for Lead Exports
Both lead export actions (CSV and Excel) SHALL produce output whose header row contains exactly the following eight columns, in this exact order, in Spanish: `Nombre`, `Email`, `Teléfono`, `Puesto de trabajo`, `Empresa`, `Evento`, `Spam`, `Fecha de Registro`.

The per-row content MUST be derived from each `Lead` instance using the following rules:
- `Nombre` → `lead.name` (empty string when `None`)
- `Email` → `lead.email` (empty string when `None`)
- `Teléfono` → `lead.phone` (empty string when `None`)
- `Puesto de trabajo` → `lead.job_position` (empty string when `None`)
- `Empresa` → `lead.company` (empty string when `None`)
- `Evento` → `lead.event.title`
- `Spam` → `"Sí"` when `lead.is_spam` is truthy, else `"No"`
- `Fecha de Registro` → `lead.created_at` formatted with the pattern `%Y-%m-%d %H:%M:%S`

The CSV and Excel exports MUST remain content-equivalent: the same selected queryset SHALL produce the same header row and the same row strings, differing only by their serial container format (CSV vs. XLSX) and the styled header in Excel.

#### Scenario: CSV header row matches the schema
- **WHEN** the administrator selects one or more leads and runs `Exportar registros seleccionados a CSV`
- **THEN** the first decoded line of the CSV response equals `Nombre,Email,Teléfono,Puesto de trabajo,Empresa,Evento,Spam,Fecha de Registro` (modulo CSV quoting rules for the comma inside `Puesto de trabajo` and `Fecha de Registro`)
- **AND** every subsequent row contains the eight string values for one lead in the defined order

#### Scenario: Excel header row matches the schema
- **WHEN** the administrator selects one or more leads and runs `Exportar registros seleccionados a Excel`
- **THEN** the first row of the first worksheet of the returned `.xlsx` contains the eight Spanish header strings `Nombre`, `Email`, `Teléfono`, `Puesto de trabajo`, `Empresa`, `Evento`, `Spam`, `Fecha de Registro` in the same left-to-right order as the CSV export
- **AND** every subsequent row contains the eight string values for one lead in the order defined by this requirement

#### Scenario: Spam column renders as Spanish strings
- **WHEN** the queryset contains a lead with `is_spam=True` and a lead with `is_spam=False`
- **THEN** the `Spam` column of both the CSV and Excel exports shows `"Sí"` for the spam lead and `"No"` for the non-spam lead, never the literal boolean strings `True`/`False`/`TRUE`/`FALSE`

#### Scenario: Date column renders as the formatted string pattern
- **WHEN** a lead with `created_at = 2026-07-20 14:32:05` is in the queryset
- **THEN** the `Fecha de Registro` column of both exports contains the string `2026-07-20 14:32:05` (not a datetime cell, not an ISO-8601 timezone-suffixed string, not a localized locale-formatted date)

### Requirement: Excel Export File Format and Response
The `export_as_excel` action SHALL return an HTTP response that delivers a valid `.xlsx` workbook generated solely from the selected queryset, with no extra dependencies beyond what is already declared in `requirements.txt`.

The HTTP response MUST satisfy:
- `Content-Type` header equals `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition` header equals `attachment; filename="leads_registro.xlsx"`
- The response body, when parsed by `openpyxl.load_workbook`, MUST yield a workbook with a single worksheet

The single worksheet SHALL be named after `Lead`'s model metadata for `verbose_name_plural` (i.e., `Registros (Leads)`), so the sheet label matches the admin's existing Spanish labeling.

The header row cells SHALL be styled with a bold font (`openpyxl.styles.Font(bold=True)`). No other styling requirements are imposed.

#### Scenario: Excel action returns the Open XML MIME type
- **WHEN** the administrator runs `Exportar registros seleccionados a Excel` on any non-empty selection
- **THEN** the HTTP response `Content-Type` equals `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **AND** the `Content-Disposition` equals `attachment; filename="leads_registro.xlsx"`

#### Scenario: Excel response body is a valid openpyxl workbook
- **WHEN** the administrator runs the Excel action on a selection containing one or more leads
- **THEN** `openpyxl.load_workbook(io.BytesIO(response.content))` succeeds without raising
- **AND** the workbook has exactly one worksheet
- **AND** the worksheet title equals `Registros (Leads)` (the value of `Lead._meta.verbose_name_plural`)

#### Scenario: Excel header row is bold
- **WHEN** the administrator runs the Excel action on any non-empty selection
- **THEN** for each of the eight header cells in row 1 of the worksheet, the cell's `font.bold` attribute is `True`

#### Scenario: Excel action preserves zero-row selection semantics
- **WHEN** the administrator runs the Excel action with an empty queryset
- **THEN** the returned workbook contains only the bold header row and zero data rows
- **AND** the response still carries the correct `Content-Type` and `Content-Disposition` headers

### Requirement: CSV Export Behavior Preservation
The existing `Exportar registros seleccionados a CSV` action SHALL continue to produce byte-identical output to its pre-change behavior, including the `text/csv; charset=utf-8-sig` content type, the same `Content-Disposition` filename `leads_registro.csv`, and the same row serialization order. The change introducing `export_as_excel` MUST NOT alter the CSV output's user-visible bytes.

#### Scenario: CSV output bytes are unchanged before and after this change
- **WHEN** a baseline CSV export is captured on a representative queryset containing a spam and a non-spam lead
- **AND** the same queryset is exported via the CSV action after the Excel action has been added and `actions` updated
- **THEN** the two CSV byte streams are identical
- **AND** the CSV `Content-Type` remains `text/csv; charset=utf-8-sig`
- **AND** the CSV `Content-Disposition` filename remains `leads_registro.csv`

### Requirement: No New Runtime Dependencies
The implementation of `export_as_excel` SHALL only depend on libraries already listed in the project's `requirements.txt`. Specifically, the project's pinned `openpyxl==3.1.5` entry SHALL be the sole Excel library imported; no additional Excel-writing package SHALL be added to `requirements.txt` as part of this change.

#### Scenario: requirements.txt stays unchanged
- **WHEN** the change that adds Excel export lands
- **THEN** `requirements.txt` has no new lines compared to before the change
- **AND** the implementation imports `openpyxl` rather than `xlsxwriter`, `xlwt`, or `pandas`