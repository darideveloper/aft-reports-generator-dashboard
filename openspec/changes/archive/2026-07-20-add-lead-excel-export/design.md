## Context

The Django admin's `LeadAdmin` (`events/admin.py:64-125`) currently exposes one `@admin.action` named `export_as_csv` registered in `actions = ["export_as_csv"]`. The action streams a CSV response using `csv.writer` over `HttpResponse`, with the column schema `Nombre, Email, Teléfono, Puesto de trabajo, Empresa, Evento, Spam, Fecha de Registro`. Spam is rendered as the Spanish strings `Sí`/`No`. `created_at` is formatted `%Y-%m-%d %H:%M:%S`.

The marketing team uses these exports in Excel and requests an `.xlsx` action because:
- Direct `.xlsx` files preserve cell types (date, number) instead of treating everything as text-after-CSV-import.
- `.xlsx` avoids Excel's CSV import wizard / UTF-8 BOM detection quirks.
- The same dropdown that produces CSV should produce Excel without changing filters or row selection.

The project already pins `openpyxl==3.1.5` in `requirements.txt` and lists it under "Utilities" in `openspec/project.md` as "Excel file handling" — the dependency is present in the install manifest and anticipated by project docs but is not yet referenced by any application code (`grep import openpyxl` yields no hits). So adopting `openpyxl` is the canonical choice: it carries no new installable footprint, no transitive surprise, and is already documented as the project's Excel toolkit.

The existing CSV action is undocumented in any spec — `openspec/specs/admin-download-ux/spec.md` only covers `target="_blank"` download links, and `openspec/specs/event-forms/spec.md` covers the public form / API / SMTP path but not the admin export actions. This change documents the export-actions surface for the first time under the new `lead-export` capability.

## Goals / Non-Goals

**Goals:**
- Add `export_as_excel` action to `LeadAdmin` that produces a valid `.xlsx` workbook from the selected queryset.
- The Excel file MUST be byte-equivalent in *content* (same headers, same Spanish labels, same date format string) as the CSV output so users switching between the two formats see identical data.
- The action MUST appear alongside `export_as_csv` in the same admin action dropdown — no new menus, no new templates.
- Capture both export actions (CSV and Excel) under a `lead-export` spec with concrete scenarios so future tweaks (e.g., adding a column) have a single contract to update.
- No new runtime dependencies — reuse the already-installed `openpyxl==3.1.5`.

**Non-Goals:**
- No changes to the CSV export's behavior or output bytes. Existing consumers of CSV must be untouched.
- No new public endpoints, no new views, no admin templates, no custom admin pages.
- No multi-sheet export (one sheet only, named after the model verbose name).
- No streaming / chunking for very large querysets. Lead volume is small (one row per registration); a single in-memory workbook is acceptable.
- No internationalization of the headers beyond the current Spanish strings.
- No new columns. The column set is locked to the existing 8 to keep CSV and Excel interchangeable.
- No permission changes. The action relies on the existing `LeadAdmin` change permission, inherit from the action machinery.

## Decisions

### Decision 1: Library — `openpyxl` (Workbook / write_only=False)

**Choice:** Use `openpyxl.Workbook()` (default mode, in-memory) to build the workbook.

**Alternatives considered:**
- *`xlsxwriter`*: excellent writer, slightly better performance on huge datasets, but would add a new dependency. The project has already chosen `openpyxl`; introducing `xlsxwriter` would create two Excel libraries for the same task.
- *`openpyxl` write_only mode*: optimized for large streamed writes. Overkill — lead counts are low and write_only mode disables some cell styling that may be wanted later (e.g., bold header row).
- *`csv` with `.xls` extension and HTML table body (Office 2003 XML)*: a vintage hack that produces "Excel-compatible" but not real `.xlsx` files. Fragile, encoding-sensitive, and misleading to consumers. Rejected.
- *`pandas.to_excel`*: would add `pandas` for a feature that doesn't need it.

**Rationale:** `openpyxl` is already a project dependency (`requirements.txt:39`), already documented in `openspec/project.md:49` as "Excel file handling", and small enough to use trivially for this purpose. Brings zero new install surface.

### Decision 2: Action discovery — single shared column builder

**Choice:** Extract the row-mapping logic (object → ordered Python list of column values) into a small private function on `LeadAdmin`, e.g. `_lead_row(self, obj) -> list[str]`. Both `export_as_csv` and `export_as_excel` use it.

```
LeadAdmin
  ├─ _HEADER_COLUMNS = [Nombre, Email, Teléfono, Puesto de trabajo,
  │                     Empresa, Evento, Spam, Fecha de Registro]
  ├─ _lead_row(obj) -> [name, email, phone, job_position, company,
  │                     event.title, "Sí"|"No", strftime("%Y-%m-%d %H:%M:%S")]
  ├─ export_as_csv  (existing, refactored to use _HEADER_COLUMNS and _lead_row)
  └─ export_as_excel (new)
```

