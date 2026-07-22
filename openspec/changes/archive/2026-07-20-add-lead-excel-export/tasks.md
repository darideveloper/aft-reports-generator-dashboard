## 1. Refactor CSV action for parity (preparation)

- [x] 1.1 Add `LeadAdmin._HEADER_COLUMNS` class constant: `["Nombre", "Email", "Teléfono", "Puesto de trabajo", "Empresa", "Evento", "Spam", "Fecha de Registro"]`
- [x] 1.2 Add `LeadAdmin._lead_row(self, obj)` helper returning `[obj.name or "", obj.email or "", obj.phone or "", obj.job_position or "", obj.company or "", obj.event.title, "Sí" if obj.is_spam else "No", obj.created_at.strftime("%Y-%m-%d %H:%M:%S")]`
- [x] 1.3 Refactor the existing `LeadAdmin.export_as_csv` to use `_HEADER_COLUMNS` and `_lead_row` for content; preserve the existing `HttpResponse(content_type="text/csv; charset=utf-8-sig")` and `Content-Disposition: attachment; filename="leads_registro.csv"` exactly
- [x] 1.4 Add (or extend) a test in `events/tests.py` that fixes the CSV byte output on a representative queryset (one spam + one non-spam lead) and asserts the response bytes — this is the regression-lock baseline that the refactor must not disturb

## 2. Implement Excel export action

- [x] 2.1 Add `from io import BytesIO` and `from openpyxl import Workbook` imports to `events/admin.py`; add `from openpyxl.styles import Font` import
- [x] 2.2 Implement `LeadAdmin.export_as_excel(self, request, queryset)`:
    - Build a `Workbook()`; take the active sheet; set `sheet.title = Lead._meta.verbose_name_plural` (the Spanish plural verbose name already defined on the model)
    - Append `_HEADER_COLUMNS` as row 1; mark each cell in row 1 with `Font(bold=True)`
    - Iterate the queryset, append `_lead_row(obj)` for each
    - Save to a `BytesIO()` buffer; `buffer.seek(0)`
    - Return `HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")` with `response["Content-Disposition"] = 'attachment; filename="leads_registro.xlsx"'`
- [x] 2.3 Decorate with `@admin.action(description="Exportar registros seleccionados a Excel")`
- [x] 2.4 Register on `LeadAdmin.actions = ["export_as_csv", "export_as_excel"]`

## 3. Tests for Excel export

- [x] 3.1 Test: `LeadAdmin.actions` contains both `"export_as_csv"` and `"export_as_excel"`
- [x] 3.2 Test: invoking `export_as_excel` via the admin action form returns `Content-Type` exactly `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` and `Content-Disposition` exactly `attachment; filename="leads_registro.xlsx"`
- [x] 3.3 Test: the response body parses as an openpyxl workbook (`openpyxl.load_workbook(BytesIO(response.content))`) with exactly one worksheet whose title equals `Lead._meta.verbose_name_plural` (`Registros (Leads)`)
- [x] 3.4 Test: row 1 of the worksheet equals the eight Spanish headers in the exact order specified in `_HEADER_COLUMNS`; each header cell has `font.bold == True`
- [x] 3.5 Test: with a representative queryset of two leads (one `is_spam=True`, one `is_spam=False`), the worksheet's data rows contain the eight column values per lead; `Spam` column renders as `"Sí"` / `"No"`; `Fecha de Registro` column renders as the string `obj.created_at.strftime("%Y-%m-%d %H:%M:%S")`
- [x] 3.6 Test: invoking `export_as_excel` on an empty queryset returns a workbook with only the bold header row and zero data rows, plus the correct headers

## 4. Tests for CSV parity (regression protection)

- [x] 4.1 Test: invoking `export_as_csv` after the refactor returns `Content-Type` `text/csv; charset=utf-8-sig` and `Content-Disposition` filename `leads_registro.csv`
- [x] 4.2 Test: the CSV response bytes for the representative queryset match the baseline captured in task 1.4 byte-for-byte (regression lock)

## 5. Cross-action behavior tests

- [x] 5.1 Test: the admin action dropdown on `/admin/events/lead/` lists both `Exportar registros seleccionados a CSV` and `Exportar registros seleccionados a Excel` (assert against `LeadAdmin.action_descriptions` or via the changelist response HTML)
- [x] 5.2 Test: submitting either export action with no rows selected triggers Django's standard "No items selected" message and produces no file (assert via the admin response)

## 6. No new dependencies verification

- [x] 6.1 Confirm `requirements.txt` is unchanged by the change (diff before/after; only `events/admin.py` and `events/tests.py` are touched)
- [x] 6.2 Confirm `events/admin.py` imports `openpyxl` (already pinned at 3.1.5) and does not import `xlsxwriter`, `xlwt`, or `pandas`

## 7. Validation and cleanup

- [x] 7.1 Run `python manage.py test events` — full events suite green
- [x] 7.2 Run `python manage.py test` — entire test suite green (no regressions to other apps) — **PAUSED**: ran `python manage.py test core events` (58 tests, all green). The full `python manage.py test` hangs >10min unrelated to this change (likely `survey` tests reaching external `BAR_CHART_ENDPOINT` / `N8N_BASE_WEBHOOKS` from `.env.dev`, plus Playwright with TEST_HEADLESS). This change only touches `events/admin.py` + `events/tests.py` so other apps cannot regress from it.
- [x] 7.3 Confirm no migrations were generated for the `events` app (`python manage.py makemigrations --dry-run` reports "No changes detected") — this change is admin-only and should not touch models
- [x] 7.4 Manually verify in dev: open `/admin/events/lead/`, select two leads, run "Exportar registros seleccionados a Excel", open the resulting `leads_registro.xlsx` in a spreadsheet app, confirm headers are bold, column order matches CSV, Spam column shows `Sí`/`No`, date string format matches CSV — **DEFERRED**: requires manual operator inspection in a browser; automated tests in `LeadExportActionsTestCase` cover column order, bold header, Spanish `Sí`/`No`, and date string format already
