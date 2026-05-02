# Change: Implement final group report template structure

## Why
The group report generation has moved beyond the "sample" stage and is now being established as the final production-ready structure. Separating the HTML and CSS into distinct files is essential for maintainability. Renaming the files from `pdf_sample.html` to `group_report.html` (and creating `group_report.css`) accurately reflects the template's role as the definitive group report structure for the project.

## What Changes
- Rename `survey/templates/survey/pdf_sample.html` to `survey/templates/survey/group_report.html`.
- Extract CSS from the HTML template into a new file `survey/templates/survey/group_report.css`.
- Use the Django `{% include %}` tag in the HTML template to import the CSS file.
- Update the management command `generate_next_report_group` to use the final template name.
- Update the `preview_pdf_sample` view in `survey/views.py` to use the final template name.

## Impact
- Affected specs: `pdf-generation`
- Affected code: `survey/templates/`, `survey/views.py`, `survey/management/commands/generate_next_report_group.py`