**Why refactor `export_as_csv`:** the current CSV writer hardcodes the column order and Spam string formatting inline. Duplicating those literals in the new Excel action risks them diverging over time (someone updates CSV column label, forgets Excel). The spec mandates identical columns, so the source of truth should be one place.

**Alternative considered:** leave CSV unchanged and copy-paste the literals into the new action. Rejected as maintenance hazard; the spec literally requires parity.

### Decision 3: Date column rendered as a formatted string

**Choice:** Hold `created_at` as a string formatted with `strftime("%Y-%m-%d %H:%M:%S")` in the Excel cell, identical to CSV.

**Alternatives considered:**
- Write a real `datetime` / `cell.value = obj.created_at` and rely on Excel's date formatting. Cleaner spreadsheet semantics (date cells, sortable as dates). However, this would diverge from CSV's string output and break the "byte-equivalent content" goal. Consumers comparing CSV vs. Excel exports should see the same string.

**Non-Goal trade-off:** This means the Excel cell is text, not a date. If future consumers want true date cells, that's a separate change. Documented in `lead-export` spec under "Spam + Date column rendering parity".

### Decision 4: Spam column rendered as `Sí`/`No` strings (not booleans)

**Choice:** Identical to CSV — `obj.is_spam` becomes `"Sí"` or `"No"`. Excel cells holding booleans would render `TRUE`/`FALSE` and would diverge from CSV. Strings it is. Documented in spec.

### Decision 5: HTTP response and filename

**Choice:** Use Django's `HttpResponse` with `content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"` (the official Office Open XML MIME type) and `Content-Disposition: attachment; filename="leads_registro.xlsx"`.

- Filename mirrors the CSV convention (`leads_registro.csv` → `leads_registro.xlsx`) so users see a sibling-style filename in their downloads folder.
- `attachment` (not inline) is required to force a download in browsers; this also matches the CSV action's behavior.

**Alternatives considered:**
- `application/octet-stream`: too generic, loses the office mime for content-type sniffers.
- Generating the workbook bytes via `BytesIO.getvalue()` and constructing `HttpResponse(content, headers=...)`. Chosen — fits Django's idiomatic API.

### Decision 6: Styling — bold header row (optional)

**Choice:** Apply a single `Font(bold=True)` to the header row. No other styling.

**Rationale:** improves usability at near-zero cost (`openpyxl` makes this a one-liner). The CSV file has no styling concept, so this is not a parity concern — headers are *content* parity, not visual parity.

**Alternative considered:** no styling at all (closest parity with CSV). Rejected — Excel users expect a bold header; not bolding harms usability with no upside.

### Decision 7: Sheet name

**Choice:** Use the model's `verbose_name_plural` from `Lead._meta`, i.e., "Registros (Leads)". This matches the admin's existing labeling and respects the project convention of Spanish verbose names.

**Alternative considered:** hardcode `"Leads"`. Rejected — duplicates metadata already defined on the model.

## Risks / Trade-offs

- **Refactoring `export_as_csv` carries a small regression risk.** → Mitigation: extract `_lead_row` and `_HEADER_COLUMNS` as pure additions inside `export_as_csv`'s existing code path; keep the response branch byte-for-byte identical. Cover with an existing-or-new test asserting the CSV output matches today's bytes before the refactor lands.
- **`openpyxl` writes to in-memory buffer.** For pathological lead counts (10k+ rows) the request times out / OOMs. → Acceptable given current volumes; if volume grows, switch to `write_only=True` mode as a follow-up (not this change).
- **Filename collisions on browser download.** If two exports land in the same folder the second overwrites the first. → Mirrors existing CSV behavior; out of scope.
- **MIME type acceptance in some proxies.** Unlikely for an admin-only endpoint behind session auth, but worth noting: the long MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` is the only correct one.
- **Tests will need to read an `.xlsx` to assert cell values.** Tests must `import openpyxl` and call `openpyxl.load_workbook(BytesIO(response.content))` — a testing-time dependency on `openpyxl`. Already installed, so no new test dependency.

## Migration Plan

1. Add the new `_HEADER_COLUMNS` constant and `_lead_row` helper to `LeadAdmin` (pure refactor; existing CSV action uses them).
2. Add `export_as_excel` method decorated with `@admin.action(description="Exportar registros seleccionados a Excel")`.
3. Register it: `actions = ["export_as_csv", "export_as_excel"]`.
4. Add tests to `events/tests.py` (see tasks for full coverage list).
5. Run `python manage.py test events` to confirm green.
6. Deploy: no migrations, no env changes, no infra changes. Pure code change.
7. Rollback: revert the single `events/admin.py` commit. The CSV action is unchanged in user-visible behavior.