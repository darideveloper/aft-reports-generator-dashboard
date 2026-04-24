# Tasks: Make Report Title Dynamic

- [x] **Research**
    - [x] Confirm exact positioning of "Alfabetización Tecnológica" in generated reports by running a test generation. <!-- id: 0 -->
- [x] **Configuration**
    - [x] Add `PDF_REPORT_TITLE` and `PDF_REPORT_ACRONYM` to `project/settings.py` with default values. <!-- id: 1 -->
    - [x] Add example values to `.env` (or a sample env file). <!-- id: 2 -->
- [x] **Implementation**
    - [x] Update `utils/pdf_generator.py` to use `settings.PDF_REPORT_ACRONYM` in the footer. <!-- id: 3 -->
    - [x] Add logic to `utils/pdf_generator.py` to draw `settings.PDF_REPORT_TITLE` as a title on the first page. <!-- id: 4 -->
- [x] **Verification**
    - [x] Run `python manage.py generate_next_report` and verify the output PDF contains the dynamic title. <!-- id: 5 -->
    - [x] Verify footer text is correctly centered with different acronym lengths. <!-- id: 6 -->
