## 1. Python: Env Var for Chunk Size

- [x] 1.1 Add `NOMINAL_RANKING_CHUNK_SIZE = int(os.getenv("NOMINAL_RANKING_CHUNK_SIZE", 18))` to `project/settings.py`
- [x] 1.2 Change `NOMINAL_RANKING_CHUNK_SIZE = 15` to `settings.NOMINAL_RANKING_CHUNK_SIZE` in `utils/group_report_generator.py`

## 2. CSS Changes

- [x] 2.1 Add `.nominal-ranking-table { table-layout: fixed; font-size: 10pt; }` rule block to `survey/templates/survey/pdf/group_report_style.css` after the `.dark-header th` block (after line 342)
- [x] 2.2 Add `.nominal-ranking-table th, .nominal-ranking-table td { padding: 8px 6px; }` rule to the same block

## 3. Template Changes

- [x] 3.1 Add `<colgroup>` element inside the nominal ranking `<table>` in `survey/templates/survey/pdf/group_report_template.html` (after line 339, before `<thead>`)
- [x] 3.2 Define columns: `<col style="width: 6%">` (Ranking), `<col style="width: 35%">` (Nombre), `<col style="width: 32%">` (Posición), `<col style="width: 8%">` (Índice), `<col style="width: 12%">` (Nivel), `<col style="width: 7%">` (Semáforo)

## 4. Fix Temp File Crash in Management Command

- [x] 4.1 Remove `import os`, `import tempfile`, and `from django.core.files.base import File`
- [x] 4.2 Add `from django.core.files.base import ContentFile`
- [x] 4.3 Replace `NamedTemporaryFile` + `open` + `save` with `ContentFile` + `save`
- [x] 4.4 Remove unused `from django.conf import settings` (no longer referenced)

## 5. Verification

- [x] 5.1 Generate a group report PDF in prod — verify no `[Errno 2]` crash
- [x] 5.2 Verify the nominal ranking table has fixed column widths and correct spacing
- [x] 5.3 Adjust `NOMINAL_RANKING_CHUNK_SIZE` env var in prod if needed
