## Why

The current PDF generation in the project is inconsistent regarding page sizes and font styling across WeasyPrint-based reports. Some reports use A4 while others might use different sizes. Additionally, font sizes are not standardized to the client's preference of 11pt for normal text and 12pt bold for headings. Standardizing these ensures a professional and uniform appearance for all modern HTML-based reports.

## What Changes

- Change PDF page size to **Letter** (8.5" x 11") for all WeasyPrint-based reports.
- Standardize normal font size to **11pt**.
- Standardize heading font size to **12pt bold**.
- Update WeasyPrint CSS files (`survey/templates/survey/group_report.css` and `survey/templates/survey/pdf/style.css`) to reflect these changes.

## Capabilities

### New Capabilities
- `standardized-pdf-styling`: Capability to generate WeasyPrint PDFs with a consistent Letter page size and uniform font sizes (11pt normal, 12pt bold headings).

### Modified Capabilities
- `pdf-generation`: Requirements for page size and font styling in WeasyPrint templates are being updated.

## Impact

- `survey/templates/survey/group_report.css`: Update `@page` size to `Letter` and font sizes.
- `survey/templates/survey/pdf/style.css`: Ensure `font-size` is 11pt and headings are 12pt bold.
- WeasyPrint report layouts might need minor adjustments due to the change in page size or font dimensions.
