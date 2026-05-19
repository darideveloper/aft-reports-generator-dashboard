## 1. CSS Variable Definitions

- [x] 1.1 Define `--page-size`, `--font-size-normal`, and `--font-size-heading` variables in `survey/templates/survey/group_report.css`.
- [x] 1.2 Define `--page-size`, `--font-size-normal`, and `--font-size-heading` variables in `survey/templates/survey/pdf/style.css`.

## 2. Standardize Group Report Styles

- [x] 2.1 Update `@page { size: ... }` to use `--page-size` (Letter) in `survey/templates/survey/group_report.css`.
- [x] 2.2 Update body text font-size to use `--font-size-normal` (11pt) in `survey/templates/survey/group_report.css`.
- [x] 2.3 Update heading tags (h1-h6) and header classes to use `--font-size-heading` (12pt) and bold weight in `survey/templates/survey/group_report.css`.
- [x] 2.4 Update sub-headings (A., B., etc. using h4) to use `--font-size-sub-heading` (11pt) and bold weight in `survey/templates/survey/group_report.css`.

## 3. Standardize Individual Report Styles (WeasyPrint)

- [x] 3.1 Update `@page { size: ... }` to use `--page-size` (Letter) in `survey/templates/survey/pdf/style.css`.
- [x] 3.2 Update body text font-size to use `--font-size-normal` (11pt) in `survey/templates/survey/pdf/style.css`.
- [x] 3.3 Update heading tags (h1-h6), `.report-title`, `.section-title`, and `.subset-title` to use `--font-size-heading` (12pt) and bold weight in `survey/templates/survey/pdf/style.css`.
- [x] 3.4 Update sub-headings (A., B., etc. using h4 or `.subset-title`) to use `--font-size-sub-heading` (11pt) and bold weight in `survey/templates/survey/pdf/style.css`.
- [x] 3.5 Audit `survey/templates/survey/pdf/report_template.html` and remove/update any inline styles that conflict with the new font size standards.


## 4. Verification

- [x] 4.1 Use the `/preview-pdf/` endpoint to visually verify the group report layout with Letter size and updated font sizes.
- [x] 4.2 Use the live preview for the organizational report to verify its layout and styling.
