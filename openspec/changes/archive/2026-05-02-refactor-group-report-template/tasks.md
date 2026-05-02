## 1. Implementation
- [x] 1.1 Create `survey/templates/survey/group_report.css` and move the CSS from `pdf_sample.html` into it.
- [x] 1.2 Rename `survey/templates/survey/pdf_sample.html` to `survey/templates/survey/group_report.html`.
- [x] 1.3 Update `group_report.html` to use `{% include "survey/group_report.css" %}`.
- [x] 1.4 Update the `generate_next_report_group` management command to reference `survey/group_report.html`.
- [x] 1.5 Update the `preview_pdf_sample` view in `survey/views.py` to reference `survey/group_report.html`.
- [x] 1.6 Verify the PDF generation via the management command and the browser preview.