## 1. Implementation
- [x] 1.1 Add `WeasyPrint` to `requirements.txt`
- [x] 1.2 Create HTML/CSS template for the PDF in the `survey` app (using running elements and page counters)
- [x] 1.3 Create a Django management command `generate_next_report_group` at `survey/management/commands/` to populate the template with random data and render it using WeasyPrint
- [x] 1.4 Test the PDF generation command locally