## Why

The current PDF report generation uses a static HTML file (`survey/pdf_templates/html-pdf/index.html`) which is read as a raw string. This makes it difficult to inject dynamic data from the database and leverage Django's template engine for logic, loops, and conditional formatting. Converting this HTML/CSS bundle into a proper Django template will enable fully dynamic report generation.

## What Changes

- **Template Relocation**: Move the HTML and CSS assets from `survey/pdf_templates/html-pdf/` to the standard Django templates directory at `survey/templates/survey/pdf/`.
- **Template Conversion**: Transform `index.html` into a Django template (`report_template.html`) by replacing static text with template variables (`{{ ... }}`) and using template tags (`{% ... %}`) for logic.
- **Asset Handling**: Update the template to correctly reference CSS and images so they are accessible to WeasyPrint during PDF generation, likely using `base_url` or absolute paths.
- **View Refactoring**: Update `preview_report_pdf` in `survey/views.py` to use `render_to_string()` with a context object instead of reading the file manually.

## Capabilities

### New Capabilities
- `dynamic-pdf-report`: A Django-based template system for the organizational report that supports dynamic data injection for participants, scores, and company information.

### Modified Capabilities
- None

## Impact

- **survey/views.py**: The `preview_report_pdf` view will be updated to render the template with context.
- **Template Files**: New files in `survey/templates/survey/pdf/`.
- **Existing Logic**: This change replaces the static file reading logic with standard Django rendering, which is more robust and maintainable.
