# Change: Add sample WeasyPrint PDF generator

## Why
The project needs to generate PDFs with advanced CSS features (like headers and footers using running elements) and dynamic tables spanning multiple pages. WeasyPrint is an excellent library that allows rendering PDFs from HTML+CSS and supports these advanced Paged Media features natively. Currently, the project uses ReportLab and Playwright for PDF generation, but this change introduces a robust sample leveraging WeasyPrint for easier HTML-to-PDF templating.

## What Changes
- Add `WeasyPrint==63.1` to `requirements.txt`.
- Add a new Django management command `generate_next_report_group` at `survey/management/commands/` to demonstrate the PDF generation with support for dynamic colors and logos.
- Create a professional HTML template in the `survey` app with an advanced CSS block that utilizes `@page` rules, `position: running()`, and rich styling (colors, pills, cover page).
- The sample template will include a cover page, repeating header/footer, dynamic table with random data, colored status pills, and proper `thead` repeating behavior.

## Impact
- Affected specs: `pdf-generation`
- Affected code: `requirements.txt`, new template file, new utility/command file.