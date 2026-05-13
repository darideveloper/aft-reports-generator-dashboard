## 1. Setup and Preparation

- [x] 1.1 Create the new template directory `survey/templates/survey/pdf/` and its `assets/` subdirectory.
- [x] 1.2 Copy existing assets (images, CSS) from `survey/pdf_templates/html-pdf/` to the new location.

## 2. Template Conversion

- [x] 2.1 Copy `survey/pdf_templates/html-pdf/index.html` to `survey/templates/survey/pdf/report_template.html`.
- [x] 2.2 Replace static company name with `{{ company_name }}` in the cover page and footers.
- [x] 2.3 Replace static participant count with `{{ total_participants }}`.
- [x] 2.4 Replace static date with `{{ report_date }}`.
- [x] 2.5 Audit `report_template.html` and `style.css` to ensure all asset paths are relative and correctly resolved via WeasyPrint `base_url`.

## 3. View Refactoring

- [x] 3.1 Update `preview_report_pdf` in `survey/views.py` to use `render_to_string()` with a dummy context dictionary.
- [x] 3.2 Configure `base_url` in the view to point to the new `survey/templates/survey/pdf/` directory.

## 4. Verification

- [x] 4.1 Access `/preview-report-pdf/` and verify the PDF renders with dynamic data ("Acme Corp", etc.).
- [x] 4.2 Confirm all images and styles are correctly applied in the generated PDF.
