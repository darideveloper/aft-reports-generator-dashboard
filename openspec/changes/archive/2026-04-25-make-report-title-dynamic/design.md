# Design: Dynamic Report Title

## Context
The PDF reports use a static template and some hardcoded strings. The user wants to change "Alfabetización Tecnológica" to be dynamic. This string is likely the full name of what is abbreviated as "AFT" in the code.

## Architecture
We will introduce two new settings:
- `PDF_REPORT_TITLE`: The full title (e.g., "Alfabetización Tecnológica").
- `PDF_REPORT_ACRONYM`: The short version used in footers (e.g., "AFT").

These will be loaded from the `.env` file via `project/settings.py`.

### PDF Modification
In `utils/pdf_generator.py`:
1.  Import `settings` from `django.conf`.
2.  In `footer_setting`, replace `f"Reporte AFT de {name}"` with `f"Reporte {settings.PDF_REPORT_ACRONYM} de {name}"`.
3.  We will also add a step to draw the `PDF_REPORT_TITLE` on the first page of the PDF. Since the first page currently draws:
    ```python
    c.setFont("arialbd", 22)
    c.drawRightString(width - 70, 300, name)
    c.drawRightString(width - 70, 270, date)
    ```
    We will investigate if we should add `c.drawCentredString(width / 2, y, settings.PDF_REPORT_TITLE)` or similar.

## Layout Considerations
- Footer text centering logic needs to be robust to varying acronym lengths.
- If the title is drawn on page 1, we must avoid overlapping with the logo (drawn at `y=115`) and the applicant info (at `y=300`).

## Environment Variables
```env
PDF_REPORT_TITLE=Alfabetización Tecnológica
PDF_REPORT_ACRONYM=AFT
```
