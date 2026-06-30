## Why

The "6. Ranking nominal" section in group reports uses pre-computed chunks of 16 participants per page, each rendered as a `<section class="page">` with `page-break-before: always`. This design assumes uniform row heights — but with the current auto table layout, column widths are unpredictable. When a participant has a long name ("David Gerson Cárdenas Escobedo") or long job title ("Jefe de Departamento"), text wraps to a second line, doubling the row height. The wrapped rows overflow the page, WeasyPrint spills them to a new page within the same section, and the result is a page with only 3 overflowed rows followed by massive whitespace. The report looks broken and unprofessional.

The root cause: the table has no column width constraints (`table-layout: auto` default) and no font-size or padding reduction on the nominal ranking table specifically. The name and position columns squeeze into whatever space remains, and long names wrap.

## What Changes

- Add a `.nominal-ranking-table` CSS rule block with `table-layout: fixed`, `font-size: 10pt`, and reduced cell padding (`8px 6px`)
- Add a `<colgroup>` element to the nominal ranking table template with explicit percentage-based column widths (Ranking 6%, Nombre 35%, Posición 32%, Índice 8%, Nivel 12%, Semáforo 7%)
- Move `NOMINAL_RANKING_CHUNK_SIZE` to an environment variable (default 18) in `project/settings.py`, read from settings in `utils/group_report_generator.py`
- Fix temp file crash in `survey/management/commands/create_group_report.py`: replace `NamedTemporaryFile` + `File` with `ContentFile` to avoid dependency on a non-existent `/app/media/temp/` directory in production

## Capabilities

### New Capabilities
- `fixed-table-layout`: The nominal ranking table SHALL use `table-layout: fixed` with explicit column widths defined via `<colgroup>` to guarantee predictable column sizing and row heights, independent of cell content length

### Modified Capabilities
- `standardized-pdf-styling`: The nominal ranking table font size is reduced from 11pt to 10pt as a targeted override. This exception is necessary to prevent text wrapping from destabilizing the pre-computed page-chunk pagination. The global 11pt standard remains in effect for all other report text.

## Impact

- **CSS**: `survey/templates/survey/pdf/group_report_style.css` — new `.nominal-ranking-table` rule block (~10 lines) inserted after `.dark-header th`
- **Template**: `survey/templates/survey/pdf/group_report_template.html` — `<colgroup>` added inside the nominal ranking `<table>` (~8 lines)
- **Python (settings)**: `NOMINAL_RANKING_CHUNK_SIZE` added as env var in `project/settings.py` with default 18, read from `django.conf.settings` in `utils/group_report_generator.py`. Default 18 fills the page for single-line rows while allowing prod env override (e.g. `NOMINAL_RANKING_CHUNK_SIZE=20`). At 18, even with several 2-line wraps, 18 rows fit (225mm < 229mm).
- **Python (management command)**: `survey/management/commands/create_group_report.py` — replaced `NamedTemporaryFile` + `File` with `ContentFile` to fix `[Errno 2] No such file or directory` crash when `/app/media/temp/` doesn't exist in production
- **Other sections**: Unaffected. `.ranking-table`, `.area-results-table`, `.heatmap-table`, and all non-table content retain their current styling
- **WeasyPrint**: No changes to the generation pipeline. The existing `page-break-before: always` on `.page` sections continues to govern pagination
